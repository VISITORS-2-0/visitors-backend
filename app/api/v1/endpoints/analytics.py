from fastapi import APIRouter
from typing import List
from app.models.schemas import SummaryRequest, IntervalSummary
from app.services.summer import SummaryService

router = APIRouter()

@router.post("/", response_model=List[IntervalSummary])
def summarize_intervals(request: SummaryRequest):
    """
    Generate a summary of interval distributions.
    """
    return SummaryService.summarize_intervals(request.data)
