import sys
import os
from datetime import datetime
from app.models.schemas import GenerationRequest, PatientEvent
from app.services.visitors_queries import VisitorsQueriesService
from app.services.generator import DataGeneratorService

# Mock DB session if needed or rely on existing (sqlite)
# Assuming run from root

print("Testing generate_raw_data...")
req = GenerationRequest(
    patients_list=["9999"],
    concept_name="DebugConcept",
    start_date=datetime(2020,1,1),
    end_date=datetime(2021,1,1)
)

try:
    # 1. Generate events
    events = DataGeneratorService.generate_numeric_data(req)
    print(f"Generated {len(events)} events")
    
    # 2. Build response
    resp = VisitorsQueriesService._build_response(events, req)
    print("Response built successfully")
    print(f"Summary items: {len(resp.summary)}")
    print(f"Concept data: {resp.concept_data}")

except Exception as e:
    print(f"Error caught: {e}")
    import traceback
    traceback.print_exc()

print("Test Complete")
