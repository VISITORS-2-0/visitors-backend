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

    def init_entities(self) -> None:
        """
        Takes all XML files from tak_entities_dir, converts them to dicts 
        using xmltodict, creates TAKEntity objects, and populates the data structure.
        """
        self.tak_by_name = {}
        self.tak_name_by_id = {}
        
        if not os.path.exists(self.tak_entities_dir):
            raise FileNotFoundError(f"Directory not found: {self.tak_entities_dir}")

        for filename in os.listdir(self.tak_entities_dir):
            if not filename.endswith('.xml'):
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
                
                model_class = self._MODEL_MAP.get(root_tag)
                
                if model_class:
                    tak_obj = model_class(**root_data)
                    
                    self.tak_by_name[tak_name] = tak_obj
                    self.tak_name_by_id[tak_id] = tak_name
                else:
                    raise ValueError(f"Unknown tag '{root_tag}' in file {filename}")
                
            except Exception as e:
                raise ValueError(f"Error processing {filename}: {str(e)}")

        derivied_into_dict = defaultdict(list)

        for tak_name, tak_obj in self.tak_by_name.items():

            if isinstance(tak_obj, AbstractConcept):
                derived_from_names = []

                for derived_from_id in tak_obj.derived_from:
                    derivied_into_dict[self.tak_name_by_id[derived_from_id]].append(tak_obj.name)
                    derived_from_names.append(self.tak_name_by_id[derived_from_id])

                tak_obj.derived_from = derived_from_names

        for tak_name, tak_obj in self.tak_by_name.items():
            if isinstance(tak_obj, AbstractConcept):
                tak_obj.derived_into = derivied_into_dict.get(tak_obj.name, [])
                tak_obj.siblings = list({sibling for parent in tak_obj.derived_from for sibling in derivied_into_dict.get(parent, []) if sibling != tak_name})

    def get_entity_by_name(self, tak_name: str) -> TAKEntity:
        return self.tak_by_name.get(tak_name)

    def get_entity_by_id(self, tak_id: str) -> TAKEntity:
        tak_name = self.tak_name_by_id.get(tak_id)
        return self.tak_by_name.get(tak_name)

    def get_all_entities(self) -> Dict[str, TAKEntity]:
        return self.tak_by_name

from app.core.config import settings
concept_manager_instance = ConceptManager(settings.TAK_FILES_DIR)
