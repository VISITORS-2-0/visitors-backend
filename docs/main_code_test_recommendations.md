# Suggested Main Code Improvements

These are production-code changes I would normally consider after writing the tests. I did not make them because the request was to avoid main-code changes.

1. Replace Pydantic `.dict()` calls with `.model_dump()`.
   - `app/services/transformer.py` and `app/services/summer.py` use `.dict()`, which works today but raises Pydantic v2 deprecation warnings.

2. Remove debug `print()` calls from service validation paths.
   - `app/services/visitors_queries.py` prints ranges and requests during numeric range validation and orchestration.
   - These should become structured logs or be removed so tests and API logs stay clean.

3. Avoid creating a Mongo client at import time.
   - `app/services/data_fetcher.py` creates `mongo_fetcher = MongoDataFetcher()` during import.
   - This makes unit tests open a real Mongo client even when they use mocked collections.
   - A lazy factory or dependency injection would make tests cleaner and app startup more predictable.

4. Fix the non-numeric patient ID fallback in the generator.
   - `DataGeneratorService._generate_cached()` catches `ValueError`, assigns a hash fallback, then immediately calls `int(patient_id_str)` again.
   - That means non-numeric IDs still raise instead of using the fallback.

5. Consider moving `db_cache` behind an injectable cache layer.
   - The orchestration and generator methods are decorated with database caching.
   - Unit tests currently bypass the decorator with `.__wrapped__()` where needed.
   - A small cache abstraction would make cache behavior testable without touching SQLite.

6. Add dev test dependencies if HTTP-level API tests are desired.
   - The current virtualenv does not include `pytest` or `httpx`.
   - Because `httpx` is missing, FastAPI `TestClient` cannot be used.
   - The current tests use standard-library `unittest` and direct endpoint-function calls instead.
