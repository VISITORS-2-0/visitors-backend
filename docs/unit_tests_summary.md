# Unit Tests Summary

The project now has a standard-library `unittest` suite under `tests/`. Run it with:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

## Interval Transformation

`IntervalTransformationService` turns raw patient records into fixed time intervals.

Tests cover empty input, choosing the value with the most time in a bucket, clipping events to interval boundaries, assigning `"No Value"` when nothing overlaps, and keeping patient/concept groups separate.

## Summary Service

`SummaryService` counts how many patients have each value in each interval.

Tests cover empty input, value counts per interval, zero-count values that should still appear, `"No Value"` handling, and total patient counts.

## CSV Data Fetcher

`CSVDataFetcher` reads patient CSV files and turns matching rows into records.

Tests cover timestamp parsing, 7-digit fractional seconds, ISO timestamps, missing files, concept filtering, date-window filtering, invalid date skipping, and raw vs abstract file suffixes.

## Data Generator

`DataGeneratorService` creates synthetic categorical or numeric records.

Tests cover invalid date ranges, generated numeric values staying inside concept min/max, generated records staying inside the request dates, missing categorical values raising an error, and public methods passing concept values or numeric limits into the cached generator.

## Concept Models

The concept models parse TAK XML-shaped dictionaries into typed Pydantic models.

Tests cover `derived-from` parsing, numeric min/max extraction, output and duration type detection, nominal/state allowed values, pattern defaults, and mapping-function parsing.

## Concept Manager

`ConceptManager` loads TAK XML files and builds concept lookup and relationship data.

Tests cover missing directories, XML missing required attributes, entity lookup by name/id, raw XML storage, `derived_from`, `derived_into`, and context relationships.

## Menu Builder

The menu builder scans TAK XML files and places each entity into the navigation structure.

Tests cover event, context, raw concept, and abstract concept classification, skipping files with no `concept-type`, and avoiding rebuilds after the hierarchy is already built.
