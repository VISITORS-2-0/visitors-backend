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
        
        freq = interval_str
        if interval_str == 'ME':
            freq = 'MS'
            # Align global_min to the start of the month
            global_min = global_min.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Align global_max to the start of the next month if not already a month start
            is_month_start = (global_max.day == 1 and global_max.hour == 0 and global_max.minute == 0 and global_max.second == 0 and global_max.microsecond == 0)
            if not is_month_start:
                if global_max.month == 12:
                    global_max = global_max.replace(year=global_max.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                else:
                    global_max = global_max.replace(month=global_max.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif interval_str == 'YE':
            freq = 'YS'
            # Align global_min to the start of the year
            global_min = global_min.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            # Align global_max to the start of the next year if not already a year start
            is_year_start = (global_max.month == 1 and global_max.day == 1 and global_max.hour == 0 and global_max.minute == 0 and global_max.second == 0 and global_max.microsecond == 0)
            if not is_year_start:
                global_max = global_max.replace(year=global_max.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # Create the buckets (intervals)
        buckets_index = pd.date_range(start=global_min, end=global_max, freq=freq)
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
                
                # Interval overlaps if:
                # 1. It has duration (StartTime < EndTime) and overlaps with (bucket_start, bucket_end)
                # 2. It is a point event (StartTime == EndTime) and falls in [bucket_start, bucket_end)
                is_point = group['StartTime'] == group['EndTime']
                overlaps_interval = (group['StartTime'] < bucket_end) & (group['EndTime'] > bucket_start)
                is_point_in_bucket = is_point & (group['StartTime'] >= bucket_start) & (group['StartTime'] < bucket_end)
                
                relevant_rows = group[overlaps_interval | is_point_in_bucket].copy()
                
                representative_value = 'No Value'
                
                if not relevant_rows.empty:
                    # Clip start/end to stay within the bucket boundaries
                    relevant_rows['clip_start'] = relevant_rows['StartTime'].apply(lambda x: max(x, bucket_start))
                    relevant_rows['clip_end'] = relevant_rows['EndTime'].apply(lambda x: min(x, bucket_end))
                    
                    relevant_rows['duration'] = (relevant_rows['clip_end'] - relevant_rows['clip_start']).dt.total_seconds()
                    
                    # Sum duration per unique Value
                    durations = relevant_rows.groupby('Value')['duration'].sum()
                    
                    if method == 'most_time_spent':
                        if not durations.empty:
                            if durations.max() > 0:
                                representative_value = durations.idxmax()
                            else:
                                # They are point events (duration == 0). Pick the most frequent value.
                                value_counts = relevant_rows['Value'].value_counts()
                                if not value_counts.empty:
                                    representative_value = value_counts.idxmax()
                
                new_rows.append(Record(
                    StartTime=bucket_start,
                    EndTime=bucket_end,
                    Value=representative_value,
                    PatientID=patient_id,
                    ConceptName=concept_name
                ))
                
        return new_rows
