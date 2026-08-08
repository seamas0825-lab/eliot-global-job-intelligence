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
AUDIT_ID = re.compile(r"\b(?:EXP|AST|FIT|CLM|SRC|SMP|GAP|BRAND|CAM|TOOL|OPS|ANS|CON)-\d{3}\b", re.I)
ACRONYMS = {
    "KOL": "Key Opinion Leader",
    "KPI": "Key Performance Indicator",
    "GMV": "Gross Merchandise Value",
    "ROI": "Return on Investment",
    "ROAS": "Return on Ad Spend",
    "CTR": "Click-Through Rate",
    "CVR": "Conversion Rate",
    "CPM": "Cost per Mille",
    "CPC": "Cost per Click",
    "UGC": "User-Generated Content",
    "ICP": "Ideal Customer Profile",
    "CRM": "Customer Relationship Management",
    "DTC": "Direct-to-Consumer",
    "CTA": "Call to Action",
    "SKU": "Stock Keeping Unit",
    "AOV": "Average Order Value",
    "CAC": "Customer Acquisition Cost",
    "LTV": "Lifetime Value",
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
            if "可以直接说" in match.group(2) or "自然回答" in match.group(2):
                active = {"heading": match.group(2), "start": line_number, "lines": []}
            continue
        if active is not None:
            active["lines"].append((line_number, line))
    if active:
        sections.append(active)
    return sections


def lint(path, glossary_path=None):
    text = path.read_text(encoding="utf-8")
    glossary_path = glossary_path or path.with_name("GLOSSARY.md")
    glossary = glossary_path.read_text(encoding="utf-8") if glossary_path.exists() else ""
    sections = candidate_sections(text)
    failures = []
    technical_heading = re.search(r"^#{1,6}\s+.*CANDIDATE SAYS", text, re.I | re.M)
    if technical_heading:
        failures.append({
            "type": "technical_reader_heading",
            "line": text[:technical_heading.start()].count("\n") + 1,
            "message": "Use a natural heading such as ‘可以直接说’, not CANDIDATE SAYS.",
        })
    if not re.search(r"^#{1,6}\s+.*(?:10\s*分钟|10[- ]minute)", text, re.I | re.M):
        failures.append({
            "type": "missing_priority_ladder",
            "line": 1,
            "message": "Start with a 10-minute priority ladder containing P0/P1/P2 guidance.",
        })
    if not re.search(r"^#{1,6}\s+.*(?:乱序|out[- ]of[- ]order|nonlinear|random[- ]order)", text, re.I | re.M):
        failures.append({
            "type": "missing_nonlinear_router",
            "line": 1,
            "message": "Add an out-of-order question router by interviewer intent.",
        })
    leaked = sorted(set(AUDIT_ID.findall(text)))
    if leaked:
        failures.append({
            "type": "reader_facing_id_leak",
            "line": 1,
            "message": f"Move audit IDs out of the reader-facing cheatsheet: {leaked[:8]}",
        })
    combined = text + "\n" + glossary
    for acronym, expansion in ACRONYMS.items():
        if re.search(rf"\b{acronym}\b", text) and expansion.lower() not in combined.lower():
            failures.append({
                "type": "unexplained_acronym",
                "line": 1,
                "message": f"Explain {acronym} on first use or in GLOSSARY.md ({expansion}).",
            })
    if not sections:
        failures.append({
            "type": "missing_candidate_says_sections",
            "line": 1,
            "message": "Mark candidate-ready speech with a natural heading such as ‘可以直接说’.",
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
    parser.add_argument("--glossary", type=Path)
    args = parser.parse_args()
    sections, failures = lint(args.path, args.glossary)
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
