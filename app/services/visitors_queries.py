from typing import List, Any
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, GenerationRequest, Record, IntervalSummary
from app.services.generator import DataGeneratorService
from app.services.transformer import IntervalTransformationService
from app.services.summer import SummaryService
from app.core.cache_utils import db_cache
from app.services.concept_manager import ConceptManager

# ... (imports)

class VisitorsQueriesService:
    @staticmethod
    def _build_visitor_response(result: Any, concept_name: str) -> VisitorResponse:
        concept_def = None
        try:
             concept_def = ConceptManager.get_or_create_concept(concept_name)
        except Exception as e:
             print(f"Failed to fetch concept data: {e}")
        return VisitorResponse(result=result, concept_data=concept_def)

    @staticmethod
    @db_cache
    def create_multiple_patients_abstraction(request: MultiplePatientsAbstractionRequest) -> VisitorResponse[List[IntervalSummary]]:
        # Compatibility adapter for old request model
        gen_request = GenerationRequest(
            patients_list=request.patients_list,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        # 1. Generate Data (Strict/Standard)
        patient_events = DataGeneratorService.generate_data(gen_request)
        
        # 2. Transform Data
        intervals = IntervalTransformationService.transform_to_intervals(
            events=patient_events,
            interval_str=request.interval_str,
            method=request.method
        )
        
        # 3. Summarize Data
        summary_list = SummaryService.summarize_intervals(intervals)
        
        return VisitorsQueriesService._build_visitor_response(summary_list, request.concept_name)

    @staticmethod
    def generate_abstraction(request: GenerationRequest) -> VisitorResponse[List[Record]]:
        # 1. Generate Data (Strict)
        patient_events = DataGeneratorService.generate_data(request)
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)

    @staticmethod
    def generate_raw_data(request: GenerationRequest) -> VisitorResponse[List[Record]]:
        # 1. Generate Data (Numeric)
        patient_events = DataGeneratorService.generate_numeric_data(request)
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)
