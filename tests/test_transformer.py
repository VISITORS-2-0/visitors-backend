import unittest
import warnings
from datetime import datetime

from app.models.schemas import Record
from app.services.transformer import IntervalTransformationService

warnings.simplefilter("ignore")


def record(start, end, value, patient_id=1, concept="Status"):
    return Record(
        StartTime=datetime.fromisoformat(start),
        EndTime=datetime.fromisoformat(end),
        Value=value,
        PatientID=patient_id,
        ConceptName=concept,
    )


class IntervalTransformationServiceTests(unittest.TestCase):
    def test_empty_events_return_empty_list(self):
        result = IntervalTransformationService.transform_to_intervals([])

        self.assertEqual(result, [])

    def test_most_time_spent_value_wins_after_clipping_to_bucket(self):
        events = [
            record("2020-01-01T06:00:00", "2020-01-02T12:00:00", "A"),
            record("2020-01-01T00:00:00", "2020-01-01T12:00:00", "B"),
        ]

        result = IntervalTransformationService.transform_to_intervals(
            events,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 3),
            interval_str="D",
        )

        self.assertEqual([row.Value for row in result], ["A", "A"])
        self.assertEqual(result[0].StartTime.isoformat(), "2020-01-01T00:00:00+00:00")
        self.assertEqual(result[0].EndTime.isoformat(), "2020-01-02T00:00:00+00:00")

    def test_bucket_with_no_overlap_gets_no_value(self):
        events = [
            record("2020-01-01T00:00:00", "2020-01-01T12:00:00", "A"),
        ]

        result = IntervalTransformationService.transform_to_intervals(
            events,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 3),
            interval_str="D",
        )

        self.assertEqual([row.Value for row in result], ["A", "No Value"])

    def test_patient_and_concept_groups_are_transformed_independently(self):
        events = [
            record("2020-01-01T00:00:00", "2020-01-02T00:00:00", "A", patient_id=1, concept="C1"),
            record("2020-01-01T00:00:00", "2020-01-02T00:00:00", "B", patient_id=2, concept="C1"),
            record("2020-01-01T00:00:00", "2020-01-02T00:00:00", "C", patient_id=1, concept="C2"),
        ]

        result = IntervalTransformationService.transform_to_intervals(
            events,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 2),
            interval_str="D",
        )

        grouped = {(row.PatientID, row.ConceptName): row.Value for row in result}
        self.assertEqual(grouped[(1, "C1")], "A")
        self.assertEqual(grouped[(2, "C1")], "B")
        self.assertEqual(grouped[(1, "C2")], "C")


if __name__ == "__main__":
    unittest.main()
