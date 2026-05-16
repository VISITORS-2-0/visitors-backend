import csv
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from app.models.schemas import DataRequest
from app.services.csv_data_fetcher import CSVDataFetcher


class CSVDataFetcherTests(unittest.TestCase):
    def test_parse_datetime_supports_fractional_plain_and_iso_values(self):
        self.assertEqual(
            CSVDataFetcher.parse_datetime("2004-12-29 00:07:07.1234567"),
            datetime(2004, 12, 29, 0, 7, 7, 123456),
        )
        self.assertEqual(
            CSVDataFetcher.parse_datetime("2007-12-13 00:00:00"),
            datetime(2007, 12, 13, 0, 0, 0),
        )
        self.assertEqual(
            CSVDataFetcher.parse_datetime("2007-12-13T00:00:00"),
            datetime(2007, 12, 13, 0, 0, 0),
        )

    def test_fetch_data_filters_files_concepts_and_requested_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            self._write_csv(
                data_dir / "ID_1_Abstract.csv",
                [
                    ["2020-01-01 00:00:00", "2020-01-02 00:00:00", "Keep", "1", "Target"],
                    ["2020-01-03 00:00:00", "2020-01-04 00:00:00", "WrongConcept", "1", "Other"],
                    ["2019-01-01 00:00:00", "2019-01-02 00:00:00", "TooEarly", "1", "Target"],
                    ["2022-01-01 00:00:00", "2022-01-02 00:00:00", "TooLate", "1", "Target"],
                    ["not-a-date", "2020-01-02 00:00:00", "BadDate", "1", "Target"],
                ],
            )
            fetcher = CSVDataFetcher(data_dir=str(data_dir))
            request = DataRequest(
                patients_list=["1", "missing"],
                concept_name="Target",
                start_date=datetime(2020, 1, 1),
                end_date=datetime(2021, 1, 1),
            )

            result = fetcher.fetch_data(request, abstract=True)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].Value, "Keep")
            self.assertEqual(result[0].PatientID, 1)
            self.assertEqual(result[0].ConceptName, "Target")

    def test_fetch_data_uses_raw_suffix_when_abstract_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            self._write_csv(
                data_dir / "ID_2_Raw.csv",
                [["2020-01-01 00:00:00", "2020-01-02 00:00:00", "7.5", "2", "Lab"]],
            )
            self._write_csv(
                data_dir / "ID_2_Abstract.csv",
                [["2020-01-01 00:00:00", "2020-01-02 00:00:00", "Abstract", "2", "Lab"]],
            )
            fetcher = CSVDataFetcher(data_dir=str(data_dir))
            request = DataRequest(
                patients_list=["2"],
                concept_name="Lab",
                start_date=datetime(2020, 1, 1),
                end_date=datetime(2021, 1, 1),
            )

            result = fetcher.fetch_data(request, abstract=False)

            self.assertEqual([row.Value for row in result], ["7.5"])

    @staticmethod
    def _write_csv(path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["StartTime", "EndTime", "Value", "PatientID", "ConceptName"])
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
