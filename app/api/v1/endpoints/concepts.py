from fastapi import APIRouter, HTTPException
from typing import Union
from app.services.concept_manager import concept_manager_instance
from app.models.concept import (
    TAKEntity, Event, Context, 
    NumericRawConcept, NominalRawConcept, 
    State, Trend, Pattern
)
from app.services.menu_builder import get_navigation_structure
from app.core.config import settings

router = APIRouter()

@router.get("/menu")
def get_menu():
    """
    Get menu by scanning TakEntities XML files.
    """
    try:
        # Pass the directory to get_navigation_structure to lazy-load if not built
        return get_navigation_structure(settings.TAK_FILES_DIR)
    except Exception as e:
        # In production we might want to log this or return a 500, but for now getting the error detail is helpful if it persists.
        raise e

@router.get("/{concept_name}/knowledge-exploration")
def get_tak_object_by_name(concept_name: str):
    """
    Get full TAK concept definition by name. 
    Returns all defined fields on the specific subclass.
    """
    entity = concept_manager_instance.get_entity_by_name(concept_name)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")
        
    data = entity.model_dump(by_alias=True, exclude_none=True)
    
    if "min" in data and "max" in data:
        if "values" in data:
            del data["values"]
            
    return data

@router.get("/{concept_name}")
def get_tak_object_basic_by_name(concept_name: str):
    """
    Get basic TAK concept definition by name. 
    Only returns TAKEntity fields, plus conditionally min/max or values.
    """
    entity = concept_manager_instance.get_entity_by_name(concept_name)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")

    result = {
        "id": entity.id, 
        "name": entity.name, 
        "concept_type": entity.concept_type,
        "output_type": entity.output_type,
        "duration_type": entity.duration_type
    }

    # Add specific fields based on whether min/max are present
    if entity.min is not None and entity.max is not None:
        result["min"] = entity.min
        result["max"] = entity.max
    else:
        values = getattr(entity, "values", None)
        if values is not None:
            result["values"] = values
        
    return result
