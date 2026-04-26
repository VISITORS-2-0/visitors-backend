from fastapi import APIRouter
from typing import List
from app.models.schemas import DataRequest, Record
from app.services.data_fetcher import mongo_fetcher

router = APIRouter()

@router.post("/", response_model=List[Record])
def fetch_data(request: DataRequest):
    """
    Fetches patient data from the database.
    """
    return mongo_fetcher.fetch_data(request, abstract=True)
