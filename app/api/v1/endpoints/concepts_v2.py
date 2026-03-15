from fastapi import APIRouter, HTTPException
from typing import Union
from app.services.concept_manager_v2 import concept_manager_v2_instance
from app.models.concept_v2 import (
    TAKEntity, Event, Context, 
    NumericRawConcept, NominalRawConcept, 
    State, Trend, Pattern
)

router = APIRouter()


@router.get("/{concept_name}/knowledge-exploration")
def get_tak_object_by_name(concept_name: str):
    """
    Get full TAK concept definition by name. 
    Returns all defined fields on the specific subclass.
    """
    entity = concept_manager_v2_instance.get_entity_by_name(concept_name)
    
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
    entity = concept_manager_v2_instance.get_entity_by_name(concept_name)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")

    # Base fields from TAKEntity
    fields_to_include = {"id", "name", "concept_type"}

    # Add specific fields based on the type
    if isinstance(entity, NumericRawConcept):
        fields_to_include.update({"min", "max"})
    elif isinstance(entity, (NominalRawConcept, State, Trend, Pattern)):
        fields_to_include.add("values")
        
    return entity.model_dump(include=fields_to_include, by_alias=True)
