import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from app.models.schemas import Record, TransformationRequest

class IntervalTransformationService:
    @staticmethod
    def transform_to_intervals(events: List[Record], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, interval_str: str = 'ME', method: str = 'most_time_spent') -> List[Record]:
        
        if not events:
            return []

        # Convert list of Pydantic models to DataFrame
        data = [e.dict() for e in events]
        df = pd.DataFrame(data)
        
        # 1. Preprocessing: Ensure datetime and consistent timezone (convert to UTC)
        df['StartTime'] = pd.to_datetime(df['StartTime'], utc=True)
        df['EndTime'] = pd.to_datetime(df['EndTime'], utc=True)
        
        # 2. Define Global Time Grid
        if start_date and end_date:
            global_min = pd.to_datetime(start_date, utc=True)
            global_max = pd.to_datetime(end_date, utc=True)
        else:
            global_min = df['StartTime'].min().floor('D') 
            global_max = df['EndTime'].max().ceil('D')
        
        # Create the buckets (intervals)
        buckets_index = pd.date_range(start=global_min, end=global_max, freq=interval_str)
        buckets = list(buckets_index)
        
        # Ensure the first bucket covers the start of the data
        if not buckets or buckets[0] > global_min:
            buckets.insert(0, global_min)
            
        # Ensure the last bucket covers the end of the data
        if buckets[-1] < global_max:
            buckets.append(global_max)
            
        buckets = pd.DatetimeIndex(buckets)

        new_rows = []
        
        # Group by Patient and Concept
        grouped = df.groupby(['PatientID', 'ConceptName'])
        
        for (patient_id, concept_name), group in grouped:
            group = group.sort_values('StartTime')
            
            for i in range(len(buckets) - 1):
                bucket_start = buckets[i]
                bucket_end = buckets[i+1]
                
                # Filter rows that physically overlap with the current bucket
                relevant_rows = group[
                    (group['StartTime'] < bucket_end) & 
                    (group['EndTime'] > bucket_start)
                ].copy()
                
                representative_value = 'No Value'
                
                if not relevant_rows.empty:
                    # Clip start/end to stay within the bucket boundaries
                    relevant_rows['clip_start'] = relevant_rows['StartTime'].apply(lambda x: max(x, bucket_start))
                    relevant_rows['clip_end'] = relevant_rows['EndTime'].apply(lambda x: min(x, bucket_end))
                    
                    relevant_rows['duration'] = (relevant_rows['clip_end'] - relevant_rows['clip_start']).dt.total_seconds()
                    
                    # Sum duration per unique Value
                    durations = relevant_rows.groupby('Value')['duration'].sum()
                    
                    if method == 'most_time_spent':
                        if not durations.empty and durations.max() > 0:
                            representative_value = durations.idxmax()
                
                new_rows.append(Record(
                    StartTime=bucket_start,
                    EndTime=bucket_end,
                    Value=representative_value,
                    PatientID=patient_id,
                    ConceptName=concept_name
                ))
                
        return new_rows
