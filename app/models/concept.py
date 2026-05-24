from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

class ConditionMapping(BaseModel):
    abstracted_from_concept: str
    values_accepted: str

class CategoryMapping(BaseModel):
    order: int
    category: str
    logical_operation: Optional[str] = None
    conditions: List[ConditionMapping]

class MappingAbstractions(BaseModel):
    category_mappings: List[CategoryMapping]

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

    # We define the type as a List of strings, and map it to the JSON key "derived-from"
    derived_from: List[str] = Field(default_factory=list, validation_alias="derived-from")
    derived_into: List[str] = Field(default_factory=list)
    siblings: List[str] = Field(default_factory=list)
    context: List[str] = Field(default_factory=list)
    mapping_abstractions: Optional[MappingAbstractions] = None

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
        if self.__class__.__name__ == "NumericRawConcept":
            self.duration_type = "point"
        else:
            self.duration_type = "interval"
        
        if self.values == ["Normal", "High", "Low"]:
            self.values = ["Low", "Normal", "High"]
        
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
    values: Optional[List[str]] = Field(default=["TRUE"])

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
    pass


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
    values: Optional[List[str]] = Field(default=["Inc", "Same", "Dec"])

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

def parse_mapping_abstractions(raw_data: dict, id_to_name_fn) -> Optional[MappingAbstractions]:
    mf = raw_data.get("mapping-function")
    if not isinstance(mf, dict):
        return None
        
    mfts = mf.get("mapping-functions-to-values", {})
    mf2vs = mfts.get("mapping-function-2-value", [])
    if isinstance(mf2vs, dict):
        mf2vs = [mf2vs]
        
    category_mappings = []
    
    for item in mf2vs:
        val = item.get("@value")
        if not val:
            continue
            
        tree = item.get("evaluation-tree", {})
        
        conditions = []
        logical_op = None
        
        def parse_node(node):
            nonlocal logical_op
            if not node:
                return
            if "logical-function" in node:
                lf = node["logical-function"]
                op = lf.get("@logical-operator", "and")
                if logical_op is None:
                    logical_op = op
                
                operands = lf.get("operands", {}).get("operand", [])
                if isinstance(operands, dict):
                    operands = [operands]
                for operand in operands:
                    parse_node(operand)
            elif "comparison-function" in node:
                cf = node["comparison-function"]
                op = cf.get("@comparison-operator", "")
                
                ops_map = {
                    "bigger": ">",
                    "smaller": "<",
                    "bigger-equal": ">=",
                    "smaller-equal": "<=",
                    "equal": "==",
                }
                symbol = ops_map.get(op, op)
                
                left_node = cf.get("left", {})
                concept_id = left_node.get("concept-id-allowed-values", {}).get("@id")
                concept_name = id_to_name_fn(concept_id) if concept_id else "Unknown"
                
                right_node = cf.get("right", {})
                right_val = ""
                if "double" in right_node:
                    right_val = right_node.get("double")
                elif "integer" in right_node:
                    right_val = right_node.get("integer")
                elif "string" in right_node:
                    right_val = right_node.get("string")
                    
                conditions.append(ConditionMapping(
                    abstracted_from_concept=concept_name,
                    values_accepted=f"{symbol}{right_val}"
                ))

        parse_node(tree)
        
        compressed_conditions = []
        # If it's an AND operation or single condition, we can combine bounds for the same concept
        if logical_op == "and" or logical_op is None:
            concept_to_bounds = {}
            for c in conditions:
                concept_to_bounds.setdefault(c.abstracted_from_concept, []).append(c.values_accepted)
            
            for concept, bounds in concept_to_bounds.items():
                if len(bounds) > 1:
                    compressed_conditions.append(ConditionMapping(
                        abstracted_from_concept=concept,
                        values_accepted=" and ".join(bounds)
                    ))
                else:
                    compressed_conditions.append(ConditionMapping(
                        abstracted_from_concept=concept,
                        values_accepted=bounds[0]
                    ))
        else:
             compressed_conditions = conditions
        order_str = item.get("@order")
        order_val = int(order_str) if order_str is not None else 0
             
        category_mappings.append(CategoryMapping(
            order=order_val,
            category=val,
            logical_operation=logical_op if len(compressed_conditions) > 1 else None,
            conditions=compressed_conditions
        ))
        
    if category_mappings:
        return MappingAbstractions(category_mappings=category_mappings)
    return None
