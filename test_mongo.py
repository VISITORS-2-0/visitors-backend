import os
import sys
from datetime import datetime

# Add root folder to sys.path so we can import app modules mapping correctly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.schemas import DataRequest
from app.services.data_fetcher import mongo_fetcher

def test_fetch_data():
    print("Testing connection to Mongo and querying syntax...")
    request = DataRequest(
        patients_list=["1000", "1001", "1"],
        concept_name="ALP",
        start_date=datetime(2000, 1, 1),
        end_date=datetime(2010, 1, 1)
    )
    
    try:
        # We try to fetch from abstract. 
        # This might return empty if the DB is empty or missing, but it validates the query.
        results = mongo_fetcher.fetch_data(request, abstract=True)
        print(f"Success! Fetched {len(results)} abstract records syntactically.")
        
        results = mongo_fetcher.fetch_data(request, abstract=False)
        print(f"Success! Fetched {len(results)} raw records syntactically.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_fetch_data()
