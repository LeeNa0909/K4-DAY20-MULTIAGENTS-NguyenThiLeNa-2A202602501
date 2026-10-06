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
