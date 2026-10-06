### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "offset": 0, "limit": 300}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "offset": 0, "limit": 300}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py", "offset": 0, "limit": 300}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 300}

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "offset": 0, "limit": 100}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

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
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 250}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 200}

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

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    return round(minutes / block)\n", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n\n    # Integer arithmetic avoids both rounding down partial blocks and\n    # floating-point precision issues for large minute counts.\n    return -(-minutes // block)\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/timeutil.py", "old_string": "    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))\n", "new_string": "    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    value = text.strip()\n    match = re.fullmatch(r\"(\\d+)h(\\d+)m\", value)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    match = re.fullmatch(r\"(\\d+)h\", value)\n    if match:\n        return int(match.group(1)) * 60\n\n    match = re.fullmatch(r\"(\\d+)m\", value)\n    if match:\n        return int(match.group(1))\n\n    match = re.fullmatch(r\"(\\d+):(\\d{2})\", value)\n    if match and int(match.group(2)) < 60:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    match = re.fullmatch(r\"\\d+\", value)\n    if match:\n        return int(value)\n\n    raise ValueError(f\"bad duration: {text!r}\")\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/schedule.py", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots\n", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*(slots or []), slot]\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/schedule.py", "old_string": "    return [*(slots or []), slot]\n", "new_string": "    return [*([] if slots is None else slots), slot]\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: execute
{"command": "python -m pytest workspace/tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "python -m pytest workspace/tests -q", "timeout": 3600}

### Tool result

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-run-3pv0tums/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/tests/test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ============================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.13s

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && python - <<'PY'\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot\n\nassert [parse_duration(value) for value in ('1h30m', '2h', '45m', '1:30', '45', ' 45 ')] == [90, 120, 45, 90, 45, 45]\nassert billable_blocks(16) == 2\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative minutes should fail')\noriginal = ['a']\nresult = add_slot('b', original)\nassert result == ['a', 'b'] and result is not original and original == ['a']\nassert add_slot('a') == ['a'] and add_slot('b') == ['b']\nPY", "timeout": 3600}

### Tool result
<no output>
[Command succeeded with exit code 0]

### Assistant
Updated `billing.py`, `timeutil.py`, and `schedule.py` to round billable blocks up and reject negative minutes, support every documented duration format, and return a new slot list without shared state. The test suite passes.