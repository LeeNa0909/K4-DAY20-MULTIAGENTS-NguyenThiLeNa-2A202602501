"""Audit the completed lab artifacts. Run in the same Linux environment as runner."""
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

from lab.compare import build_table, load_runs
from lab.curator import parse_skill_blocks, validate_skill
from lab.tasks import ROOT, hash_skills, list_tasks

BASE_REF = "d982034"


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout


def definition(text, name):
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.dump(node, include_attributes=False)
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.dump(node, include_attributes=False)
    raise ValueError(f"Missing definition: {name}")


def main():
    problems = []
    protected_paths = [
        "tests", "tasks", "scripts", "src/lab/model.py", "src/lab/tasks.py",
        "src/lab/grading.py", "src/lab/testing.py", "src/lab/compare.py",
    ]
    changed = git("diff", "--name-only", BASE_REF, "--", *protected_paths).strip()
    if changed:
        problems.append("Protected files changed: " + changed.replace("\n", ", "))
    protected_definitions = {
        "src/lab/agent.py": ["PATHS_NOTE", "BASE_PROMPT", "SKILLS_NOTE", "SUBAGENTS_NOTE"],
        "src/lab/runner.py": ["CONDITIONS", "render_trace", "main"],
        "src/lab/curator.py": ["SAFE_NAME", "validate_skill", "parse_skill_blocks"],
    }
    for relative, names in protected_definitions.items():
        original = git("show", f"{BASE_REF}:{relative}")
        current = (ROOT / relative).read_text(encoding="utf-8")
        for name in names:
            if definition(original, name) != definition(current, name):
                problems.append(f"Provided definition changed: {relative}:{name}")
    protected_ok = not problems

    runs = load_runs(ROOT / "results")
    expected = {(task.id, condition) for task in list_tasks()
                for condition in ("baseline", "subagents", "skills-auto")}
    actual = {(run["task"], run["condition"]) for run in runs}
    if actual != expected or len(runs) != 18:
        problems.append("Expected exactly 18 official task/condition records")
    frozen_hash = hash_skills(ROOT / "skills" / "auto")
    for run in runs:
        label = f"{run['condition']}/{run['task']}"
        if run.get("error") or run.get("grading_error"):
            problems.append(f"Run error: {label}")
        checks = run["checks"]
        passed = sum(check["passed"] for check in checks)
        if run["total"] != len(checks) or run["passed"] != passed:
            problems.append(f"Inconsistent check counts: {label}")
        if not checks or abs(run["score"] - passed / len(checks)) > 1e-12:
            problems.append(f"Inconsistent score: {label}")
        if run["tokens"]["total"] <= 0:
            problems.append(f"Missing real token usage: {label}")
        if run["tokens"]["input"] + run["tokens"]["output"] != run["tokens"]["total"]:
            problems.append(f"Inconsistent token counts: {label}")
        if run["skills_modified"]:
            problems.append(f"Skill modified during run: {label}")
        if run["condition"] == "skills-auto" and run["skills_sha256"] != frozen_hash:
            problems.append(f"Wrong frozen skill hash: {label}")
        trace = ROOT / "results" / run["condition"] / run["task"] / "trace.md"
        if not trace.is_file() or not trace.read_text(encoding="utf-8").strip():
            problems.append(f"Missing trace: {label}")
        if run["role"] == "eval" and any(check.get("detail") for check in checks):
            problems.append(f"Evaluation feedback should be blank: {label}")

    table = ROOT / "report" / "table.md"
    if not table.is_file() or table.read_text(encoding="utf-8") != build_table(runs) + "\n":
        problems.append("report/table.md does not match lab.compare output")
    report = (ROOT / "report" / "REPORT.md").read_text(encoding="utf-8")
    if table.is_file() and table.read_text(encoding="utf-8").strip() not in report:
        problems.append("Report does not contain the generated comparison table")
    for number in range(1, 11):
        if not re.search(rf"^## {number}\. ", report, re.M):
            problems.append(f"Missing report section {number}")
    if any(line.startswith("> ") for line in report.splitlines()) or "(dán bảng ở đây)" in report:
        problems.append("Report still contains template instructions")
    dev = list((ROOT / "results" / "skills-auto-dev").glob("*/run.json"))
    if len(dev) != 3:
        problems.append("Missing three development records for noise comparison")
    for path in dev:
        run = json.loads(path.read_text(encoding="utf-8"))
        if (run.get("error") or run["skills_modified"] or run["role"] != "learn"
                or run["skills_sha256"] != frozen_hash):
            problems.append(f"Development run is not comparable: {run['task']}")

    audits = list((ROOT / "report" / "curator").glob("*.json"))
    generated = {}
    for path in audits:
        audit = json.loads(path.read_text(encoding="utf-8"))
        if any(not task.endswith("-learn") for task in audit["learning_tasks"]):
            problems.append("Curator provenance contains an evaluation source")
        blocks = dict(parse_skill_blocks(audit["reply"]))
        for name, digest in audit["skills"].items():
            generated[name] = (digest, blocks[name] + "\n")
    skills = sorted((ROOT / "skills" / "auto").glob("*/SKILL.md"))
    if not skills:
        problems.append("No generated skills")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        name = path.parent.name
        if validate_skill(text, name):
            problems.append(f"Invalid skill: {name}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if generated.get(name) != (digest, text):
            problems.append(f"Skill differs from original curator output: {name}")

    secrets = [value for key, value in dotenv_values(ROOT / ".env").items()
               if value and any(marker in key for marker in ("KEY", "TOKEN", "SECRET"))]
    files = [path for folder in ("src", "report", "results", "skills")
             for path in (ROOT / folder).rglob("*")
             if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"]
    for path in files:
        content = path.read_bytes()
        if any(secret.encode() in content for secret in secrets):
            problems.append(f"API secret found in {path.relative_to(ROOT)}")

    for problem in problems:
        print("FAIL:", problem)
    print(f"Official runs: {len(runs)}; dev runs: {len(dev)}; generated skills: {len(skills)}")
    print("Provided files/functions: " + ("OK" if protected_ok else "FAIL"))
    print("Artifact audit: " + ("OK" if not problems else "FAIL"))
    return bool(problems)


if __name__ == "__main__":
    sys.exit(main())
