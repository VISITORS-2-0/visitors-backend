import pandas as pd
from typing import List, Tuple
from datetime import datetime, timezone
from app.models.schemas import Record, RelativeTimeConfig, DataRequest, ReferenceConcept
from app.services.csv_data_fetcher import csv_fetcher
from app.services.generator import DataGeneratorService

class RelativeTimeService:
    ANCHOR_DATE = datetime(1970, 1, 1, tzinfo=timezone.utc)

    @staticmethod
    def _apply_delta(dt: datetime, val: int, unit: str) -> datetime:
        if unit == 'h':
            return dt + pd.DateOffset(hours=val)
        elif unit == 'd':
            return dt + pd.DateOffset(days=val)
        elif unit == 'w':
            return dt + pd.DateOffset(weeks=val)
        elif unit == 'm':
            return dt + pd.DateOffset(months=val)
        elif unit == 'y':
            return dt + pd.DateOffset(years=val)
        return dt

    @staticmethod
    def align_records_to_anchor(
        records: List[Record], 
        config: RelativeTimeConfig, 
        patients_list: List[str], 
        use_generated_data: bool = False,
        start_date: datetime = None,
        end_date: datetime = None,
        interval_str: str = "ME"
    ) -> Tuple[List[Record], datetime, datetime]:
        """
        Calculates patient-specific t_zero based on the reference concepts list, 
        shifts all primary records to align exactly onto the ANCHOR_DATE,
        and filters shifted records by the global relative bounds.
        """
        # Group by patient
        patient_ref_events = {}

        # 1. Fetch reference data for each concept in the list
        for ref_c in config.reference_concepts:
            ref_request = DataRequest(
                patients_list=patients_list,
                concept_name=ref_c.concept_name,
                start_date=start_date,
                end_date=end_date,
                use_generated_data=use_generated_data
            )
            
            if use_generated_data:
                ref_records = DataGeneratorService.generate_data(ref_request)
            else:
                # Try Abstract first (events, categorical abstractions).
                # If nothing is found, fall back to Raw (e.g. Anti_Platelets_Drugs, Visit, etc.)
                ref_records = csv_fetcher.fetch_data(ref_request, abstract=True)
                if not ref_records:
                    ref_records = csv_fetcher.fetch_data(ref_request, abstract=False)

            # Filter records per concept
            concept_patient_events = {}
            for r in ref_records:
                if ref_c.concept_value and r.Value != ref_c.concept_value:
                    continue
                if r.PatientID not in concept_patient_events:
                    concept_patient_events[r.PatientID] = []
                concept_patient_events[r.PatientID].append(r)

            # Fallback for generated data: if no events matched the value, just use all events of that concept
            if use_generated_data and ref_c.concept_value:
                for pid in patients_list:
                    pid_int = int(pid)
                    if pid_int not in concept_patient_events:
                        # Collect all generated events for this patient regardless of value
                        fallbacks = [r for r in ref_records if r.PatientID == pid_int]
                        if fallbacks:
                            concept_patient_events[pid_int] = fallbacks

            # Add these events to the accumulated list for each patient
            for pid, evs in concept_patient_events.items():
                if pid not in patient_ref_events:
                    patient_ref_events[pid] = []
                patient_ref_events[pid].extend(evs)
            
        # Calculate t_zero for each patient
        t_zeros = {}
        for pid, evs in patient_ref_events.items():
            evs.sort(key=lambda x: x.StartTime)
            try:
                target_ev = evs[config.occurrence_index]
                t_zeros[pid] = target_ev.StartTime
            except IndexError:
                # Patient doesn't have the occurrence at this index
                pass
                
        # 2. Shift primary records
        shifted_records = []
        for r in records:
            if r.PatientID not in t_zeros:
                continue # Exclude patient
                
            t_zero = t_zeros[r.PatientID]
            if t_zero.tzinfo is None:
                t_zero = t_zero.replace(tzinfo=timezone.utc)
                
            r_start = r.StartTime.replace(tzinfo=timezone.utc) if r.StartTime.tzinfo is None else r.StartTime
            r_end = r.EndTime.replace(tzinfo=timezone.utc) if r.EndTime.tzinfo is None else r.EndTime
            
            shift = RelativeTimeService.ANCHOR_DATE - t_zero
            
            new_start = r_start + shift
            new_end = r_end + shift
            
            shifted_records.append(Record(
                StartTime=new_start,
                EndTime=new_end,
                Value=r.Value,
                PatientID=r.PatientID,
                ConceptName=r.ConceptName
            ))
            
        # 3. Filter bounds based on start_delta and end_delta around ANCHOR_DATE
        unit_map = {
            'D': 'd',
            'W-SUN': 'w',
            'ME': 'm',
            'YE': 'y'
        }
        unit = unit_map.get(interval_str, 'm')

        global_start = RelativeTimeService._apply_delta(RelativeTimeService.ANCHOR_DATE, config.start_delta, unit)
        global_end = RelativeTimeService._apply_delta(RelativeTimeService.ANCHOR_DATE, config.end_delta, unit)
        
        # Ensure correct temporal ordering for Pandas
        global_start_pd = pd.to_datetime(global_start, utc=True)
        global_end_pd = pd.to_datetime(global_end, utc=True)
        
        final_records = []
        for r in shifted_records:
            r_start_pd = pd.to_datetime(r.StartTime, utc=True)
            r_end_pd = pd.to_datetime(r.EndTime, utc=True)
            
            if r_end_pd < global_start_pd or r_start_pd > global_end_pd:
                continue
            final_records.append(r)
            
        return final_records, global_start, global_end
