from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse, GenerationRequest
from app.services.generator import DataGeneratorService
from app.services.transformer import IntervalTransformationService
from app.services.summer import SummaryService

class MultiplePatientsAbstractionService:
    @staticmethod
    def run_flow(request: MultiplePatientsAbstractionRequest) -> SummaryResponse:
        # 1. Generate Data
        gen_request = GenerationRequest(
            num_patients=request.num_patients,
            values=request.values,
            concept_name=request.concept_name,
            start_year=request.start_year,
            end_year=request.end_year
        )
        # Using the public method which handles caching internally
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
