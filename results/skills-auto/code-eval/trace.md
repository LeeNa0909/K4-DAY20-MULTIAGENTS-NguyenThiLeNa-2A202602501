### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: read_file
{"file_path": "skills/python-bugfix-workflow/SKILL.md", "offset": 0, "limit": 1000}

### Tool call: ls
{"path": "workspace"}

### Tool call: ls
{"path": "skills"}

### Tool result
@@ lines 1-11 of 11 @@
---
name: python-bugfix-workflow
description: Use when fixing bugs in a Python package and delivering tested, documented changes.
---
1. Inspect the package, its existing tests, and project instructions before editing.
2. Fix the identified bugs with focused changes.
3. Add type annotations to every parameter and return value of each public package function.
4. Add `tests/test_regressions.py` with one test per fixed bug; include at least 3 tests.
5. Record each fix in `CHANGELOG.md` under `## Unreleased`, using `- fix(<function name>): <short description>`; include at least 3 bullets.
6. Run the tests from the repository root or package root so package imports resolve.
7. Verify the regression file and full relevant test suite pass, and confirm the changelog and annotations meet these requirements.

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool result
['/skills/csv-data-cleaning/', '/skills/log-triage-json/', '/skills/python-bugfix-workflow/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 200}

### Tool call: glob
{"pattern": "**/*", "path": "workspace"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-313.pyc', '/workspace/bookings/__pycache__/__init__.cpython-314.pyc', '/workspace/bookings/__pycache__/billing.cpython-313.pyc', '/workspace/bookings/__pycache__/billing.cpython-314.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-313.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-314.pyc', '/workspace/bookings/__pycache__/schedule.cpython-313.pyc', '/workspace/bookings/__pycache__/schedule.cpython-314.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-313.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-314.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-313-pytest-9.1.1.pyc', '/workspace/tests/__pycache__/test_bookings.cpython-314-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "offset": 0, "limit": 500}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120}

### Tool result
FF.                                                                      [100%]
=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
________________________ test_billable_blocks_rounds_up ________________________

    def test_bil

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return (minutes + block - 1) // block\n"}

### Tool result
Updated file /workspace/bookings/billing.py

### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\n_DURATION_PATTERN = re.compile(r\"(?:(\\d+)h)?(?:(\\d+)m)?\\Z\")\n_CLOCK_PATTERN = re.compile(r\"(\\d+):(\\d+)\\Z\")\n_MINUTES_PATTERN = re.compile(r\"\\d+\\Z\")\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    value = text.strip()\n    clock_match = _CLOCK_PATTERN.fullmatch(value)\n    if clock_match:\n        hours, minutes = (int(part) for part in clock_match.groups())\n        if minutes >= 60:\n            raise ValueError(f\"bad duration: {text!r}\")\n        return hours * 60 + minutes\n\n    if _MINUTES_PATTERN.fullmatch(value):\n        return int(value)\n\n    duration_match = _DURATION_PATTERN.fullmatch(value)\n    if duration_match and any(part is not None for part in duration_match.groups()):\n        hours, minutes = (int(part or 0) for part in duration_match.groups())\n        return hours * 60 + minutes\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable\n\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(duration) for duration in durations)\n\n\ndef add_slot(slot: object, slots: list[object] | None = None) -> list[object]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*(slots if slots is not None else []), slot]\n"}

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool call: write_file
{"file_path": "workspace/bookings/calendar_export.py", "content": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)\n"}

### Tool result
Updated file /workspace/bookings/calendar_export.py

### Tool call: write_file
{"file_path": "workspace/tests/test_regressions.py", "content": "import pytest\n\nfrom bookings.billing import billable_blocks\nfrom bookings.calendar_export import slot_end\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\n\n\ndef test_parse_duration_accepts_every_documented_format():\n    assert parse_duration(\"1h30m\") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n    assert parse_duration(\" 45 \") == 45\n\n\ndef test_billable_blocks_rounds_up_and_rejects_negative_minutes():\n    assert billable_blocks(0) == 0\n    assert billable_blocks(16) == 2\n    assert billable_blocks(20, block=10) == 2\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n\n\ndef test_add_slot_returns_a_new_list_without_mutating_input():\n    original = [\"existing\"]\n    result = add_slot(\"new\", original)\n    assert result == [\"existing\", \"new\"]\n    assert original == [\"existing\"]\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n\n\ndef test_total_minutes_and_slot_end_use_duration_parser():\n    assert total_minutes([\"45m\", \"1:30\", \"2h\"]) == 255\n    assert slot_end(60, \"1h\") == 120\n\n\ndef test_parse_duration_rejects_malformed_values():\n    for value in (\"\", \"1h2h\", \"1:60\", \"1.5h\"):\n        with pytest.raises(ValueError):\n            parse_durat

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n\n", "new_string": "## Unreleased\n- fix(parse_duration): support all documented duration formats\n- fix(billable_blocks): round partial blocks up and reject negative minutes\n- fix(add_slot): return a fresh list without mutating the input\n\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120}

### Tool result
........                                                                 [100%]
8 passed in 0.02s

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && python -m compileall -q bookings && git diff -- bookings/billing.py bookings/timeutil.py bookings/schedule.py bookings/calendar_export.py CHANGELOG.md tests/test_regressions.py", "timeout": 120}

### Tool result
[stderr] warning: Limiting comparison with pathspecs is only supported if both paths are directories.
[stderr] usage: git diff --no-index [<options>] <path> <path> [<pathspec>...]
[stderr] 
[stderr] Diff output format options
[stderr]     -p, --patch           generate patch
[stderr]     -s, --no-patch        suppress diff output
[stderr]     -u                    generate patch
[stderr]     -U, --unified[=<n>]   generate diffs with <n> lines context
[stderr]     -W, --[no-]function-context
[stderr]                           generate diffs with <n> lines context
[stderr]     --raw                 generate the diff in raw format
[stderr]     --patch-with-raw      synonym for '-p --raw'
[stderr]     --patch-with-stat     synonym for '-p --stat'
[stderr]     --numstat             machine friendly --stat
[stderr]     --shortstat           output only the last line of --stat
[stderr]     -X, --dirstat[=<param1>,<param2>...]
[stderr]                           output the distribution of relative amount of changes for each sub-directory
[stderr]     --cumulative          synonym for --dirstat=cumulative
[stderr]     --dirstat-by-file[=<param1>,<param2>...]
[stderr]                           synonym for --dirstat=files,<param1>,<param2>...
[stderr]     --check               warn if changes introduce conflict markers or whitespace errors
[stderr]     --summary             condensed summary such as creations, renames and mode changes
[stderr]     --name-only           show only names of

### Assistant
Fixed duration parsing for all documented formats, corrected billable-block rounding and negative-minute handling, and made `add_slot` return a new list without mutating its input. Added regression tests and changelog entries. The full test suite passes: **8 passed**.

Changed: `workspace/bookings/billing.py`, `workspace/bookings/timeutil.py`, `workspace/bookings/schedule.py`, `workspace/bookings/calendar_export.py`, `workspace/CHANGELOG.md`. Created: `workspace/tests/test_regressions.py`.