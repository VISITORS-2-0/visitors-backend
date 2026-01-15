import pandas as pd
from typing import List
from app.models.schemas import Record, IntervalSummary

class SummaryService:
    @staticmethod
    def summarize_intervals(intervals: List[Record]) -> List[IntervalSummary]:
        if not intervals:
            return []

        data = [i.dict() for i in intervals]
        df = pd.DataFrame(data)
        
        # 1. Identify all unique values
        all_possible_values = sorted(df['Value'].dropna().unique())
        if 'No Value' not in all_possible_values:
            all_possible_values.append('No Value')
            
        # 2. Group by time interval and concept
        # Note: We group by StartTime, EndTime, ConceptName
        grouped = df.groupby(['StartTime', 'EndTime', 'ConceptName'])
        
        results = []
        
        for (start, end, concept), group in grouped:
            current_counts = group['Value'].value_counts().to_dict()
            
            # Initialize with 0s
            complete_counts = {val: 0 for val in all_possible_values}
            complete_counts.update(current_counts)
            
            total_patients = sum(complete_counts.values())
            
            results.append(IntervalSummary(
                StartTime=start,
                EndTime=end,
                ConceptName=concept,
                Value_Dict=complete_counts,
                TotalPatientsWithData=total_patients
            ))
            
        return results
