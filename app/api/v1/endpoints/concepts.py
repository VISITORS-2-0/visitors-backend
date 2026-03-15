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
        
    return entity

@router.get("/{concept_name}")
def get_tak_object_basic_by_name(concept_name: str):
    """
    Get basic TAK concept definition by name. 
    Only returns TAKEntity fields, plus:
    - min and max if it is a NumericRawConcept
    - values otherwise (if applicable)
    """
    entity = concept_manager_instance.get_entity_by_name(concept_name)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")

    result = {"id": entity.id, "name": entity.name, "concept_type": entity.concept_type}

    # Add specific fields based on the type
    if isinstance(entity, NumericRawConcept):
        result["min-value"] = entity.min
        result["max-value"] = entity.max
    elif isinstance(entity, (NominalRawConcept, State, Trend, Pattern)):
        result["values"] = entity.values
        
    return result
