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


def candidate_resume_anchors(path):
    if not path or not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    values = []
    for key in ("organization_or_context", "title_or_role"):
        for match in re.finditer(rf"^\s*{key}:\s*(.+?)\s*$", text, re.M):
            value = match.group(1).split(" #", 1)[0].strip().strip("\"'")
            if value and " | " not in value and len(value) >= 2:
                values.append(value)
    return list(dict.fromkeys(values))


def default_candidate_evidence(path):
    candidate = path.parent.parent / "work" / "candidate-evidence.yaml"
    return candidate if candidate.exists() else None


def section_text(section):
    return "\n".join(line for _, line in section["lines"])


def lint(path, glossary_path=None, candidate_evidence_path=None):
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
    candidate_evidence_path = candidate_evidence_path or default_candidate_evidence(path)
    resume_anchors = candidate_resume_anchors(candidate_evidence_path)
    if resume_anchors and sections:
        introductions = [
            section for section in sections
            if re.search(r"自我介绍|self[- ]?introduction|introduce yourself", section["heading"], re.I)
        ]
        if not introductions:
            failures.append({
                "type": "missing_resume_grounded_introduction",
                "line": 1,
                "message": "A supplied resume requires a complete candidate-ready self-introduction.",
            })
        else:
            introduction = section_text(introductions[0])
            if not re.search(r"面试官.{0,8}(?:好|您好)|\b(?:hello|hi)\b", introduction, re.I):
                failures.append({
                    "type": "missing_introduction_greeting",
                    "line": introductions[0]["start"],
                    "message": "Open the primary self-introduction with a natural greeting.",
                })
            if not re.search(r"我(?:叫|姓|是)|\bmy name is\b|\bi(?:'m| am)\b", introduction, re.I):
                failures.append({
                    "type": "missing_introduction_identity",
                    "line": introductions[0]["start"],
                    "message": "Use a truthful spoken identity phrase such as ‘我叫’, ‘我姓’, or ‘我是’.",
                })
            intro_hits = [anchor for anchor in resume_anchors if anchor.lower() in introduction.lower()]
            minimum = min(2, len(resume_anchors))
            if len(intro_hits) < minimum:
                failures.append({
                    "type": "generic_self_introduction",
                    "line": introductions[0]["start"],
                    "message": f"Ground the introduction in at least {minimum} resume anchors; found {intro_hits}.",
                })
        for section in sections:
            spoken_section = section_text(section)
            hits = [anchor for anchor in resume_anchors if anchor.lower() in spoken_section.lower()]
            if not hits:
                failures.append({
                    "type": "generic_candidate_answer",
                    "line": section["start"],
                    "message": f"‘{section['heading']}’ needs a human-readable company or role anchor from candidate evidence.",
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
    parser.add_argument("--candidate-evidence", type=Path)
    args = parser.parse_args()
    sections, failures = lint(args.path, args.glossary, args.candidate_evidence)
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
