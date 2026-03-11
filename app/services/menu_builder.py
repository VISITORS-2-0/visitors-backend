import os
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def _init_navigation_structure() -> Dict[str, Any]:
    return {
        "TakEntity": {
            "Event": [],
            "Context": [],
            "Concept": {
                "RawConcept": [],      # Contains all raw-numeric, raw-nominal, etc.
                "AbstractConcept": []  # Contains all state, gradient, pattern, etc.
            }
        }
    }

_navigation_structure = _init_navigation_structure()
_is_built = False

def process_file(file_path: str, filename: str) -> None:
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract attributes
        name = root.attrib.get('name', filename)
        concept_type = root.attrib.get('concept-type')
        entity_id = root.attrib.get('id')
        description = root.attrib.get('description')
        
        if not concept_type:
            logger.warning(f"Skipping {filename}: No 'concept-type' attribute found.")
            return

        # Create the entity object
        entity_data = {
            "name": name,
            "type": concept_type,
            "id": entity_id
        }
        
        # Omit description if not present to match typical JSON formatting behavior
        if description is not None:
            entity_data["description"] = description

        # Consolidated Mapping
        concept_type_lower = concept_type.lower()
        
        # --- Events & Contexts ---
        if concept_type_lower == 'event':
            _navigation_structure["TakEntity"]["Event"].append(entity_data)
        elif concept_type_lower == 'context':
            _navigation_structure["TakEntity"]["Context"].append(entity_data)
            
        # --- Raw Concepts ---
        elif concept_type_lower in ['raw-numeric', 'raw-ordinal', 'raw-nominal', 'raw-boolean', 'raw-datetime']:
            _navigation_structure["TakEntity"]["Concept"]["RawConcept"].append(entity_data)
            
        # --- Abstract Concepts ---
        elif concept_type_lower in ['state', 'gradient', 'trend', 'rate', 'pattern']:
            _navigation_structure["TakEntity"]["Concept"]["AbstractConcept"].append(entity_data)
            
        else:
            logger.warning(f"Warning: File '{filename}' has unknown concept-type: '{concept_type}'")
            
    except ET.ParseError as e:
        logger.error(f"Error parsing XML in {filename}: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing file {filename}: {str(e)}")


def scan_directory(directory: str) -> None:
    if not os.path.exists(directory):
        logger.error(f"Directory {directory} not found.")
        return

    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.xml'):
                file_path = os.path.join(root_dir, file)
                process_file(file_path, file)


def build_hierarchy(tak_files_dir: str) -> None:
    global _is_built, _navigation_structure
    
    if _is_built:
        return
        
    logger.info(f"Scanning directory: {tak_files_dir}...")
    try:
        if not os.path.exists(tak_files_dir):
            logger.error(f"Directory {tak_files_dir} not found.")
            return
            
        # Reset just in case it's called multiple times
        _navigation_structure = _init_navigation_structure()
        scan_directory(tak_files_dir)
        _is_built = True
        logger.info("Hierarchy build complete.")
    except Exception as e:
        logger.error(f"Failed to read directory: {str(e)}")

def get_navigation_structure(tak_files_dir: str = None) -> Dict[str, Any]:
    # Lazy load if the directory is provided and not built yet
    if tak_files_dir and not _is_built:
        build_hierarchy(tak_files_dir)
        
    return _navigation_structure
