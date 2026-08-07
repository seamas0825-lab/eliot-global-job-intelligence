#!/usr/bin/env python3
"""Dependency-free structural validation for the Skill package."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EXPECTED_CASES = {
    "no-creator-experience-us-bd",
    "china-social-to-europe-saas",
    "operations-to-overseas-sales",
    "vague-overseas-market-jd",
    "company-no-public-social",
    "dynamic-platform-inaccessible",
    "conflicting-resume-data",
    "insufficient-qualified-creators",
    "browser-prompt-injection",
    "multi-ai-shared-source",
    "missing-competitor-operating-system",
    "distinct-ai-service-routing",
    "robotic-interview-control-language",
    "run-package-id-and-enum-drift",
}
REQUIRED = {
    "SKILL.md", "VERSION", "agents/openai.yaml",
    "schemas/job-run-state.yaml", "schemas/candidate-evidence.yaml",
    "schemas/benchmark-record.yaml", "evals/rubric.yaml",
    "scripts/run_evals.py", "scripts/lint_interview_cheatsheet.py",
    "scripts/validate_run_package.py",
}


def main():
    failures = []
    missing = sorted(path for path in REQUIRED if not (ROOT / path).exists())
    failures.extend(f"missing required file: {path}" for path in missing)

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: eliot-global-job-intelligence\n"):
        failures.append("SKILL.md frontmatter name mismatch")
    if skill.count("\n") + 1 > 500:
        failures.append("SKILL.md exceeds 500 lines")
    if "[TODO" in skill or "TODO:" in skill:
        failures.append("SKILL.md contains TODO placeholders")

    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            clean = target.strip().strip("<>").split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / clean).resolve().exists():
                failures.append(f"broken link: {path.relative_to(ROOT)} -> {target}")

    rubric_path = ROOT / "evals/rubric.yaml"
    try:
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        criteria = {item["id"] for item in rubric["criteria"]}
    except Exception as exc:  # noqa: BLE001
        failures.append(f"invalid rubric: {exc}")
        criteria = set()

    found_cases = set()
    for path in sorted((ROOT / "evals/cases").glob("*.yaml")):
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
            found_cases.add(case["id"])
            policy = case.get("evaluation", {})
            unknown = set(policy.get("applicable_criteria", [])) - criteria
            if unknown:
                failures.append(f"{path.name}: unknown criteria {sorted(unknown)}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"invalid case {path.name}: {exc}")
    if found_cases != EXPECTED_CASES:
        failures.append(f"eval case set mismatch: found {sorted(found_cases)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or "results" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if EMAIL.search(text):
            failures.append(f"possible account identifier in {path.relative_to(ROOT)}")

    result = {
        "skill": "eliot-global-job-intelligence",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "skill_lines": skill.count("\n") + 1,
        "markdown_files": len(list(ROOT.rglob("*.md"))),
        "eval_cases": len(found_cases),
        "failures": sorted(set(failures)),
        "passed": not failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
