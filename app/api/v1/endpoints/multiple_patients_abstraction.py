from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse
from app.services.multiple_patients_abstraction import MultiplePatientsAbstractionService

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
def abstract_multiple_patients(request: MultiplePatientsAbstractionRequest, db: Session = Depends(get_db)):
    """
    Abstract multiple patients data flow: Generate -> Transform -> Summarize.
    Returns the final summary.
    """
    return MultiplePatientsAbstractionService.run_flow(request, db)
