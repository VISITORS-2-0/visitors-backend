from fastapi import APIRouter
from typing import List
from app.models.schemas import TransformationRequest, Record
from app.services.transformer import IntervalTransformationService

router = APIRouter()

@router.post("/", response_model=List[Record])
def transform_data(request: TransformationRequest):
    """
    Transform raw patient events into fixed intervals.
    """
    return IntervalTransformationService.transform_to_intervals(
        events=request.data,
        interval_str=request.interval_str,
        method=request.method
    )
