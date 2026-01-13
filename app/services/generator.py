import random
from datetime import datetime, timedelta
from typing import List
from app.models.schemas import GenerationRequest, PatientEvent

class DataGeneratorService:
    @staticmethod
    def generate_data(request: GenerationRequest) -> List[PatientEvent]:
        new_data = []
        
        # Determine strict types for iteration to prevent validation errors
        num_patients: int = request.num_patients
        start_year: int = request.start_year
        end_year: int = request.end_year
        values: List[str] = request.values
        concept_name: str = request.concept_name

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
