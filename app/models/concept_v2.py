from pydantic import model_validator
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any

# ==========================================
# Root Entity
# ==========================================

class TAKEntity(BaseModel):
    """The root abstract class for all TAK entities."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: Optional[str] = Field(alias="@id", default=None)
    name: Optional[str] = Field(alias="@name", default=None)
    concept_type: Optional[str] = Field(alias="@concept-type", default=None)


# ==========================================
# Level 1 Entities
# ==========================================

class Event(TAKEntity):
    """Event class"""
    pass

class Context(TAKEntity):
    """Context class"""
    pass

class Concept(TAKEntity):
    """Base class for all Concepts"""
    pass


# ==========================================
# Level 2 Entities (Concept Branches)
# ==========================================

class RawConcept(Concept):
    """Base class for Raw Concepts"""
    pass

class AbstractConcept(Concept):
    """Base class for Abstract Concepts"""
    
    # We define the type as a List of strings, and map it to the JSON key "derived-from"
    derived_from: List[str] = Field(default_factory=list, alias="derived-from")
    derived_into: List[str] = Field(default_factory=list)
    siblings: List[str] = Field(default_factory=list)

    @field_validator("derived_from", mode="before")
    @classmethod
    def extract_derived_from_ids(cls, value: Any) -> List[str]:
        """
        Extracts the 'derived-from-id' from the nested dictionary and 
        ensures it is always returned as a list of strings.
        """
        # Handle the expected nested dictionary format from the JSON
        if isinstance(value, dict):
            inner_val = value.get("derived-from-id")
            
            if inner_val is None:
                return []
            
            # If it's a single string, wrap it in a list
            if isinstance(inner_val, str):
                return [inner_val]
            
            # If it's already a list, ensure all elements are strings
            if isinstance(inner_val, list):
                return [str(v) for v in inner_val]
                
        # Fallbacks just in case the data comes in already somewhat flattened
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(v) for v in value]
            
        return []


# ==========================================
# Level 3 Entities (Specific Concepts)
# ==========================================

# --- Raw Concepts ---

class NumericRawConcept(RawConcept):
    """Numeric Raw Concept"""

    # numeric_allowed_values: Optional[dict] = Field(default=None, alias="numeric-allowed-values")
    min: Optional[float] = None
    max: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def _extract_min_max(cls, obj: any) -> List[str]:
        numeric_allowed_values = obj.pop("numeric-allowed-values", None)

        if isinstance(numeric_allowed_values, dict):
            min_val = numeric_allowed_values.get("@min-value")
            max_val = numeric_allowed_values.get("@max-value")
            
            obj["min"] = float(min_val)
            obj["max"] = float(max_val)
        
        return obj

class NominalRawConcept(RawConcept):
    """Nominal Raw Concept"""
    values: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        nominal_allowed_values = obj.pop("nominal-allowed-values", None)

        if isinstance(nominal_allowed_values, dict):
            nominal_allowed_values = nominal_allowed_values.get("values").get("nominal-allowed-value")
            
            if isinstance(nominal_allowed_values, dict):
                nominal_allowed_values = [nominal_allowed_values]
            
            values = [value_obj.get("@value") for value_obj in nominal_allowed_values]
            
            obj["values"] = values
        
        return obj


# --- Abstract Concepts ---

class State(AbstractConcept):
    """State abstraction concept"""
    values: List[str] = Field(default_factory=list)
    
    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        return extract_values(obj, "ordinal-allowed-values", "ordinal-allowed-value")

class Trend(AbstractConcept):
    """Trend abstraction concept"""
    values: List[str] = Field(default_factory=list)
    
    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        return extract_values(obj, "gradient-trend-allowed-values", "ordinal-allowed-value")

class Pattern(AbstractConcept):
    """Pattern concept"""
    values: List[str] = ["True"]


def extract_values(obj: dict, parameter: str, parameter2: str) -> dict:
    allowed_values = obj.pop(parameter, None)

    if isinstance(allowed_values, dict):
        allowed_values = allowed_values.get("values").get(parameter2)
        
        if isinstance(allowed_values, dict):
            allowed_values = [allowed_values]
        
        values = [value_obj.get("@value") for value_obj in allowed_values]
        
        obj["values"] = values
    
    return obj