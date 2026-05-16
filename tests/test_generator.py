import random
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from app.models.schemas import DataRequest
from app.services.generator import DataGeneratorService


class DataGeneratorServiceTests(unittest.TestCase):
    def test_generate_cached_returns_empty_for_invalid_date_range(self):
        result = DataGeneratorService._generate_cached.__wrapped__(
            ("1",),
            datetime(2020, 1, 2),
            datetime(2020, 1, 1),
            ("A",),
            "Status",
            allow_numeric=False,
        )

        self.assertEqual(result, [])

    def test_generate_cached_numeric_records_stay_in_range_and_dates(self):
        random.seed(7)
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 10)

        result = DataGeneratorService._generate_cached.__wrapped__(
            ("5",),
            start,
            end,
            (),
            "Lab",
            min_value=10,
            max_value=20,
            allow_numeric=True,
        )

        self.assertGreater(len(result), 0)
        for row in result:
            self.assertEqual(row.PatientID, 5)
            self.assertEqual(row.ConceptName, "Lab")
            self.assertGreaterEqual(row.StartTime, start)
            self.assertLessEqual(row.EndTime, end)
            self.assertGreaterEqual(float(row.Value), 10)
            self.assertLessEqual(float(row.Value), 20)

    def test_generate_cached_raises_when_categorical_values_are_missing(self):
        with self.assertRaises(ValueError):
            DataGeneratorService._generate_cached.__wrapped__(
                ("1",),
                datetime(2020, 1, 1),
                datetime(2020, 1, 2),
                None,
                "Status",
                allow_numeric=False,
            )

    def test_public_generate_data_passes_concept_values_to_cached_generator(self):
        request = DataRequest(
            patients_list=["1"],
            concept_name="Status",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 2),
        )
        concept = SimpleNamespace(values=["Low", "High"])

        with patch("app.services.generator.concept_manager_instance.get_entity_by_name", return_value=concept):
            with patch.object(DataGeneratorService, "_generate_cached", return_value=[]) as generate_cached:
                DataGeneratorService.generate_data(request)

        generate_cached.assert_called_once_with(
            ("1",),
            datetime(2020, 1, 1),
            datetime(2020, 1, 2),
            ("Low", "High"),
            "Status",
            0.0,
            100.0,
            allow_numeric=False,
        )

    def test_public_generate_numeric_data_uses_concept_min_and_max(self):
        request = DataRequest(
            patients_list=["1"],
            concept_name="Lab",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 2),
        )
        concept = SimpleNamespace(min=3.5, max=9.5)

        with patch("app.services.generator.concept_manager_instance.get_entity_by_name", return_value=concept):
            with patch.object(DataGeneratorService, "_generate_cached", return_value=[]) as generate_cached:
                DataGeneratorService.generate_numeric_data(request)

        generate_cached.assert_called_once_with(
            ("1",),
            datetime(2020, 1, 1),
            datetime(2020, 1, 2),
            (),
            "Lab",
            3.5,
            9.5,
            allow_numeric=True,
        )


if __name__ == "__main__":
    unittest.main()
