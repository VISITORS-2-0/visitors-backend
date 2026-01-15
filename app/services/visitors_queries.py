from typing import List
from app.models.schemas import MultiplePatientsAbstractionRequest, SummaryResponse, GenerationRequest, PatientEvent
from app.services.generator import DataGeneratorService
from app.services.transformer import IntervalTransformationService
from app.services.summer import SummaryService
from app.core.cache_utils import db_cache
from app.services.concept_manager import ConceptManager

# ... (imports)

class VisitorsQueriesService:
    @staticmethod
    @db_cache
    def _build_response(events: List[PatientEvent], request: GenerationRequest) -> SummaryResponse:
        # 2. Transform Data
        intervals = IntervalTransformationService.transform_to_intervals(
            events=events,
            interval_str=request.interval_str,
            method=request.method
        )
        
        # 3. Summarize Data
        summary_response = SummaryService.summarize_intervals(intervals)

        # 4. Enrich with Concept Data and Raw Events
        summary_response.events = events
        try:
             concept_def = ConceptManager.get_or_create_concept(request.concept_name)
             summary_response.concept_data = concept_def
        except Exception as e:
             print(f"Failed to fetch concept data: {e}")
        
        return summary_response

    @staticmethod
    @db_cache
    def run_flow(request: MultiplePatientsAbstractionRequest) -> SummaryResponse:
        # Compatibility adapter for old request model
        gen_request = GenerationRequest(
            patients_list=request.patients_list,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date,
            interval_str=request.interval_str,
            method=request.method
        )
        # 1. Generate Data (Strict/Standard)
        patient_events = DataGeneratorService.generate_data(gen_request)
        return VisitorsQueriesService._build_response(patient_events, gen_request)

    @staticmethod
    def generate_abstraction(request: GenerationRequest) -> SummaryResponse:
        # 1. Generate Data (Strict)
        patient_events = DataGeneratorService.generate_data(request)
        return VisitorsQueriesService._build_response(patient_events, request)

    @staticmethod
    def generate_raw_data(request: GenerationRequest) -> SummaryResponse:
        # 1. Generate Data (Numeric)
        patient_events = DataGeneratorService.generate_numeric_data(request)
        return VisitorsQueriesService._build_response(patient_events, request)
