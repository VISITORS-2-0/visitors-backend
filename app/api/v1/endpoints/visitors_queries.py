from typing import List
from fastapi import APIRouter
from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse, PatientEvent, GenerationRequest
from app.services.visitors_queries import VisitorsQueriesService
from app.services.generator import DataGeneratorService

router = APIRouter()

@router.post("/multiple-patients-abstraction", response_model=SummaryResponse)
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest):
    """
    Abstract multiple patients data flow: Generate -> Transform -> Summarize.
    Returns the final summary.
    """
    return VisitorsQueriesService.run_flow(request)

@router.post("/abstraction", response_model=SummaryResponse)
def generate_abstraction(request: GenerationRequest):
    """
    Generates synthetic patient data (Abstraction) with summary.
    """
    return VisitorsQueriesService.generate_abstraction(request)

@router.post("/raw-data", response_model=SummaryResponse)
def generate_raw_data_abstraction(request: GenerationRequest):
    """
    Generate raw data (numeric) with summary.
    """
    return VisitorsQueriesService.generate_raw_data(request)
