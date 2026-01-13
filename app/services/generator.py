import random
from datetime import datetime, timedelta
from typing import List
from functools import lru_cache
from app.models.schemas import GenerationRequest, PatientEvent

from sqlalchemy.orm import Session
from app.services.concept_manager import ConceptManager

class DataGeneratorService:
    @staticmethod
    def generate_data(request: GenerationRequest, db: Session) -> List[PatientEvent]:
        # Fetch allowed values from DB
        concept_schema = ConceptManager.get_or_create_concept(db, request.concept_name)
        values = concept_schema.allowed_values.get("values", [])
        
        # Unpack params and convert list to tuple for hashing
        return DataGeneratorService._generate_cached(
            request.num_patients,
            request.start_year,
            request.end_year,
            tuple(values),
            request.concept_name
        )

    @staticmethod
    @lru_cache(maxsize=32)
    def _generate_cached(num_patients: int, start_year: int, end_year: int, values: tuple, concept_name: str) -> List[PatientEvent]:
        new_data = []

        for i in range(num_patients):
            patient_id = 1000 + i
            
            # Random start time in the first half of the start year
            current_time = datetime(start_year, 1, 1) + timedelta(days=random.randint(0, 180))
            
            # Generate events until the end of the end_year
            while current_time.year <= end_year:
                # 20% chance of a "point event" (0 duration)
                if random.random() < 0.2:
                    duration_minutes = 0
                else:
                    duration_minutes = random.randint(1, 5 * 24 * 60)
                
                end_time = current_time + timedelta(minutes=duration_minutes)
                val = random.choice(values)
                
                new_data.append(PatientEvent(
                    StartTime=current_time,
                    EndTime=end_time,
                    Value=val,
                    PatientID=patient_id,
                    ConceptName=concept_name
                ))
                
                # Random gap between 1 hour and 30 days
                gap_minutes = random.randint(60, 30 * 24 * 60)
                current_time = end_time + timedelta(minutes=gap_minutes)
                
        return new_data
