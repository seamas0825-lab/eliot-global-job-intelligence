#!/usr/bin/env python3
"""Dependency-free validation for a generated job-intelligence run package."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from lint_interview_cheatsheet import lint as lint_interview


HEADERS = [
    "record_id", "sample_type", "name", "market", "language", "platform",
    "url", "observed_date", "source_role", "relevance", "direct_evidence",
    "inference", "key_mechanism", "public_metrics", "risk",
    "transfer_lesson", "interview_use", "confidence",
]
SAMPLE_TYPES = {
    "benchmark_brand", "campaign", "program", "creator", "account", "content",
    "prospect", "ad", "listing", "tool_or_platform", "expert_case",
    "discussion", "policy", "source_asset",
}
SOURCE_ROLES = {
    "official", "native_behavior", "candidate_claim", "user_supplied_job",
    "user_voice", "practitioner_voice", "authoritative", "reporting", "vendor",
    "ai_lead",
}
CONFIDENCE = {"low", "medium", "high"}
PREFIX_BY_TYPE = {
    "benchmark_brand": "BRAND",
    "campaign": "CAM",
    "program": "CAM",
    "tool_or_platform": "TOOL",
    "policy": "SRC",
    "source_asset": "SRC",
    "creator": "SMP",
    "account": "SMP",
    "content": "SMP",
    "prospect": "SMP",
    "ad": "SMP",
    "listing": "SMP",
    "expert_case": "SMP",
    "discussion": "SMP",
}
PUBLIC_ID = re.compile(r"\b(?:SRC|SMP|BRAND|CAM|TOOL)-\d{3}\b")
CANDIDATE_ID = re.compile(r"\b(?:EXP|AST|CLM|CON)-\d{3}\b")
ID_SHAPE = re.compile(r"^(SRC|SMP|BRAND|CAM|TOOL)-\d{3}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HTTP_URL = re.compile(r"^https?://[^\s]+$")


def locate_dirs(run_root):
    run_root = run_root.resolve()
    if (run_root / "outputs").is_dir():
        return run_root / "outputs", run_root / "work"
    return run_root, run_root.parent / "work"


def candidate_definitions(path):
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    patterns = [
        r"experience_id:\s*[\"']?(EXP-\d{3})",
        r"asset_id:\s*[\"']?(AST-\d{3})",
        r"claim_id:\s*[\"']?(CLM-\d{3})",
        r"contradiction_id:\s*[\"']?(CON-\d{3})",
    ]
    return {match for pattern in patterns for match in re.findall(pattern, text)}


def state_scalar(text, key):
    match = re.search(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n#]+)", text, re.M)
    return match.group(1).strip() if match else None


def validate(run_root, require_state=False):
    output_dir, work_dir = locate_dirs(run_root)
    failures, warnings = [], []
    required = {
        "brief": output_dir / "JOB_INTELLIGENCE_BRIEF.md",
        "cheatsheet": output_dir / "INTERVIEW_CHEATSHEET.md",
        "csv": output_dir / "EVIDENCE_AND_BENCHMARKS.csv",
    }
    for label, path in required.items():
        if not path.exists():
            failures.append(f"missing required {label}: {path}")
    if failures:
        return failures, warnings, {"output_dir": str(output_dir)}

    with required["csv"].open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if reader.fieldnames != HEADERS:
            failures.append(f"CSV header mismatch: {reader.fieldnames}")

    ids = []
    for index, row in enumerate(rows, 2):
        if None in row:
            failures.append(f"CSV row {index} has more cells than headers")
            continue
        record_id = (row.get("record_id") or "").strip()
        ids.append(record_id)
        sample_type = (row.get("sample_type") or "").strip()
        source_role = (row.get("source_role") or "").strip()
        confidence = (row.get("confidence") or "").strip()
        date = (row.get("observed_date") or "").strip()
        url = (row.get("url") or "").strip()
        if not ID_SHAPE.fullmatch(record_id):
            failures.append(f"CSV row {index} invalid record_id: {record_id!r}")
        if sample_type not in SAMPLE_TYPES:
            failures.append(f"CSV row {index} noncanonical sample_type: {sample_type!r}")
        elif record_id and record_id.split("-", 1)[0] != PREFIX_BY_TYPE[sample_type]:
            failures.append(f"CSV row {index} ID/type mismatch: {record_id} for {sample_type}")
        if source_role not in SOURCE_ROLES:
            failures.append(f"CSV row {index} noncanonical source_role: {source_role!r}")
        if confidence not in CONFIDENCE:
            failures.append(f"CSV row {index} invalid confidence: {confidence!r}")
        if not ISO_DATE.fullmatch(date):
            failures.append(f"CSV row {index} invalid observed_date: {date!r}")
        if url and not HTTP_URL.fullmatch(url):
            failures.append(f"CSV row {index} URL must be a direct http(s) URL: {url!r}")

    duplicates = sorted(record_id for record_id in set(ids) if ids.count(record_id) > 1)
    if duplicates:
        failures.append(f"duplicate CSV record IDs: {duplicates}")

    markdown_paths = sorted(output_dir.glob("*.md"))
    markdown_text = "\n".join(path.read_text(encoding="utf-8") for path in markdown_paths)
    public_refs = set(PUBLIC_ID.findall(markdown_text))
    unresolved_public = sorted(public_refs - set(ids))
    if unresolved_public:
        failures.append(f"public IDs referenced in Markdown but absent from CSV: {unresolved_public}")
    unreferenced = sorted(set(ids) - public_refs)
    if unreferenced:
        warnings.append(f"CSV IDs not referenced by Markdown: {len(unreferenced)}")

    candidate_path = work_dir / "candidate-evidence.yaml"
    candidate_refs = set(CANDIDATE_ID.findall(markdown_text))
    candidate_defs = candidate_definitions(candidate_path)
    if candidate_refs and not candidate_path.exists():
        failures.append(f"candidate IDs are referenced but evidence file is missing: {candidate_path}")
    unresolved_candidate = sorted(candidate_refs - candidate_defs)
    if unresolved_candidate:
        failures.append(
            "candidate IDs referenced in Markdown but absent from candidate evidence: "
            f"{unresolved_candidate}"
        )

    _, interview_failures = lint_interview(required["cheatsheet"])
    failures.extend(
        f"interview lint {item['type']} at line {item['line']}: {item['message']}"
        for item in interview_failures
    )

    state_path = work_dir / "job-run-state.yaml"
    if require_state and not state_path.exists():
        failures.append(f"required run state is missing: {state_path}")
    if state_path.exists():
        state = state_path.read_text(encoding="utf-8")
        for key in (
            "package_validation", "cross_file_ids_valid", "candidate_fact_readiness",
            "interview_readiness", "validation_failures",
        ):
            if not re.search(rf"^\s*{re.escape(key)}:", state, re.M):
                failures.append(f"run state missing deliverable readiness field: {key}")
        sample_unit = state_scalar(state, "sample_unit")
        collected = state_scalar(state, "collected_count")
        if sample_unit and collected and collected.isdigit():
            target_type = "benchmark_brand" if sample_unit == "competitor" else sample_unit
            actual = sum(row.get("sample_type") == target_type for row in rows)
            if actual != int(collected):
                failures.append(
                    f"sample count drift: state collected_count={collected}, "
                    f"CSV {target_type} rows={actual}"
                )

    summary = {
        "run_root": str(run_root.resolve()),
        "output_dir": str(output_dir),
        "csv_rows": len(rows),
        "csv_ids": len(set(ids)),
        "markdown_files": len(markdown_paths),
        "public_references": len(public_refs),
        "candidate_references": len(candidate_refs),
    }
    return failures, warnings, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--require-state", action="store_true")
    args = parser.parse_args()
    failures, warnings, summary = validate(args.run_root, args.require_state)
    result = {
        "validator": "eliot-global-job-intelligence/run-package",
        "summary": summary,
        "failures": failures,
        "warnings": warnings,
        "passed": not failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
