### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"description": "Investigate the inventory package failure and docstring requirements. Workspace paths are relative to sandbox root, e.g. workspace/inventory. Do not modify tests. Report relevant source files, suspected defects, and suggested fix scope; do not edit files.", "subagent_type": "explorer"}

### Tool result
## Findings

The tests reproduce **2 failures out of 6**:

- `test_total_value_thousands_separator` fails because `parse_price("$1,299.50")` raises `decimal.InvalidOperation`.
- `test_discount_rounding_half_up` fails because `apply_discount(Decimal("10.05"), 10)` returns `Decimal("9.04")`, not `Decimal("9.05")`.

The README says to run the tests from `workspace/` with `python -m pytest tests -q` (`workspace/README.md:3–5`). I made no changes.

## Relevant source and suspected defects

- **`workspace/inventory/pricing.py:5–15` — `parse_price`**  
  Its docstring lists comma-separated prices and accounting-style parentheses as supported formats (`:8–12`), but the implementation only strips whitespace and dollar signs before passing the result to `Decimal` (`:14–15`). The comma case is confirmed to fail in the test run. The parentheses case is also not handled by the implementation and is a likely defect relative to the docstring.

- **`workspace/inventory/pricing.py:18–25` — `apply_discount`**  
  The docstring requires rounding to two decimal places using “round half up” (`:21–22`). The implementation calls `quantize` without specifying a rounding mode (`:25`); its default rounding does not meet that stated requirement. The test confirms a mismatch.

- **`workspace/inventory/export.py:5–12` — `to_csv_row`**  
  The docstring says names containing commas or double quotes must be quoted, with embedded double quotes doubled (`:8–9`). The implementation inserts the name directly i

### Tool call: ls
{"path": "workspace"}

### Tool call: glob
{"pattern": "**/*.py", "path": "workspace"}

### Tool call: glob
{"pattern": "tests/**", "path": "workspace"}

### Tool result
['/workspace/.pytest_cache/', '/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py', '/workspace/tests/test_report.py']

### Tool result
['/workspace/tests/__pycache__/test_report.cpython-313-pytest-9.1.1.pyc', '/workspace/tests/__pycache__/test_report.cpython-314-pytest-9.1.1.pyc', '/workspace/tests/test_report.py']

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 100}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 100}

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py", "offset": 0, "limit": 200}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 0.3.1
- initial import

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool call: task
{"description": "Implement documented fixes in inventory package. Paths are sandbox-relative under workspace/ (use paths exactly like workspace/inventory/pricing.py). Do not modify anything under workspace/tests/. Read each source before editing. Requirements from docstrings: pricing.parse_price supports '$1,299.50', whitespace around numbers, plain decimal strings, and accounting parentheses meaning negative; apply_discount must round to 2 decimals using ROUND_HALF_UP. export.to_csv_row must CSV-escape item names: quote names containing comma or double quote and double embedded quotes; price two decimals. report.low_stock returns names with qty strictly below threshold, sorted alphabetically case-insensitively. Keep scope focused, follow standard Python conventions. Make changes and report files changed plus key implementation details; do not run tests unless convenient.", "subagent_type": "implementer"}

### Tool result
Implemented the documented fixes in:

- `workspace/inventory/pricing.py` — `parse_price` now handles comma-separated prices and accounting parentheses; `apply_discount` explicitly rounds with `ROUND_HALF_UP`.
- `workspace/inventory/export.py` — CSV-escapes names containing commas or double quotes and retains two-decimal price formatting.
- `workspace/inventory/report.py` — `low_stock` uses a strict threshold and sorts names case-insensitively.

Manual validation covered the requested price formats, half-up rounding, CSV escaping, and low-stock filtering and ordering. All checks passed. No test suite was run.

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 120}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py", "offset": 0, "limit": 120}

### Tool result
@@ lines 1-31 of 31 @@
"""Price utilities for the inventory package."""
from decimal import Decimal, ROUND_HALF_UP


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip()
    is_negative = cleaned.startswith("(") and cleaned.endswith(")")
    if is_negative:
        cleaned = cleaned[1:-1].strip()

    cleaned = cleaned.replace("$", "").replace(",", "").strip()
    price = Decimal(cleaned)
    return -price if is_negative else price


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

### Tool result
@@ lines 1-16 of 16 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    name = str(item["name"])
    if "," in name or '"' in name:
        name = '"' + name.replace('"', '""') + '"'

    price = parse_price(item["price"])
    return f'{name},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-26 of 26 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    names = [item["name"] for item in items if item["qty"] < threshold]
    return sorted(names, key=str.casefold)

### Tool call: execute
{"command": "python -m pytest workspace/tests -q && python - <<'PY'\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.export import to_csv_row\nfrom inventory.report import low_stock\nassert parse_price('$1,299.50') == Decimal('1299.50')\nassert parse_price('  12 ') == Decimal('12')\nassert parse_price('1299.5') == Decimal('1299.5')\nassert parse_price('(12.00)') == Decimal('-12.00')\nassert apply_discount(Decimal('10.05'), 10) == Decimal('9.05')\nassert to_csv_row({'name':'a,\"b','price':'2.5','qty':4}) == '\"a,\"\"b\",2.50,4'\nassert low_stock([{'name':'z','qty':4},{'name':'A','qty':1},{'name':'b','qty':5}]) == ['A','z']\nPY", "timeout": 120}

### Tool result

==================================== ERRORS ====================================
_______________ ERROR collecting workspace/tests/test_report.py ________________
ImportError while importing test module '/tmp/lab-run-xrp_yyp1/workspace/tests/test_report.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/tests/test_report.py:3: in <module>
    from inventory.export import to_csv_row
E   ModuleNotFoundError: No module named 'inventory'
=========================== short test summary info ============================
ERROR workspace/tests/test_report.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.13s

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q && python - <<'PY'\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.export import to_csv_row\nfrom inventory.report import low_stock\nassert parse_price('$1,299.50') == Decimal('1299.50')\nassert parse_price('  12 ') == Decimal('12')\nassert parse_price('1299.5') == Decimal('1299.5')\nassert parse_price('(12.00)') == Decimal('-12.00')\nassert apply_discount(Decimal('10.05'), 10) == Decimal('9.05')\nassert to_csv_row({'name':'a,\"b','price':'2.5','qty':4}) == '\"a,\"\"b\",2.50,4'\nassert low_stock([{'name':'z','qty':4},{'name':'A','qty':1},{'name':'b','qty':5}]) == ['A','z']\nPY", "timeout": 120}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Updated `workspace/inventory/pricing.py`, `export.py`, and `report.py` to match their docstrings: support documented price formats and half-up discount rounding, escape CSV names, and apply strict, case-insensitive low-stock filtering and sorting.

Verified with the test suite (6 passed) and additional checks for the documented edge cases.