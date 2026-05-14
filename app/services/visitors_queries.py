from typing import List, Any
from fastapi import HTTPException
from app.models.schemas import MultiplePatientsAbstractionRequest, VisitorResponse, DataRequest, Record, IntervalSummary, MultiplePatientsNumericAbstractionRequest, NumericRange
from app.services.csv_data_fetcher import csv_fetcher
from app.services.generator import DataGeneratorService
from app.services.transformer import IntervalTransformationService
from app.services.summer import SummaryService
from app.core.cache_utils import db_cache
from app.services.concept_manager import concept_manager_instance
from app.models.concept import TAKEntity
from app.services.relative_time_service import RelativeTimeService

class VisitorsQueriesService:
    @staticmethod
    def _build_visitor_response(result: Any, concept_name: str) -> VisitorResponse:
        concept_def = None
        try:
             entity = concept_manager_instance.get_entity_by_name(concept_name)
             if entity:
                 concept_def = TAKEntity.model_validate(entity).model_dump(exclude_none=True)
        except Exception as e:
             print(f"Failed to fetch concept data: {e}")
        return VisitorResponse(result=result, concept_data=concept_def)

    @staticmethod
    def _validate_ranges(ranges: List[NumericRange], concept_min: float, concept_max: float):
        if not ranges:
            return
        sorted_ranges = sorted(ranges, key=lambda r: r.min)
        
        print(sorted_ranges)
        print(concept_min)
        print(concept_max)
        if sorted_ranges[0].min != concept_min:
            raise HTTPException(status_code=400, detail=f"Ranges must start at concept min ({concept_min}). Found: {sorted_ranges[0].min}")
        if sorted_ranges[-1].max != concept_max:
            raise HTTPException(status_code=400, detail=f"Ranges must end at concept max ({concept_max}). Found: {sorted_ranges[-1].max}")
        
        for i in range(len(sorted_ranges) - 1):
            if sorted_ranges[i].max != sorted_ranges[i+1].min:
                raise HTTPException(status_code=400, detail=f"Ranges must be continuous with no gaps. Found gap/overlap between {sorted_ranges[i].max} and {sorted_ranges[i+1].min}")

    @staticmethod
    def _generate_default_ranges(concept_min: float, concept_max: float, num_partitions: int = 4) -> List[NumericRange]:
        ranges = []
        step = (concept_max - concept_min) / num_partitions
        for i in range(num_partitions):
            current_min = concept_min + i * step
            current_max = concept_min + (i + 1) * step if i < num_partitions - 1 else concept_max
            ranges.append(NumericRange(min=current_min, max=current_max))
        return ranges

    @staticmethod
    def _assign_ranges_to_records(records: List[Record], ranges: List[NumericRange]) -> List[Record]:
        if not records or not ranges:
            return records
            
        sorted_ranges = sorted(ranges, key=lambda r: r.min)
        for record in records:
            try:
                val = float(record.Value)
            except ValueError:
                record.Value = "Out of Range"
                continue
                
            assigned = False
            for i, rng in enumerate(sorted_ranges):
                is_last_range = (i == len(sorted_ranges) - 1)
                
                if (rng.min <= val < rng.max) or (is_last_range and val == rng.max):
                    # Keep formatted consistently
                    record.Value = f"{rng.min}-{rng.max}"
                    assigned = True
                    break
                    
            if not assigned:
                record.Value = "Out of Range"
                
        return records

    @staticmethod
    @db_cache
    def create_multiple_patients_numeric_abstraction(request: MultiplePatientsNumericAbstractionRequest) -> VisitorResponse[List[IntervalSummary]]:
        concept = concept_manager_instance.get_entity_by_name(request.concept_name)
        concept_min = getattr(concept, "min", None)
        if concept_min is None: concept_min = 0.0
        concept_max = getattr(concept, "max", None)
        if concept_max is None: concept_max = 100.0

        if request.ranges:
            print(request)
            VisitorsQueriesService._validate_ranges(request.ranges, concept_min, concept_max)
            ranges = request.ranges
        else:
            ranges = VisitorsQueriesService._generate_default_ranges(concept_min, concept_max)
            
        gen_request = DataRequest(
            patients_list=request.patients_list,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date,
            use_generated_data=request.use_generated_data
        )
        
        if request.use_generated_data:
            patient_events = DataGeneratorService.generate_numeric_data(gen_request)
        else:
            patient_events = csv_fetcher.fetch_data(gen_request, abstract=False)
        patient_events = VisitorsQueriesService._assign_ranges_to_records(patient_events, ranges)
        
        if getattr(request, 'relative_time', None):
            patient_events, request.start_date, request.end_date = RelativeTimeService.align_records_to_anchor(
                patient_events, request.relative_time, request.patients_list, request.use_generated_data, request.start_date, request.end_date
            )
        
        intervals = IntervalTransformationService.transform_to_intervals(
            events=patient_events,
            start_date=request.start_date,
            end_date=request.end_date,
            interval_str=request.interval_str,
            method=request.method
        )
        
        summary_list = SummaryService.summarize_intervals(intervals)
        response = VisitorsQueriesService._build_visitor_response(summary_list, request.concept_name)
        
        if response.concept_data is not None:
            response.concept_data["values"] = [f"{rng.min}-{rng.max}" for rng in ranges]
            
        return response

    @staticmethod
    @db_cache
    def create_multiple_patients_abstraction(request: MultiplePatientsAbstractionRequest) -> VisitorResponse[List[IntervalSummary]]:
        # Compatibility adapter for old request model
        gen_request = DataRequest(
            patients_list=request.patients_list,
            concept_name=request.concept_name,
            start_date=request.start_date,
            end_date=request.end_date,
            use_generated_data=request.use_generated_data
        )
        # 1. Generate Data (Strict/Standard)
        if request.use_generated_data:
            patient_events = DataGeneratorService.generate_data(gen_request)
        else:
            patient_events = csv_fetcher.fetch_data(gen_request, abstract=True)
            
        if getattr(request, 'relative_time', None):
            patient_events, request.start_date, request.end_date = RelativeTimeService.align_records_to_anchor(
                patient_events, request.relative_time, request.patients_list, request.use_generated_data, request.start_date, request.end_date
            )
        
        # 2. Transform Data
        intervals = IntervalTransformationService.transform_to_intervals(
            events=patient_events,
            start_date=request.start_date,
            end_date=request.end_date,
            interval_str=request.interval_str,
            method=request.method
        )
        
        # 3. Summarize Data
        summary_list = SummaryService.summarize_intervals(intervals)
        
        return VisitorsQueriesService._build_visitor_response(summary_list, request.concept_name)

    @staticmethod
    def generate_abstraction(request: DataRequest) -> VisitorResponse[List[Record]]:
        # 1. Generate Data (Strict)
        if request.use_generated_data:
            patient_events = DataGeneratorService.generate_data(request)
        else:
            patient_events = csv_fetcher.fetch_data(request, abstract=True)
            
        if getattr(request, 'relative_time', None):
            patient_events, request.start_date, request.end_date = RelativeTimeService.align_records_to_anchor(
                patient_events, request.relative_time, request.patients_list, request.use_generated_data, request.start_date, request.end_date
            )
            
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)

    @staticmethod
    def generate_raw_data(request: DataRequest) -> VisitorResponse[List[Record]]:
        # 1. Generate Data (Numeric)
        if request.use_generated_data:
            patient_events = DataGeneratorService.generate_numeric_data(request)
        else:
            patient_events = csv_fetcher.fetch_data(request, abstract=False)
            
        if getattr(request, 'relative_time', None):
            patient_events, request.start_date, request.end_date = RelativeTimeService.align_records_to_anchor(
                patient_events, request.relative_time, request.patients_list, request.use_generated_data, request.start_date, request.end_date
            )
            
        return VisitorsQueriesService._build_visitor_response(patient_events, request.concept_name)
