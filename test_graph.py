import sys
import json
from datetime import datetime
from app.models.schemas import MultiplePatientsAbstractionRequest
from app.services.visitors_queries import VisitorsQueriesService

def test_fetch_state():
    print("Testing Blood_Pressure_Systole_Level_State graph output...")
    request = MultiplePatientsAbstractionRequest(
        patients_list=["1"],
        concept_name="Blood_Pressure_Systole_Level_State",
        start_date=datetime(2007, 1, 1),
        end_date=datetime(2015, 12, 31),
        interval_str="ME",
        method="most_time_spent"
    )
    
    try:
        response = VisitorsQueriesService.create_multiple_patients_abstraction(request)
        print("Concept Data:")
        print(response.concept_data.model_dump_json(indent=2) if response.concept_data else "None")
        print("\nSummary Data Length:", len(response.result))
        for i, res in enumerate(response.result):
            print(f"[{i}]:", res.model_dump_json(indent=2))
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_fetch_state()
