### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: read_file
{"file_path": "skills/python-bugfix-workflow/SKILL.md", "offset": 0, "limit": 1000}

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

### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/inventory"}

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 1000}

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_report.py']

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 0.3.1
- initial import

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: read_file
{"file_path": "workspace/inventory/__init__.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py", "offset": 0, "limit": 1000}

### Tool result
@@ lines 1-1 @@
System reminder: File exists but has empty contents

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

### Tool call: execute
{"command": "python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
.FF...                                                                   [100%]
=================================== FAILURES ===================================
_____________________ test_total_value_thousands_separator _____________________

    def test_total_value_thousands_separator():
        items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
>       assert total_value(items) == Decimal("2599.00")
               ^^^^^^^^^^^^^^^^^^

tests/test_report.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
inventory/report.py:14: in total_value
    price = parse_price(item["price"])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '$1,299.50'

    def parse_price(text):
        """Convert a price string to a Decimal.
    
        Supported formats:
          "$1,299.50" -> Decimal("1299.50")
          "  12 "     -> Decimal("12")
          "1299.5"    -> Decimal("1299.5")
          "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
        """
        cleaned = text.strip().replace("$", "")
>       return Decimal(cleaned)
               ^^^^^^^^^^^^^^^^
E       decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

inventory/pricing.py:15: InvalidOperation
________________________ test_discount_rounding_half_up ________________________

    def test_discount_rounding_half_up():
>       assert apply_discount(Decimal

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "old_string": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import Decimal\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)\n\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))\n", "new_string": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import Decimal, ROUND_HALF_UP\n\n\ndef parse_price(text: str) -> Decimal:\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip()\n    is_negative = cleaned.startswith(\"(\") and cleaned.endswith(\")\")\n    if is_negative:\n        cleaned 

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "workspace/inventory/report.py", "old_string": "\"\"\"Inventory reports.\"\"\"\nfrom decimal import Decimal\n\nfrom .pricing import apply_discount, parse_price\n\n\ndef total_value(items):\n    \"\"\"Total value of `items` after per-item discounts.\n\n    Each item is a dict: {\"name\": str, \"price\": str, \"qty\": int, \"discount\": percent (optional)}.\n    \"\"\"\n    total = Decimal(\"0\")\n    for item in items:\n        price = parse_price(item[\"price\"])\n        price = apply_discount(price, item.get(\"discount\", 0))\n        total += price * item[\"qty\"]\n    return total\n\n\ndef low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]\n", "new_string": "\"\"\"Inventory reports.\"\"\"\nfrom decimal import Decimal\nfrom typing import Any\n\nfrom .pricing import apply_discount, parse_price\n\n\ndef total_value(items: list[dict[str, Any]]) -> Decimal:\n    \"\"\"Total value of `items` after per-item discounts.\n\n    Each item is a dict: {\"name\": str, \"price\": str, \"qty\": int, \"discount\": percent (optional)}.\n    \"\"\"\n    total = Decimal(\"0\")\n    for item in items:\n        price = parse_price(item[\"price\"])\n        price = apply_discount(price, item.get(\"discount\", 0))\n        total += price * item[\"qty\"]\n    return total\n\n\ndef l

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 1000}

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

### Tool call: edit_file
{"file_path": "workspace/inventory/export.py", "old_string": "\"\"\"Export helpers.\"\"\"\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'\n", "new_string": "\"\"\"Export helpers.\"\"\"\nfrom typing import Any\n\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item: dict[str, Any]) -> str:\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    name = str(item[\"name\"])\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    price = parse_price(item[\"price\"])\n    return f'{name},{price:.2f},{item[\"qty\"]}'\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: write_file
{"file_path": "workspace/tests/test_regressions.py", "content": "from decimal import Decimal\n\nfrom inventory.export import to_csv_row\nfrom inventory.pricing import apply_discount, parse_price\nfrom inventory.report import low_stock\n\n\ndef test_parse_price_supports_grouping_and_accounting_notation():\n    assert parse_price(\"$1,299.50\") == Decimal(\"1299.50\")\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\n\ndef test_discount_uses_round_half_up():\n    assert apply_discount(Decimal(\"10.05\"), 10) == Decimal(\"9.05\")\n\n\ndef test_low_stock_is_strict_and_sorted_case_insensitively():\n    items = [\n        {\"name\": \"zebra\", \"qty\": 1},\n        {\"name\": \"Apple\", \"qty\": 4},\n        {\"name\": \"at threshold\", \"qty\": 5},\n    ]\n    assert low_stock(items) == [\"Apple\", \"zebra\"]\n\n\ndef test_csv_row_escapes_name_fields():\n    assert to_csv_row({\"name\": 'pen,\"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen,\"\"blue\"\"\",2.50,4'\n"}

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n\n## 0.3.1", "new_string": "## Unreleased\n- fix(parse_price): support thousands separators and accounting negatives\n- fix(apply_discount): round discounted prices using round half up\n- fix(low_stock): apply a strict threshold and case-insensitive sorting\n- fix(to_csv_row): escape names containing commas or double quotes\n\n## 0.3.1", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 3600}

### Tool result
..........                                                               [100%]
10 passed in 0.02s

[Command succeeded with exit code 0]

### Assistant
Fixed price parsing, half-up discount rounding, strict and case-insensitively sorted low-stock results, and CSV name escaping. Added regression tests, public-function type annotations, and changelog entries. The full test suite passes: **10 passed**.

Files changed: `workspace/inventory/pricing.py`, `workspace/inventory/report.py`, `workspace/inventory/export.py`, `workspace/tests/test_regressions.py` (new), and `workspace/CHANGELOG.md`.