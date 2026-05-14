import unittest
import warnings
from datetime import datetime

from app.models.schemas import Record
from app.services.summer import SummaryService

warnings.simplefilter("ignore")


def interval(start, end, value, patient_id, concept="Status"):
    return Record(
        StartTime=datetime.fromisoformat(start),
        EndTime=datetime.fromisoformat(end),
        Value=value,
        PatientID=patient_id,
        ConceptName=concept,
    )


class SummaryServiceTests(unittest.TestCase):
    def test_empty_intervals_return_empty_list(self):
        self.assertEqual(SummaryService.summarize_intervals([]), [])

    def test_counts_values_by_interval_and_concept(self):
        intervals = [
            interval("2020-01-01T00:00:00", "2020-01-02T00:00:00", "A", 1),
            interval("2020-01-01T00:00:00", "2020-01-02T00:00:00", "A", 2),
            interval("2020-01-01T00:00:00", "2020-01-02T00:00:00", "B", 3),
            interval("2020-01-02T00:00:00", "2020-01-03T00:00:00", "B", 1),
        ]

        result = SummaryService.summarize_intervals(intervals)

        first = next(row for row in result if row.StartTime == datetime(2020, 1, 1))
        second = next(row for row in result if row.StartTime == datetime(2020, 1, 2))

        self.assertEqual(first.Value_Dict, {"A": 2, "B": 1, "No Value": 0})
        self.assertEqual(first.TotalPatientsWithData, 3)
        self.assertEqual(second.Value_Dict, {"A": 0, "B": 1, "No Value": 0})
        self.assertEqual(second.TotalPatientsWithData, 1)

    def test_keeps_no_value_count_when_present(self):
        intervals = [
            interval("2020-01-01T00:00:00", "2020-01-02T00:00:00", "No Value", 1),
            interval("2020-01-01T00:00:00", "2020-01-02T00:00:00", "A", 2),
        ]

        result = SummaryService.summarize_intervals(intervals)

        self.assertEqual(result[0].Value_Dict["No Value"], 1)
        self.assertEqual(result[0].Value_Dict["A"], 1)
        self.assertEqual(result[0].TotalPatientsWithData, 2)


if __name__ == "__main__":
    unittest.main()
