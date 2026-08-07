#!/usr/bin/env python3
"""Validate JSON-compatible YAML eval cases and score external judge results."""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_FIELDS = {
    "id", "input", "known_facts", "hidden_traps", "required_behavior",
    "forbidden_behavior", "expected_decisions", "acceptable_uncertainties",
}


def load_json_yaml(path):
    """The package stores JSON syntax in .yaml files; JSON is valid YAML 1.2."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_case(case, path, criterion_ids):
    missing = sorted(CASE_FIELDS - set(case or {}))
    if missing:
        raise ValueError(f"{path.name}: missing fields: {', '.join(missing)}")
    if not isinstance(case["id"], str) or not case["id"]:
        raise ValueError(f"{path.name}: id must be a non-empty string")
    if not isinstance(case["input"], str) or not case["input"]:
        raise ValueError(f"{path.name}: input must be a non-empty string")
    for field in CASE_FIELDS - {"id", "input"}:
        if not isinstance(case[field], list) or not case[field]:
            raise ValueError(f"{path.name}: {field} must be a non-empty list")
    policy = case.get("evaluation")
    if policy:
        required = {"applicable_criteria", "minimum_total", "mandatory_twos"}
        if required - set(policy):
            raise ValueError(f"{path.name}: evaluation missing required fields")
        unknown = set(policy["applicable_criteria"]) - criterion_ids
        if unknown:
            raise ValueError(f"{path.name}: unknown criteria: {sorted(unknown)}")
        if not set(policy["mandatory_twos"]).issubset(policy["applicable_criteria"]):
            raise ValueError(f"{path.name}: mandatory_twos must be applicable")
        maximum = 2 * len(policy["applicable_criteria"])
        if not 0 <= policy["minimum_total"] <= maximum:
            raise ValueError(f"{path.name}: minimum_total outside 0..{maximum}")


def policy_for(rubric, case):
    if case.get("evaluation"):
        return case["evaluation"]
    return {
        "applicable_criteria": [item["id"] for item in rubric["criteria"]],
        "minimum_total": rubric["pass_conditions"]["minimum_total"],
        "mandatory_twos": rubric["pass_conditions"]["mandatory_twos"],
    }


def score_judgment(rubric, case, judgment):
    policy = policy_for(rubric, case)
    scores = judgment.get("scores", {})
    normalized = {}
    for criterion in policy["applicable_criteria"]:
        item = scores.get(criterion)
        if not isinstance(item, dict) or item.get("score") not in (0, 1, 2):
            raise ValueError(f"{case['id']}: invalid score for {criterion}")
        normalized[criterion] = {
            "score": item["score"],
            "reason": str(item.get("reason", "")),
        }
    total = sum(item["score"] for item in normalized.values())
    failures = judgment.get("automatic_failures", [])
    passed = (
        not failures
        and total >= policy["minimum_total"]
        and all(normalized[item]["score"] == 2 for item in policy["mandatory_twos"])
    )
    return {
        "scores": normalized,
        "total": total,
        "maximum": 2 * len(normalized),
        "automatic_failures": failures,
        "passed": passed,
        "policy": policy,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="Case id; repeatable")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--emit-prompts", action="store_true", help="Emit JSONL packets for an external agent/judge harness")
    parser.add_argument("--judgments-dir", help="Directory containing <case-id>.json judge outputs")
    parser.add_argument("--output")
    args = parser.parse_args()

    rubric = load_json_yaml(ROOT / "evals/rubric.yaml")
    criterion_ids = {item["id"] for item in rubric["criteria"]}
    case_paths = sorted((ROOT / "evals/cases").glob("*.yaml"))
    cases = []
    for path in case_paths:
        case = load_json_yaml(path)
        validate_case(case, path, criterion_ids)
        cases.append(case)

    if args.case:
        requested = set(args.case)
        cases = [case for case in cases if case["id"] in requested]
        missing = requested - {case["id"] for case in cases}
        if missing:
            parser.error(f"unknown cases: {', '.join(sorted(missing))}")

    if args.emit_prompts:
        for case in cases:
            packet = {
                "instruction": "Use $eliot-global-job-intelligence to solve the case. Return traceable decisions and gate outcomes.",
                "case": case,
                "rubric": rubric,
                "judge_output_schema": {
                    "scores": {criterion: {"score": "0|1|2", "reason": "traceable reason"} for criterion in policy_for(rubric, case)["applicable_criteria"]},
                    "automatic_failures": [],
                },
            }
            print(json.dumps(packet, ensure_ascii=False))
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    if args.judgments_dir:
        result_items = []
        judgments_dir = Path(args.judgments_dir)
        for case in cases:
            judgment = json.loads((judgments_dir / f"{case['id']}.json").read_text(encoding="utf-8"))
            result_items.append({"case_id": case["id"], **score_judgment(rubric, case, judgment)})
        result = {
            "schema_version": 1,
            "run_type": "behavioral-evaluation",
            "skill_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            "run_at": now.isoformat(),
            "results": result_items,
            "passed": all(item["passed"] for item in result_items),
        }
    else:
        result = {
            "schema_version": 1,
            "run_type": "structural-validation",
            "skill_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            "run_at": now.isoformat(),
            "valid_cases": len(cases),
            "case_ids": [case["id"] for case in cases],
            "passed": True,
            "note": "Schema validation only; use --emit-prompts with an external harness for behavioral evaluation.",
        }

    if not args.validate_only or args.output:
        output = Path(args.output) if args.output else ROOT / "evals/results" / f"{now.date().isoformat()}-{result['run_type']}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

