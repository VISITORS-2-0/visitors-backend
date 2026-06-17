import os
import csv
from datetime import datetime
from typing import List
from app.models.schemas import DataRequest, Record
from app.core.config import settings

class CSVDataFetcher:
    def __init__(self, data_dir: str = settings.CSV_DATA_DIR):
        self.data_dir = data_dir

    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        dt_str = dt_str.strip()
        if '.' in dt_str:
            date_part, frac_part = dt_str.split('.', 1)
            # Python datetime supports up to 6 digits (microseconds). Truncate 7-digit strings.
            frac_part = frac_part[:6]
            dt_str = f"{date_part}.{frac_part}"
            try:
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.fromisoformat(dt_str)

    def fetch_data(self, request: DataRequest, abstract: bool = True) -> List[Record]:
        results = []
        
        file_suffixes = ["Abstract", "Raw"]
        for patient_id in request.patients_list:
            for file_suffix in file_suffixes:
                file_path = os.path.join(self.data_dir, f"ID_{patient_id}_{file_suffix}.csv")
                if not os.path.exists(file_path):
                    continue
                
                with open(file_path, mode='r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["ConceptName"] != request.concept_name:
                            continue
                        
                        try:
                            start_time = self.parse_datetime(row["StartTime"])
                            end_time = self.parse_datetime(row["EndTime"])
                        except Exception as e:
                            continue
                            
                        if not getattr(request, 'relative_time', None):
                            if request.start_date and end_time < request.start_date:
                                continue
                            if request.end_date and start_time > request.end_date:
                                continue
                            
                        results.append(Record(
                            StartTime=start_time,
                            EndTime=end_time,
                            Value=row["Value"],
                            PatientID=int(row["PatientID"]),
                            ConceptName=row["ConceptName"]
                        ))
                    
        return results

csv_fetcher = CSVDataFetcher()
