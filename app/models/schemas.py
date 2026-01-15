from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

# --- Shared Models ---

class PatientEvent(BaseModel):
    StartTime: datetime
    EndTime: datetime
    Value: str
    PatientID: int
    ConceptName: str

    class Config:
         json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class IntervalRecord(BaseModel):
    StartTime: datetime
    EndTime: datetime
    Value: str  # Can be 'No Value'
    PatientID: int
    ConceptName: str

    class Config:
         json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# --- Request/Response Models for Services ---

class GenerationRequest(BaseModel):
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "WBC_STATE_BMT2"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)
    
    # Defaults for optional summarization
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"

class TransformationRequest(BaseModel):
    data: List[PatientEvent]
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"

class SummaryRequest(BaseModel):
    data: List[IntervalRecord]

class IntervalSummary(BaseModel):
    StartTime: datetime
    EndTime: datetime
    ConceptName: str
    Value_Dict: Dict[str, int]
    TotalPatientsWithData: int

class ConceptSchema(BaseModel):
    name: str
    type: str
    allowed_values: Dict[str, Any]

class SummaryResponse(BaseModel):
    summary: List[IntervalSummary]
    events: List[PatientEvent] = []
    concept_data: Optional[ConceptSchema] = None

class MultiplePatientsAbstractionRequest(BaseModel):
    # Generation Params
    patients_list: List[str] = Field(..., example=[str(i) for i in range(1000, 1021)])
    concept_name: str = "WBC_STATE_BMT2"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)
    
    # Transformation Params
    interval_str: Literal['D', 'W-SUN', 'ME', 'YE'] = "ME"
    method: Literal['most_time_spent'] = "most_time_spent"
