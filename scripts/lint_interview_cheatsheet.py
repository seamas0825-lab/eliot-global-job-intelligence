#!/usr/bin/env python3
"""Fail when coach-side control language leaks into candidate-speech sections."""

import argparse
import json
import re
import sys
from pathlib import Path


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FORBIDDEN = {
    "evidence_or_schema_id": re.compile(r"\b(?:EXP|AST|FIT|CLM|SRC|SMP|GAP)-?\d+\b", re.I),
    "internal_claim_state": re.compile(r"\b(?:BLOCKED|TRANSFERABLE|VERIFIED|HYPOTHETICAL(?:\s+APPROACH)?|DO NOT CLAIM|LEARNING GAP)\b", re.I),
    "research_meta_language": re.compile(r"本次材料|候选人陈述|原始后台和定义|补证|安全说法|这里要收窄|\bcoach notes?\b", re.I),
    "defensive_script": re.compile(r"我不会把(?:它|这|这个)|如果无法解释.{0,12}(?:不使用|不用)|我要明确边界"),
    "inline_source_citation": re.compile(r"\[(?:EXP|AST|FIT|CLM|SRC|SMP|GAP)[^\]]*\]", re.I),
}


def candidate_sections(text):
    sections = []
    active = None
    for line_number, line in enumerate(text.splitlines(), 1):
        match = HEADING.match(line)
        if match:
            if active:
                sections.append(active)
                active = None
            if "CANDIDATE SAYS" in match.group(2).upper():
                active = {"heading": match.group(2), "start": line_number, "lines": []}
            continue
        if active is not None:
            active["lines"].append((line_number, line))
    if active:
        sections.append(active)
    return sections


def lint(path):
    text = path.read_text(encoding="utf-8")
    sections = candidate_sections(text)
    failures = []
    if not sections:
        failures.append({
            "type": "missing_candidate_says_sections",
            "line": 1,
            "message": "Separate candidate-ready speech from coach notes with CANDIDATE SAYS headings.",
        })
    spoken = "\n".join(line for section in sections for _, line in section["lines"])
    for section in sections:
        for line_number, line in section["lines"]:
            for label, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    failures.append({
                        "type": label,
                        "line": line_number,
                        "message": line.strip()[:180],
                    })
    if spoken.count("我还没有") + spoken.count("我没有") > max(2, len(sections) // 2):
        failures.append({
            "type": "repeated_gap_disclaimer",
            "line": 1,
            "message": "Candidate speech repeats gap disclaimers too often; lead more answers with useful evidence.",
        })
    return sections, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    sections, failures = lint(args.path)
    result = {
        "file": str(args.path),
        "candidate_speech_sections": len(sections),
        "failures": failures,
        "passed": not failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

