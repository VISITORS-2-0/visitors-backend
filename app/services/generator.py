import random
from datetime import datetime, timedelta
from typing import List
# from functools import lru_cache
from app.models.schemas import GenerationRequest, Record
from app.services.concept_manager import concept_manager_instance
from app.core.cache_utils import db_cache

class DataGeneratorService:
    @staticmethod
    def generate_data(request: GenerationRequest) -> List[Record]:
        # Fetch allowed values from DB (using internal session)
        concept = concept_manager_instance.get_entity_by_name(request.concept_name)
        values = getattr(concept, "values", []) if concept else []
        
        # Unpack params and convert list to tuple for hashing
        return DataGeneratorService._generate_cached(
            tuple(request.patients_list),
            request.start_date,
            request.end_date,
            tuple(values),
            request.concept_name,
            # Using defaults for min/max since they are removed from request schema
            0.0, 
            100.0,
            allow_numeric=False # Strict: only use values
        )

    @staticmethod
    def generate_numeric_data(request: GenerationRequest) -> List[Record]:
        concept = concept_manager_instance.get_entity_by_name(request.concept_name)
        min_v = getattr(concept, "min", 0.0) if concept else 0.0
        max_v = getattr(concept, "max", 100.0) if concept else 100.0
        
        return DataGeneratorService._generate_cached(
            tuple(request.patients_list),
            request.start_date,
            request.end_date,
            (), # empty values
            request.concept_name,
            min_v,
            max_v,
            allow_numeric=True # Allow numeric generation
        )

    @staticmethod
    @db_cache
    def _generate_cached(patients_list: tuple, start_date: datetime, end_date: datetime, values: tuple, concept_name: str, min_value: float = 0.0, max_value: float = 100.0, allow_numeric: bool = False) -> List[Record]:
        new_data = []

        total_seconds = int((end_date - start_date).total_seconds())
        if total_seconds <= 0:
            return []

        for patient_id_str in patients_list:
            try:
                patient_id = int(patient_id_str)
            except ValueError:
                # If ID is not an int, we might need a workaround if Record requires int. 
                # Schema says PatientID is int. 
                # User said "list of id str of numbers", so we assume they are convertible.
                patient_id = hash(patient_id_str) % 100000 # Fallback or just assume int conversion per schema requirements. 
                # But let's try strict conversion as per user "id str of numbers"
                patient_id = int(patient_id_str)
            
            # Start somewhere in the first 10% of the range or first 6 months
            offset_seconds = random.randint(0, min(total_seconds // 10, 180 * 24 * 3600))
            current_time = start_date + timedelta(seconds=offset_seconds)
            
            # Generate events until the end_date
            while current_time <= end_date:
                # 20% chance of a "point event" (0 duration)
                if random.random() < 0.2:
                    duration_minutes = 0
                else:
                    duration_minutes = random.randint(1, 5 * 24 * 60) # up to 5 days
                
                end_time = current_time + timedelta(minutes=duration_minutes)
                if end_time > end_date:
                    end_time = end_date
                
                if values:
                    val = random.choice(values)
                elif allow_numeric:
                    # Generate numeric value
                    val = round(random.uniform(min_value, max_value), 2)
                else:
                    # Original behavior: crash/error if no values available and not allowed to generate numeric
                    # We'll raise a clear error to break out
                    raise ValueError(f"No allowed values found for concept '{concept_name}' and numeric generation is disabled.")
                
                new_data.append(Record(
                    StartTime=current_time,
                    EndTime=end_time,
                    Value=str(val),
                    PatientID=patient_id,
                    ConceptName=concept_name
                ))
                
                # Random gap between 1 hour and 30 days
                gap_minutes = random.randint(60, 30 * 24 * 60)
                current_time = end_time + timedelta(minutes=gap_minutes)
                
        return new_data
