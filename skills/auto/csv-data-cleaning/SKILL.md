---
name: csv-data-cleaning
description: Use when analyzing and producing cleaned outputs from CSV data with duplicate records, inconsistent fields, or monetary values.
---
1. Read the input instructions and data dictionary before processing; use them to identify date formats, missing-value markers, and canonical categories.
2. Count input data rows, including duplicates, for `rows_in`.
3. Deduplicate by the documented record identifier; retain one row per distinct record.
4. Exclude records whose amount is marked unknown, and count distinct records with known amounts as `rows_used`.
5. Normalize categories to their documented canonical spellings.
6. Parse date-only values using the documented timezone convention; convert timestamps with offsets to UTC.
7. Write `workspace/clean.csv` with header `order_id,timestamp_utc,region,amount_cents`; include one row per distinct record with a known amount.
8. Format `timestamp_utc` as `YYYY-MM-DDTHH:MM:SSZ` and represent amounts as integer cents.
9. Write `answer.json` with a `meta` object containing exactly the required fields: `source` (input filename), `rows_in`, and `rows_used`.
10. Represent every monetary value in `answer.json` as integer cents; retain the requested analysis fields.
11. Verify the CSV header, row eligibility, UTC formatting, canonical categories, integer-cent amounts, and metadata counts.
