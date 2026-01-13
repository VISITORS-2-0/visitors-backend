from typing import List
from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse, GenerationRequest, PatientEvent
from app.services.generator import DataGeneratorService
from app.services.transformer import IntervalTransformationService
from app.services.summer import SummaryService

# ... (imports)

class VisitorsQueriesService:
    @staticmethod
    def run_flow(request: MultiplePatientsAbstractionRequest) -> SummaryResponse:
        # 1. Generate Data
        gen_request = GenerationRequest(
            num_patients=request.num_patients,
            # values removed
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date,
            min_value=request.min_value,
            max_value=request.max_value
        )
        # Pass DB session
        patient_events = DataGeneratorService.generate_data(gen_request)
        
        # 2. Transform Data
        # We pass the list of values directly, transformation service converts to DF internally
        intervals = IntervalTransformationService.transform_to_intervals(
            events=patient_events,
            interval_str=request.interval_str,
            method=request.method
        )
        
        # 3. Summarize Data
        summary_response = SummaryService.summarize_intervals(intervals)
        
        return summary_response

    @staticmethod
    def generate_raw_data(request: MultiplePatientsAbstractionRequest) -> List[PatientEvent]:
        # 1. Generate Data
        gen_request = GenerationRequest(
            num_patients=request.num_patients,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date,
            min_value=request.min_value,
            max_value=request.max_value
        )
        return DataGeneratorService.generate_numeric_data(gen_request)
