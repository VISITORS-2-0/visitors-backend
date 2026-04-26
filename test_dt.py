from app.services.csv_data_fetcher import CSVDataFetcher

dates = [
    "2004-12-29 00:07:07.0000000",
    "2007-12-13 00:00:00"
]

for d in dates:
    print(CSVDataFetcher.parse_datetime(d))
