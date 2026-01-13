from typing import List
from fastapi import APIRouter
from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse, PatientEvent
from app.services.visitors_queries import VisitorsQueriesService

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest):
    """
    Abstract multiple patients data flow: Generate -> Transform -> Summarize.
    Returns the final summary.
    """
    return VisitorsQueriesService.run_flow(request)

@router.post("/raw-data", response_model=List[PatientEvent])
def generate_raw_data_abstraction(request: MultiplePatientsAbstractionRequest):
    """
    Generate raw data for the abstraction request (skip transform/summarize) with numeric values.
    """
    return VisitorsQueriesService.generate_raw_data(request)
