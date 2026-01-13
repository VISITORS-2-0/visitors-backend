import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def run_verification():
    print("Verifying Generation Endpoint...")
    gen_payload = {
        "num_patients": 5,
        "values": ["Normal", "High"],
        "concept_name": "TestConcept",
        "start_year": 2020,
        "end_year": 2021
    }
    try:
        resp = requests.post(f"{BASE_URL}/generate/", json=gen_payload)
        resp.raise_for_status()
        generated_data = resp.json()
        print(f"Generated {len(generated_data)} events.")
        if not generated_data:
            print("Error: No data generated")
            sys.exit(1)
    except Exception as e:
        print(f"Generation failed: {e}")
        sys.exit(1)

    print("Verifying Transformation Endpoint...")
    trans_payload = {
        "data": generated_data,
        "interval_str": "M",
        "method": "most_time_spent"
    }
    try:
        resp = requests.post(f"{BASE_URL}/transform/", json=trans_payload)
        resp.raise_for_status()
        intervals = resp.json()
        print(f"Transformed into {len(intervals)} intervals.")
    except Exception as e:
        print(f"Transformation failed: {e}")
        # print(resp.text)
        sys.exit(1)

    print("Verifying Multiple Patients Abstraction Endpoint...")
    orch_payload = {
        "num_patients": 5,
        "values": ["Normal", "High"],
        "concept_name": "TestConcept",
        "start_year": 2020,
        "end_year": 2021,
        "interval_str": "M",     # Valid Literal
        "method": "most_time_spent" # Valid Literal
    }
    try:
        resp = requests.post(f"{BASE_URL}/mult-patients-abstraction/", json=orch_payload)
        resp.raise_for_status()
        orch_summary = resp.json()
        print(f"Abstraction success! Generated summary with {len(orch_summary['summary'])} time steps.")
    except Exception as e:
        print(f"Abstraction failed: {e}")
        try: 
            print(resp.text)
        except: 
            pass
        sys.exit(1)

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_verification()
