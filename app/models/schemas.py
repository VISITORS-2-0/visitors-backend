from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Literal, TypeVar, Generic

T = TypeVar("T")
from datetime import datetime

# --- Shared Models ---

# --- Shared Models ---

class Record(BaseModel):
    StartTime: datetime
    EndTime: datetime
    Value: str
    PatientID: int
    ConceptName: str

    class Config:
         json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# --- Shared Models ---

class ReferenceConcept(BaseModel):
    concept_name: str
    concept_value: Optional[str] = None

class RelativeTimeConfig(BaseModel):
    reference_concepts: List[ReferenceConcept]
    occurrence_index: int = -1
    start_delta: int
    end_delta: int

    @field_validator('reference_concepts')
    @classmethod
    def check_non_empty(cls, v: List[ReferenceConcept]) -> List[ReferenceConcept]:
        if not v:
            raise ValueError("reference_concepts list must not be empty.")
        return v


# --- Request/Response Models for Services ---

class DataRequest(BaseModel):
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "AbsCI_or_RelCI_state"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    use_generated_data: bool = False
    relative_time: Optional[RelativeTimeConfig] = None
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"

class TransformationRequest(BaseModel):
    data: List[Record]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"

class SummaryRequest(BaseModel):
    data: List[Record]

class IntervalSummary(BaseModel):
    StartTime: datetime
    EndTime: datetime
    ConceptName: str
    Value_Dict: Dict[str, int]
    TotalPatientsWithData: int

class VisitorResponse(BaseModel, Generic[T]):
    concept_data: Optional[Dict[str, Any]] = None
    result: T

class MultiplePatientsAbstractionRequest(BaseModel):
    # Fetching Params
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "AbsCI_or_RelCI_state"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    use_generated_data: bool = False
    relative_time: Optional[RelativeTimeConfig] = None
    
    # Transformation Params
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"

class NumericRange(BaseModel):
    min: float
    max: float

class MultiplePatientsNumericAbstractionRequest(BaseModel):
    # Generation Params
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "AbsCI_or_RelCI_state"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    use_generated_data: bool = False
    relative_time: Optional[RelativeTimeConfig] = None
    
    # Transformation Params
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"
    
    # New parameter for numeric abstraction
    ranges: Optional[List[NumericRange]] = None

