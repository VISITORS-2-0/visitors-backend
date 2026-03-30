from typing import List, Any
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, DataRequest, Record, IntervalSummary
from app.services.data_fetcher import csv_fetcher
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
        fetch_request = DataRequest(
            patients_list=request.patients_list,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        # 1. Fetch Data (Abstract)
        patient_events = csv_fetcher.fetch_data(fetch_request, abstract=True)
        
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
    def fetch_abstraction(request: DataRequest) -> VisitorResponse[List[Record]]:
        # 1. Fetch Data (Abstract)
        patient_events = csv_fetcher.fetch_data(request, abstract=True)
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)

    @staticmethod
    def fetch_raw_data(request: DataRequest) -> VisitorResponse[List[Record]]:
        # 1. Fetch Data (Raw)
        patient_events = csv_fetcher.fetch_data(request, abstract=False)
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)
