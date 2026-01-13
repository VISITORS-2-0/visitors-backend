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
    num_patients: int = Field(20, ge=1)
    concept_name: str = "WBC_STATE_BMT"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)

class TransformationRequest(BaseModel):
    data: List[PatientEvent]
    interval_str: Literal['W-MON', 'M', 'MS', 'D'] = "W-MON"
    method: Literal['most_time_spent'] = "most_time_spent"

class SummaryRequest(BaseModel):
    data: List[IntervalRecord]

class IntervalSummary(BaseModel):
    StartTime: datetime
    EndTime: datetime
    ConceptName: str
    Value_Dict: Dict[str, int]
    TotalPatientsWithData: int

class SummaryResponse(BaseModel):
    summary: List[IntervalSummary]

class MultiplePatientsAbstractionRequest(BaseModel):
    # Generation Params
    num_patients: int = Field(20, ge=1)
    concept_name: str = "WBC_STATE_BMT"
    start_date: datetime = datetime(1991, 1, 1)
    end_date: datetime = datetime(1994, 12, 31)
    
    # Transformation Params
    interval_str: Literal['W-MON', 'M', 'MS', 'D'] = "W-MON"
    method: Literal['most_time_spent'] = "most_time_spent"
