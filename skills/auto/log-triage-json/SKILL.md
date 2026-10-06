---
name: log-triage-json
description: Use when converting timestamped service logs with multiline entries and repeat markers into a structured error summary.
---
1. Read the log format instructions and parse each entry’s timestamp, level, service, and message.
2. Attach continuation lines to the preceding entry; treat a repeat marker as applying to that entry, including its continuation lines.
3. Keep only ERROR and CRITICAL entries, case-insensitively; write their levels in uppercase.
4. Convert timestamps to UTC and format them as `YYYY-MM-DDTHH:MM:SSZ`.
5. Normalize service names to lowercase and replace `-` with `_`.
6. Set `repeat_count` to one plus the sum of the entry’s repeat-marker counts.
7. Set `exception` to the last line of an attached traceback, or `null` when there is no traceback.
8. Sort `errors` by service, then by `timestamp_utc`, ascending.
9. Sum `repeat_count` by normalized service in `counts_by_service`.
10. Include top-level `schema_version` set to `2` and `generated_by` set to `log-triage`.
11. Verify filtering, normalized names, UTC timestamps, repeat counts, sort order, service totals, and schema fields.
=== END===
