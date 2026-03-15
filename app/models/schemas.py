from pydantic import BaseModel, Field
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

# --- Request/Response Models for Services ---

class GenerationRequest(BaseModel):
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "AbsCI_or_RelCI_state"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)

class TransformationRequest(BaseModel):
    data: List[Record]
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
    # Generation Params
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "AbsCI_or_RelCI_state"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)
    
    # Transformation Params
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"
