import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models.schemas import Record

class QueriesEndpointTests(unittest.TestCase):
    def setUp(self):
        from app.services.concept_manager import concept_manager_instance
        concept_manager_instance.init_entities()
        self.client = TestClient(app)

    @patch("app.services.csv_data_fetcher.CSVDataFetcher.fetch_data")
    def test_abstraction_endpoint_with_relative_time(self, mock_fetch):
        def side_effect(request, abstract=True):
            if request.concept_name == "Admission":
                return [Record(
                    StartTime="2020-01-01T00:00:00",
                    EndTime="2020-01-01T00:00:00",
                    Value="Emergency",
                    PatientID=1,
                    ConceptName="Admission"
                )]
            elif request.concept_name == "Sex":
                return [Record(
                    StartTime="2020-01-01T12:00:00",
                    EndTime="2020-01-01T12:00:00",
                    Value="1",
                    PatientID=1,
                    ConceptName="Sex"
                )]
            return []
        
        mock_fetch.side_effect = side_effect

        payload = {
            "patients_list": ["1"],
            "concept_name": "Sex",
            "use_generated_data": False,
            "interval_str": "D",
            "relative_time": {
                "reference_concepts": [
                    {
                        "concept_name": "Admission",
                        "concept_value": "Emergency"
                    }
                ],
                "occurrence_index": 0,
                "start_delta": -1,
                "end_delta": 2
            }
        }

        response = self.client.post("/api/v1/visitors-queries/abstraction", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertEqual(len(data["result"]), 1)
        # Shifted value:
        # t_zero is 2020-01-01T00:00:00
        # primary is 2020-01-01T12:00:00 (12 hours later)
        # ANCHOR_DATE is 1970-01-01T00:00:00+00:00.
        # Shifted: 1970-01-01T12:00:00+00:00
        self.assertTrue(data["result"][0]["StartTime"].startswith("1970-01-01T12:00:00"))

    def test_validation_error_when_reference_concepts_empty(self):
        # reference_concepts must not be empty
        payload = {
            "patients_list": ["1"],
            "concept_name": "Sex",
            "use_generated_data": False,
            "interval_str": "D",
            "relative_time": {
                "reference_concepts": [],
                "occurrence_index": 0,
                "start_delta": -1,
                "end_delta": 2
            }
        }
        response = self.client.post("/api/v1/visitors-queries/abstraction", json=payload)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity

if __name__ == "__main__":
    unittest.main()
