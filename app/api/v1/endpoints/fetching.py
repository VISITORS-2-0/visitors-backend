from fastapi import APIRouter
from typing import List
from app.models.schemas import DataRequest, Record
from app.services.data_fetcher import csv_fetcher

router = APIRouter()

@router.post("/", response_model=List[Record])
def fetch_data(request: DataRequest):
    """
    Fetches patient data from the data source.
    """
    return csv_fetcher.fetch_data(request, abstract=True)
