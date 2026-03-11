from typing import List
from fastapi import APIRouter
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, DataRequest, Record, IntervalSummary
from app.services.visitors_queries import VisitorsQueriesService

router = APIRouter()

@router.post("/multiple-patients-abstraction", response_model=VisitorResponse[List[IntervalSummary]])
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest):
    """
    Abstract multiple patients data flow: Fetch -> Transform -> Summarize.
    Returns the summary intervals.
    """
    return VisitorsQueriesService.create_multiple_patients_abstraction(request)

@router.post("/abstraction", response_model=VisitorResponse[List[Record]])
def fetch_abstraction(request: DataRequest):
    """
    Fetches real patient data (Abstraction). Returns fetched abstraction records.
    """
    return VisitorsQueriesService.fetch_abstraction(request)

@router.post("/raw-data", response_model=VisitorResponse[List[Record]])
def fetch_raw_data_abstraction(request: DataRequest):
    """
    Fetch raw data. Returns fetched raw records.
    """
    return VisitorsQueriesService.fetch_raw_data(request)
