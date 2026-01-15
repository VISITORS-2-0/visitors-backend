from typing import List
from fastapi import APIRouter
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, GenerationRequest, Record, IntervalSummary
from app.services.visitors_queries import VisitorsQueriesService

router = APIRouter()

@router.post("/multiple-patients-abstraction", response_model=VisitorResponse[List[IntervalSummary]])
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest):
    """
    Abstract multiple patients data flow: Generate -> Transform -> Summarize.
    Returns the summary intervals.
    """
    return VisitorsQueriesService.create_multiple_patients_abstraction(request)

@router.post("/abstraction", response_model=VisitorResponse[List[Record]])
def generate_abstraction(request: GenerationRequest):
    """
    Generates synthetic patient data (Abstraction). Returns generated records.
    """
    return VisitorsQueriesService.generate_abstraction(request)

@router.post("/raw-data", response_model=VisitorResponse[List[Record]])
def generate_raw_data_abstraction(request: GenerationRequest):
    """
    Generate raw data (numeric). Returns generated records.
    """
    return VisitorsQueriesService.generate_raw_data(request)
