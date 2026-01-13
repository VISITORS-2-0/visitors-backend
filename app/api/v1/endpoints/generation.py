from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import GenerationRequest, PatientEvent
from app.services.generator import DataGeneratorService

router = APIRouter()

@router.post("/", response_model=List[PatientEvent])
def generate_data(request: GenerationRequest, db: Session = Depends(get_db)):
    """
    Generates synthetic patient data.
    """
    return DataGeneratorService.generate_data(request, db)
