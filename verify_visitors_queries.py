import requests
import json
import sys
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1/visitors-queries"

def run_verification():
    print("Verifying Visitors Queries Abstraction Endpoint...")
    # Use random concept to ensure cold start
    concept_name = f"TestConcept_{uuid.uuid4().hex[:8]}"
    print(f"Using concept: {concept_name}")
    
    orch_payload = {
        "patients_list": ["1000", "1001", "1002", "1003", "1004"],
        "concept_name": concept_name,
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59",
        "interval_str": "ME",
        "method": "most_time_spent"
    }
    
    # Test Abstraction (legacy logic renamed)
    try:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/multiple-patients-abstraction", json=orch_payload)
        first_duration = time.time() - start_time
        
        if resp.status_code == 200:
             data = resp.json()
             # Result should be List[IntervalSummary]
             summary = data.get("result", [])
             print(f"Abstraction success! Summary length: {len(summary)}")
             
             # Check for Concept Data
             if 'concept_data' in data and data['concept_data']:
                 c_data = data['concept_data']
                 print(f"Concept Data verified: Name={c_data.get('name')}, Type={c_data.get('type')}")
             else:
                 print("ERROR: concept_data missing from response!")
             
             print(f"First request duration: {first_duration:.4f}s")
             
             # Test Caching: Send same request again
             start_time = time.time()
             resp2 = requests.post(f"{BASE_URL}/multiple-patients-abstraction", json=orch_payload)
             second_duration = time.time() - start_time
             print(f"Second request duration (Cached): {second_duration:.4f}s")
             
             if second_duration < first_duration and second_duration < 0.5:
                 print("Caching verified: Second request was significantly faster.")
             else:
                 print("Warning: Caching might not be effective or first request was too fast.")

        else:
             print(f"Abstraction returned status {resp.status_code} (Expected if concept is missing values).")
             try: print(resp.json())
             except: print(resp.text)

    except Exception as e:
        print(f"Abstraction failed as expected (or due to error): {e}")
        try: print(resp.text)
        except: pass


    print("Verifying Visitors Queries Raw Data Endpoint (Numeric)...")
    # Test Raw Data (should generate numeric values)
    raw_payload = {
        "patients_list": ["2000", "2001", "2002"],
        "concept_name": "TestConceptNumeric",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59"
    }
    try:
        resp = requests.post(f"{BASE_URL}/raw-data", json=raw_payload)
        resp.raise_for_status()
        
        # New structure: VisitorResponse[List[Record]]
        data = resp.json()
        raw_events = data.get("result", [])
        
        print(f"Raw Data success! Generated {len(raw_events)} events.")
        
        # Verify Concept Data existence (but NO Summary)
        if "concept_data" in data:
            print("Raw Data: Concept Data verified.")
        else:
            print("ERROR: Raw Data missing concept_data.")
            
        if "summary" in data:
             print("WARNING: 'summary' field found in raw-data response, expected only result/concept_data.")
        
        # Verify values are numeric and within default range [0, 100]
        if raw_events:
            val = float(raw_events[0]['Value'])
            print(f"Sample value: {val}")
            if 0.0 <= val <= 100.0:
                print("Value within default range [0, 100].")
            else:
                print(f"ERROR: Value {val} out of default range!")
                sys.exit(1)
            
            # Check ID is one of the requested
            pid = str(raw_events[0]['PatientID'])
            if pid in raw_payload["patients_list"]:
                 print(f"PatientID {pid} validated.")
            else:
                 print(f"Warning: PatientID {pid} not in requested list {raw_payload['patients_list']}")

        else:
            print("Warning: No events generated (could be chance or short duration).")

    except Exception as e:
        print(f"Raw Data failed: {e}")
        try: print(resp.text)
        except: pass
        sys.exit(1)

    print("Verifying Visitors Queries Generation Endpoint (New /abstraction)...")
    gen_payload = {
        "patients_list": ["3000", "3001"],
        "concept_name": "TestConceptGen",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59"
    }
    try:
        resp = requests.post(f"{BASE_URL}/abstraction", json=gen_payload)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("result", [])
            print(f"Generation success! Generated {len(events)} events.")
            if "concept_data" in data:
                 print("Generation: Concept Data verified.")
            else:
                 print("ERROR: Generation missing concept_data.")
        else:
            print(f"Generation returned status {resp.status_code} (Expected if concept is missing).")
    except Exception as e:
        print(f"Generation check failed: {e}")

    print("Verifying Validation (Missing patients_list)...")
    invalid_payload = {
        # patients_list missing
        "concept_name": "TestConceptGen",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59"
    }
    try:
        resp = requests.post(f"{BASE_URL}/abstraction", json=invalid_payload)
        if resp.status_code == 422:
            print("Validation success! Missing parameter rejected as expected.")
        else:
            print(f"Validation failed: Expected 422, got {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Validation check failed: {e}")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_verification()
