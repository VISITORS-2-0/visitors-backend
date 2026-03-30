from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from app.models.schemas import DataRequest, Record
from pathlib import Path
from app.core.config import settings

class DataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, request: DataRequest, abstract: bool = True) -> List[Record]:
        """
        Fetch data based on the request.
        :param abstract: Whether to fetch from abstract store or raw store.
        """
        pass

class CsvDataFetcher(DataFetcher):
    def __init__(self):
        pass

    def _get_patient_dataframe(self, patient_id: int, abstract: bool) -> pd.DataFrame:
        file_suffix = "Abstract" if abstract else "Raw"
        file_path = Path(settings.CSV_DATA_DIR) / f"ID_{patient_id}_{file_suffix}.csv"
        
        if not file_path.exists():
            return pd.DataFrame()
            
        df = pd.read_csv(file_path, parse_dates=['StartTime', 'EndTime'])
        return df

    def fetch_data(self, request: DataRequest, abstract: bool = True) -> List[Record]:
        try:
            patient_ids = [int(p) for p in request.patients_list]
        except ValueError:
            patient_ids = request.patients_list

        dfs = []
        for pid in patient_ids:
            df_patient = self._get_patient_dataframe(pid, abstract)
            if not df_patient.empty:
                dfs.append(df_patient)
                
        if not dfs:
            return []
            
        df = pd.concat(dfs, ignore_index=True)

        start_ts = pd.to_datetime(request.start_date, utc=True)
        end_ts = pd.to_datetime(request.end_date, utc=True)

        if 'ConceptName' not in df.columns or 'PatientID' not in df.columns or 'StartTime' not in df.columns:
            return []

        mask = (
            (df['ConceptName'] == request.concept_name) &
            (df['PatientID'].isin(patient_ids)) &
            (pd.to_datetime(df['StartTime'], utc=True) >= start_ts) &
            (pd.to_datetime(df['StartTime'], utc=True) <= end_ts)
        )

        filtered_df = df[mask]

        results = []
        for _, row in filtered_df.iterrows():
            results.append(Record(
                StartTime=row['StartTime'],
                EndTime=row['EndTime'],
                Value=str(row['Value']),
                PatientID=int(row['PatientID']),
                ConceptName=str(row['ConceptName'])
            ))
            
        return results

# Singleton instance to be used by services
csv_fetcher = CsvDataFetcher()
