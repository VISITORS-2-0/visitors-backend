import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from app.models.schemas import Record, RelativeTimeConfig, RelativeTimeDelta, ReferenceConcept
from app.services.relative_time_service import RelativeTimeService

class RelativeTimeServiceTests(unittest.TestCase):
    @patch("app.services.relative_time_service.csv_fetcher.fetch_data")
    def test_align_records_multiple_concepts(self, mock_fetch):
        # We have 3 concepts to match:
        # 1. ConceptA with value ValA
        # 2. ConceptB with no value (any value is accepted)
        # 3. ConceptC with value ValC
        
        # When fetching concept A, return records for patient 1:
        # Time: 2020-01-02
        record_a1 = Record(
            StartTime=datetime(2020, 1, 2),
            EndTime=datetime(2020, 1, 2),
            Value="ValA",
            PatientID=1,
            ConceptName="ConceptA"
        )
        record_a2 = Record( # incorrect value, should be filtered out
            StartTime=datetime(2020, 1, 1),
            EndTime=datetime(2020, 1, 1),
            Value="WrongVal",
            PatientID=1,
            ConceptName="ConceptA"
        )
        
        # When fetching concept B, return one record for patient 1:
        # Time: 2020-01-03
        record_b = Record(
            StartTime=datetime(2020, 1, 3),
            EndTime=datetime(2020, 1, 3),
            Value="AnyVal",
            PatientID=1,
            ConceptName="ConceptB"
        )
        
        # When fetching concept C, return one record for patient 1:
        # Time: 2020-01-01
        record_c = Record(
            StartTime=datetime(2020, 1, 1),
            EndTime=datetime(2020, 1, 1),
            Value="ValC",
            PatientID=1,
            ConceptName="ConceptC"
        )
        
        # Mock fetch_data based on requested concept_name
        def side_effect(request, abstract=True):
            if request.concept_name == "ConceptA":
                return [record_a1, record_a2]
            elif request.concept_name == "ConceptB":
                return [record_b]
            elif request.concept_name == "ConceptC":
                return [record_c]
            return []
        
        mock_fetch.side_effect = side_effect
        
        # Config:
        # reference_concepts: ConceptA (ValA), ConceptB (no val), ConceptC (ValC)
        # occurrence_index: 0 (the earliest event)
        # start_delta: -1d, end_delta: 2d
        config = RelativeTimeConfig(
            reference_concepts=[
                ReferenceConcept(concept_name="ConceptA", concept_value="ValA"),
                ReferenceConcept(concept_name="ConceptB"),
                ReferenceConcept(concept_name="ConceptC", concept_value="ValC")
            ],
            occurrence_index=0,
            start_delta=RelativeTimeDelta(value=-1, unit="d"),
            end_delta=RelativeTimeDelta(value=2, unit="d")
        )
        
        # Primary records to shift:
        # Record 1: at 2020-01-02 12:00:00 (1.5 days after t_zero, should stay in range)
        # Record 2: at 2020-01-05 (4 days after t_zero, should be filtered out)
        primary_records = [
            Record(
                StartTime=datetime(2020, 1, 2, 12, 0, 0),
                EndTime=datetime(2020, 1, 2, 12, 0, 0),
                Value="Primary1",
                PatientID=1,
                ConceptName="Primary"
            ),
            Record(
                StartTime=datetime(2020, 1, 5),
                EndTime=datetime(2020, 1, 5),
                Value="Primary2",
                PatientID=1,
                ConceptName="Primary"
            )
        ]
        
        # Sorted candidate reference events:
        # 1. ConceptC (ValC) at 2020-01-01
        # 2. ConceptA (ValA) at 2020-01-02
        # 3. ConceptB (AnyVal) at 2020-01-03
        # Since occurrence_index = 0, t_zero should be 2020-01-01.
        
        shifted, g_start, g_end = RelativeTimeService.align_records_to_anchor(
            records=primary_records,
            config=config,
            patients_list=["1"],
            use_generated_data=False
        )
        
        # Verify:
        # t_zero is 2020-01-01.
        # ANCHOR_DATE is 1970-01-01 00:00:00 UTC.
        # Shift is 1970-01-01 - 2020-01-01.
        # Record 1 (2020-01-02 12:00:00) shifted: 1970-01-02 12:00:00 UTC.
        # Record 2 (2020-01-05) shifted: 1970-01-05 UTC.
        # window is [-1 day, +2 days] -> [1969-12-31, 1970-01-03]
        # Only Record 1 should be within bounds.
        self.assertEqual(len(shifted), 1)
        self.assertEqual(shifted[0].Value, "Primary1")
        self.assertEqual(shifted[0].StartTime.replace(tzinfo=timezone.utc), datetime(1970, 1, 2, 12, 0, 0, tzinfo=timezone.utc))

    @patch("app.services.relative_time_service.csv_fetcher.fetch_data")
    def test_align_records_occurrence_index_last(self, mock_fetch):
        # Time: 2020-01-02
        record_a = Record(
            StartTime=datetime(2020, 1, 2),
            EndTime=datetime(2020, 1, 2),
            Value="ValA",
            PatientID=1,
            ConceptName="ConceptA"
        )
        
        # Time: 2020-01-03
        record_b = Record(
            StartTime=datetime(2020, 1, 3),
            EndTime=datetime(2020, 1, 3),
            Value="AnyVal",
            PatientID=1,
            ConceptName="ConceptB"
        )
        
        def side_effect(request, abstract=True):
            if request.concept_name == "ConceptA":
                return [record_a]
            elif request.concept_name == "ConceptB":
                return [record_b]
            return []
        
        mock_fetch.side_effect = side_effect
        
        # Config with occurrence_index = -1 (last event)
        config = RelativeTimeConfig(
            reference_concepts=[
                ReferenceConcept(concept_name="ConceptA", concept_value="ValA"),
                ReferenceConcept(concept_name="ConceptB")
            ],
            occurrence_index=-1,
            start_delta=RelativeTimeDelta(value=-1, unit="d"),
            end_delta=RelativeTimeDelta(value=2, unit="d")
        )
        
        primary_records = [
            Record(
                StartTime=datetime(2020, 1, 7),
                EndTime=datetime(2020, 1, 7),
                Value="Primary1",
                PatientID=1,
                ConceptName="Primary"
            )
        ]
        
        # Candidates:
        # 1. ConceptA at 2020-01-02
        # 2. ConceptB at 2020-01-03
        # Last (-1) is 2020-01-03.
        # Record 1 (2020-01-07) is 4 days after 2020-01-03 (t_zero). Shift to 1970-01-05.
        # Window: [-1d, +2d] around 1970-01-01 -> [1969-12-31, 1970-01-03].
        # 1970-01-05 is outside window, so shifted should be empty.
        
        shifted, g_start, g_end = RelativeTimeService.align_records_to_anchor(
            records=primary_records,
            config=config,
            patients_list=["1"],
            use_generated_data=False
        )
        
        self.assertEqual(len(shifted), 0)

if __name__ == "__main__":
    unittest.main()
