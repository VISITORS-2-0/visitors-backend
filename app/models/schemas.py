from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
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
    values: List[str] = ["Normal", "High", "Moderately_low"]
    concept_name: str = "WBC_STATE_BMT"
    start_year: int = 1991
    end_year: int = 1994

class TransformationRequest(BaseModel):
    data: List[PatientEvent]
    interval_str: str = "W-MON" # e.g., 'W-MON', 'M', 'MS', 'D'
    method: str = "most_time_spent"

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
