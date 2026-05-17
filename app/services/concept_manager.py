from collections import defaultdict
import os
import xmltodict
from typing import Dict, Any, List
from app.models.concept import (
    TAKEntity, Event, Context, 
    NumericRawConcept, NominalRawConcept, 
    State, Trend, Pattern, AbstractConcept
)

class ConceptManager:
    # Map the root XML tags to their corresponding Pydantic models
    _MODEL_MAP = {
        "event": Event,
        "context": Context,
        "numeric-raw-concept": NumericRawConcept,
        "nominal-raw-concept": NominalRawConcept,
        "state": State,
        "trend": Trend,
        "pattern": Pattern
    }

    def __init__(self, tak_entities_dir: str):
        self.tak_entities_dir = tak_entities_dir
        
        self.tak_by_name: Dict[str, TAKEntity] = {}
        self.tak_name_by_id: Dict[str, str] = {}
        self.raw_xml_by_name: Dict[str, Dict[str, Any]] = {}

    def init_entities(self) -> None:
        """
        Takes all XML files from tak_entities_dir, converts them to dicts 
        using xmltodict, creates TAKEntity objects, and populates the data structure.
        """
        self.tak_by_name = {}
        self.tak_name_by_id = {}
        self.raw_xml_by_name = {}
        
        if not os.path.exists(self.tak_entities_dir):
            raise FileNotFoundError(f"Directory not found: {self.tak_entities_dir}")

        parsed_files = []
        for filename in os.listdir(self.tak_entities_dir):
            if not filename.lower().endswith('.xml'):
                continue
                
            file_path = os.path.join(self.tak_entities_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    xml_content = file.read()
                    
                xml_dict = xmltodict.parse(xml_content)
                
                root_tag = list(xml_dict.keys())[0]
                root_data = xml_dict[root_tag]
                
                tak_name = root_data.get('@name')
                tak_id = root_data.get('@id')

                if tak_name is None:
                    raise ValueError(f"Missing '@name' attribute in {filename}")
                
                if tak_id is None:
                    raise ValueError(f"Missing '@id' attribute in {filename}")
                
                self.raw_xml_by_name[tak_name] = root_data
                parsed_files.append((filename, root_tag, root_data, tak_name, tak_id))
                
            except Exception as e:
                raise ValueError(f"Error processing {filename}: {str(e)}")

        # Split into non-patterns and patterns
        non_patterns = [p for p in parsed_files if p[1] != 'pattern']
        patterns = [p for p in parsed_files if p[1] == 'pattern']

        # Process all files in correct order
        for file_list in [non_patterns, patterns]:
            for filename, root_tag, root_data, tak_name, tak_id in file_list:
                try:
                    model_class = self._MODEL_MAP.get(root_tag)
                    
                    if model_class:
                        tak_obj = model_class(**root_data)
                        
                        self.tak_by_name[tak_name] = tak_obj
                        self.tak_name_by_id[tak_id] = tak_name
                    else:
                        raise ValueError(f"Unknown tag '{root_tag}' in file {filename}")
                except Exception as e:
                    print(f"Error instantiating {filename}: {str(e)}")


        # Map each conceptual component to its parents (abstracted-into)
        derived_into_dict = defaultdict(list)
        for tak_name, tak_obj in self.tak_by_name.items():
            if tak_obj.derived_from:
                derived_from_names = []
                for derived_from_id in tak_obj.derived_from:
                    parent_name = tak_obj.name
                    child_name = self.tak_name_by_id.get(derived_from_id)
                    if child_name:
                        derived_into_dict[child_name].append(parent_name)
                        derived_from_names.append(child_name)
                tak_obj.derived_from = derived_from_names

        # Parse context graphs
        contexts_by_inducer = defaultdict(list)
        inducers_by_context = defaultdict(list)
        
        for name, root_data in self.raw_xml_by_name.items():
            if root_data.get('@concept-type') == 'context':
                context_id = root_data.get('@id')
                inducers_element = root_data.get('inducer-entities', {})
                if inducers_element:
                    inducers = inducers_element.get('inducer-entity', [])
                    if isinstance(inducers, dict):
                        inducers = [inducers]
                    for ind in inducers:
                        ind_id = ind.get('@id')
                        ind_name = self.tak_name_by_id.get(ind_id)
                        if ind_name:
                            contexts_by_inducer[ind_name].append(name)
                            inducers_by_context[name].append(ind_name)

        # Assign final relations to entities
        for tak_name, tak_obj in self.tak_by_name.items():
            # "meta-parents": relation such as abstracted-into
            tak_obj.derived_into = derived_into_dict.get(tak_name, [])
            
            # "meta-siblings": relation such as other components on the pattern into which the current entity is abstracted
            # Therefore siblings are other concepts sharing the same meta-parents
            siblings_set = set()
            for parent_name in tak_obj.derived_into:
                parent_obj = self.tak_by_name.get(parent_name)
                if parent_obj:
                    for sibling in parent_obj.derived_from:
                        if sibling != tak_name:
                            siblings_set.add(sibling)
            tak_obj.siblings = list(siblings_set)
            
            # "context relation": generated-context relation or generated-from relation for contexts themselves
            if tak_obj.concept_type == 'context':
                tak_obj.context = list(set(inducers_by_context.get(tak_name, [])))
            else:
                tak_obj.context = list(set(contexts_by_inducer.get(tak_name, [])))

            # "mapping_abstractions": parse mapping functions using resolved names
            raw_data = self.raw_xml_by_name.get(tak_name)
            if raw_data:
                from app.models.concept import parse_mapping_abstractions
                
                def id_to_name(c_id):
                    return self.tak_name_by_id.get(str(c_id), str(c_id))
                    
                abstractions = parse_mapping_abstractions(raw_data, id_to_name)
                if abstractions:
                    tak_obj.mapping_abstractions = abstractions

    def get_entity_by_name(self, tak_name: str) -> TAKEntity:
        return self.tak_by_name.get(tak_name)

    def get_entity_by_id(self, tak_id: str) -> TAKEntity:
        tak_name = self.tak_name_by_id.get(tak_id)
        return self.tak_by_name.get(tak_name)

    def get_all_entities(self) -> Dict[str, TAKEntity]:
        return self.tak_by_name

    def get_raw_xml_by_name(self, tak_name: str) -> Dict[str, Any]:
        return self.raw_xml_by_name.get(tak_name)

from app.core.config import settings
concept_manager_instance = ConceptManager(settings.TAK_FILES_DIR)
