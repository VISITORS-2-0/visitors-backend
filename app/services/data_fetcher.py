from abc import ABC, abstractmethod
from typing import List
from pymongo import MongoClient
from app.models.schemas import DataRequest, Record
from app.core.config import settings

class DataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, request: DataRequest, abstract: bool = True) -> List[Record]:
        """
        Fetch data based on the request.
        :param abstract: Whether to fetch from abstract store or raw store.
        """
        pass

class MongoDataFetcher(DataFetcher):
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.raw_collection = self.db["raw_medical_data"]
        self.abstract_collection = self.db["abstract_medical_data"]

    def fetch_data(self, request: DataRequest, abstract: bool = True) -> List[Record]:
        collection = self.abstract_collection if abstract else self.raw_collection
        
        # Build query
        # We need PatientID to match integer type based on Record schema assumptions
        try:
            patient_ids = [int(p) for p in request.patients_list]
        except ValueError:
            # Fallback if string mapping required
            patient_ids = request.patients_list

        query = {
            "ConceptName": request.concept_name,
            "PatientID": {"$in": patient_ids},
            "StartTime": {
                "$gte": request.start_date,
                "$lte": request.end_date
            }
        }

        # Fetch and map to Record objects
        cursor = collection.find(query)
        results = []
        for doc in cursor:
            # Extract fields safely, ignoring Mongo's _id
            results.append(Record(
                StartTime=doc["StartTime"],
                EndTime=doc["EndTime"],
                Value=str(doc["Value"]),
                PatientID=doc["PatientID"],
                ConceptName=doc["ConceptName"]
            ))
            
        return results

# Singleton instance to be used by services
mongo_fetcher = MongoDataFetcher()
