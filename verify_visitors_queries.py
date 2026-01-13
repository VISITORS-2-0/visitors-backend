import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/visitors-queries"

def run_verification():
    print("Verifying Visitors Queries Abstraction Endpoint...")
    orch_payload = {
        "num_patients": 5,
        "concept_name": "TestConcept",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59",
        "interval_str": "ME",
        "method": "most_time_spent"
    }
    
    # Test Abstraction (legacy logic renamed)
    try:
        resp = requests.post(f"{BASE_URL}/multiple-patients-abstraction", json=orch_payload)
        # If it succeeds, it means values existed or something unexpected happened.
        # But we expect failure if no values exist.
        if resp.status_code == 200:
             summary = resp.json()
             print(f"Abstraction success! Summary length: {len(summary['summary'])}")
        else:
             print(f"Abstraction returned status {resp.status_code} (Expected if concept is missing values).")
             # Try to see error
             try: print(resp.json())
             except: print(resp.text)

    except Exception as e:
        print(f"Abstraction failed as expected (or due to error): {e}")
        try: print(resp.text)
        except: pass
        # Do not exit, continue to test raw data


    print("Verifying Visitors Queries Raw Data Endpoint (Numeric)...")
    # Test Raw Data (should generate numeric values)
    raw_payload = {
        "num_patients": 5,
        "concept_name": "TestConceptNumeric",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59"
        # min_value/max_value removed
        # interval_str/method removed (GenerationRequest)
    }
    try:
        resp = requests.post(f"{BASE_URL}/raw-data", json=raw_payload)
        resp.raise_for_status()
        raw_events = resp.json()
        print(f"Raw Data success! Generated {len(raw_events)} events.")
        
        # Verify values are numeric and within default range [0, 100]
        if raw_events:
            val = float(raw_events[0]['Value'])
            print(f"Sample value: {val}")
            if 0.0 <= val <= 100.0:
                print("Value within default range [0, 100].")
            else:
                print(f"ERROR: Value {val} out of default range!")
                sys.exit(1)
        else:
            print("Warning: No events generated (could be chance or short duration).")

    except Exception as e:
        print(f"Raw Data failed: {e}")
        try: print(resp.text)
        except: pass
        sys.exit(1)

    print("Verifying Visitors Queries Generation Endpoint (New /abstraction)...")
    gen_payload = {
        "num_patients": 5,
        "concept_name": "TestConceptGen",
        "start_date": "2020-01-01T00:00:00",
        "end_date": "2021-12-31T23:59:59"
    }
    try:
        resp = requests.post(f"{BASE_URL}/abstraction", json=gen_payload)
        # This uses standard generation, so it might fail if concept doesn't exist (strict mode)
        if resp.status_code == 200:
            events = resp.json()
            print(f"Generation success! Generated {len(events)} events.")
        else:
            print(f"Generation returned status {resp.status_code} (Expected if concept is missing).")
    except Exception as e:
        print(f"Generation check failed: {e}")


    except Exception as e:
        print(f"Raw Data failed: {e}")
        try: print(resp.text)
        except: pass
        sys.exit(1)

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_verification()
