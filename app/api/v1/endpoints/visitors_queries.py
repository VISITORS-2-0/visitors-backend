from typing import List
from fastapi import APIRouter
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, DataRequest, Record, IntervalSummary, MultiplePatientsNumericAbstractionRequest
from app.services.visitors_queries import VisitorsQueriesService

router = APIRouter()

@router.post("/multiple-patients-abstraction", response_model=VisitorResponse[List[IntervalSummary]])
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest):
    """
    Abstract multiple patients data flow: Generate -> Transform -> Summarize.
    Returns the summary intervals.
    """
    return VisitorsQueriesService.create_multiple_patients_abstraction(request)

@router.post("/multiple-patients-numeric-abstraction", response_model=VisitorResponse[List[IntervalSummary]])
def abstract_multiple_patients_numeric(request: MultiplePatientsNumericAbstractionRequest):
    """
    Abstract multiple patients data flow for numeric continuous values.
    Divides the numeric range into specified/default bins before abstracting and returning the summary intervals.
    """
    return VisitorsQueriesService.create_multiple_patients_numeric_abstraction(request)

@router.post("/abstraction", response_model=VisitorResponse[List[Record]])
def generate_abstraction(request: DataRequest):
    """
    Generates synthetic patient data (Abstraction). Returns generated records.
    """
    return VisitorsQueriesService.generate_abstraction(request)

@router.post("/raw-data", response_model=VisitorResponse[List[Record]])
def generate_raw_data_abstraction(request: DataRequest):
    """
    Generate raw data (numeric). Returns generated records.
    """
    return VisitorsQueriesService.generate_raw_data(request)
