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

@router.post("/abstraction", response_model=List[PatientEvent])
def generate_abstraction(request: GenerationRequest):
    """
    Generates synthetic patient data (Abstraction).
    Previously /generate.
    """
    return DataGeneratorService.generate_data(request)

@router.post("/raw-data", response_model=List[PatientEvent])
def generate_raw_data_abstraction(request: GenerationRequest):
    """
    Generate raw data for the abstraction request (skip transform/summarize) with numeric values.
    """
    # We can reuse the VisitorsQueriesService.generate_raw_data, but we need to adapt the request
    # or just call generator directly if the service expects MultiplePatientsAbstractionRequest.
    # The service method generate_raw_data expects MultiplePatientsAbstractionRequest.
    # Let's check the service.
    
    # Actually, we can just instantiate the request the service needs, or simpler:
    # ensure VisitorsQueriesService.generate_raw_data takes GenerationRequest? 
    # Or just call DataGeneratorService.generate_numeric_data directly here?
    # The user said "remove interval_str... from raw-data param", so input must be GenerationRequest.
    
    return DataGeneratorService.generate_numeric_data(request)
