from fastapi import APIRouter
from app.models.schemas import SummaryRequest, SummaryResponse
from app.services.summer import SummaryService

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
def summarize_intervals(request: SummaryRequest):
    """
    Generate a summary of interval distributions.
    """
    return SummaryService.summarize_intervals(request.data)
