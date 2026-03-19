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

    min: Optional[float] = None
    max: Optional[float] = None
    output_type: Optional[str] = None
    duration_type: Optional[str] = None
    values: Optional[List[str]] = None

    @model_validator(mode="before")
    @classmethod
    def _extract_min_max_and_types(cls, obj: any):
        if not isinstance(obj, dict):
            return obj

        # Extract min and max
        numeric_allowed_values = obj.get("numeric-allowed-values", None)
        if isinstance(numeric_allowed_values, dict):
            min_val = numeric_allowed_values.get("@min-value")
            max_val = numeric_allowed_values.get("@max-value")
            
            if min_val is not None:
                obj["min"] = float(min_val)
            if max_val is not None:
                obj["max"] = float(max_val)
        
        return obj

    @model_validator(mode="after")
    def _determine_types(self) -> 'TAKEntity':
        # 1. Determine duration_type
        if "Raw" in self.__class__.__name__:
            self.duration_type = "point"
        else:
            self.duration_type = "interval"
            
        # 2. Determine output_type
        # If there are values, it's categorial, even if it has min/max
        if self.values:
            self.output_type = "categorial"
        elif self.min is not None and self.max is not None:
            self.output_type = "range"
        else:
            self.output_type = "categorial"
            
        return self

# ==========================================
# Level 1 Entities
# ==========================================

class Event(TAKEntity):
    """Event class"""
    values: Optional[List[str]] = Field(default=["True"])

class Context(TAKEntity):
    """Context class"""
    values: Optional[List[str]] = Field(default=["True"])

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
    # Inherits min and max from TAKEntity

class NominalRawConcept(RawConcept):
    """Nominal Raw Concept"""

    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        return extract_values(obj, "nominal-allowed-values", "nominal-allowed-value")


# --- Abstract Concepts ---

class State(AbstractConcept):
    """State abstraction concept"""
    
    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        obj = extract_values(obj, "ordinal-allowed-values", "ordinal-allowed-value")
        # If still no values, check mapping-function
        if obj.get("values") is None and isinstance(obj.get("mapping-function"), dict):
            mf = obj["mapping-function"]
            mfts = mf.get("mapping-functions-to-values", {})
            mf2vs = mfts.get("mapping-function-2-value", [])
            if isinstance(mf2vs, dict): # Single value
                mf2vs = [mf2vs]
            values = [v.get("@value") for v in mf2vs if v.get("@value")]
            if values:
                obj["values"] = values
        return obj

class Trend(AbstractConcept):
    """Trend abstraction concept"""
    
    @model_validator(mode="before")
    @classmethod
    def _extract_values(cls, obj: any):
        return extract_values(obj, "gradient-trend-allowed-values", "ordinal-allowed-value")

class Pattern(AbstractConcept):
    """Pattern concept"""

    @model_validator(mode="before")
    @classmethod
    def _set_default_values(cls, obj: any):
        if isinstance(obj, dict):
            has_numeric = obj.get("numeric-allowed-values") is not None
            has_min = "min" in obj
            has_max = "max" in obj
            
            # If numeric-allowed-values exists but min and max are absent (null)
            if has_numeric and not has_min and not has_max:
                try:
                    left_id = obj.get("pattern-output", {}).get("value-local-pattern", {}).get("mathematical-function", {}).get("left", {}).get("concept-id-allowed-values", {}).get("@id")
                    if left_id:
                        # Local import to avoid circular dependency
                        from app.services.concept_manager import concept_manager_instance
                        dep_concept = concept_manager_instance.get_entity_by_id(left_id)
                        if dep_concept:
                            if dep_concept.min is not None:
                                obj["min"] = dep_concept.min
                            if dep_concept.max is not None:
                                obj["max"] = dep_concept.max
                except Exception:
                    pass

            # Update has_min and has_max after potential extraction
            has_min = "min" in obj
            has_max = "max" in obj
            
            # If still no min/max and no values
            if not has_min and not has_max and obj.get("values") is None:
                obj["values"] = ["True"]
        return obj


def extract_values(obj: dict, parameter: str, parameter2: str) -> dict:
    allowed_values = obj.get(parameter, None)

    if isinstance(allowed_values, dict):
        allowed_values = allowed_values.get("values").get(parameter2)
        
        if isinstance(allowed_values, dict):
            allowed_values = [allowed_values]
        
        values = [value_obj.get("@value") for value_obj in allowed_values]
        
        obj["values"] = values
    
    return obj