from fastapi import APIRouter
from typing import List
from app.models.schemas import GenerationRequest, PatientEvent
from app.services.generator import DataGeneratorService

router = APIRouter()

@router.post("/", response_model=List[PatientEvent])
def generate_data(request: GenerationRequest):
    """
    Generates synthetic patient data.
    """
    return DataGeneratorService.generate_data(request)
