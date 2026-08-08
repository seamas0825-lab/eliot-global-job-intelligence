# Deliverables

Use only the artifacts needed for the run. Separate audit, candidate, and employer surfaces. A Standard Run keeps machine-readable evidence backstage and delivers one human-readable dashboard as the primary entry point. Follow [human-first delivery](human-first-delivery.md).

## Stable ID convention

- `SRC-###`: source
- `SMP-###`: benchmark sample
- `OPS-###`: operating-chain step
- `EXP-###`: candidate experience
- `AST-###`: candidate evidence asset
- `FIT-###`: fit-matrix row
- `CLM-###`: candidate claim
- `ANS-###`: interview answer
- `GAP-###`: access or evidence gap
- `BRAND-###`: competitor or analogous brand
- `CAM-###`: campaign or creator-program pattern
- `TOOL-###`: tool/platform landscape record

IDs are relational keys, not reader labels. Keep them in CSV or YAML audit files. Do not show them in candidate- or employer-facing Markdown/HTML. Every ID referenced by `work/answer-evidence-map.yaml` must resolve to exactly one evidence record. Never reuse one ID for different objects.

## JOB_INTELLIGENCE_BRIEF.md

1. One-page executive summary.
2. What the company and product actually do.
3. Why the company may be hiring now: facts versus inference.
4. Role outcome and Role Reality Gate.
5. Target market, local user/customer, language, platform, and norms.
6. Complete local operating chain.
7. Direct competitors, business-model peers, mechanism analogues, and at least one reconstructed campaign operating chain.
8. Role-specific samples plus relevant tool/platform landscape, artifacts, stakeholders, and handoffs.
9. KPIs, diagnostic metrics, and common failures.
10. Company/role contradictions and reversal evidence.
11. Candidate fit matrix.
12. Material gaps and prohibited claims.
13. Prospective first-30-day framework.
14. Sources, observation dates, uncertainty, access limits, and gate results.

## INTERVIEW_CHEATSHEET.md

Keep readable in ten minutes. Put the memory ladder and nonlinear question router before long answers. Do not show audit IDs anywhere in this reader-facing file.

Store answer-to-evidence joins, truth boundaries, follow-up risks, and missing proof in `work/answer-evidence-map.yaml`, not in the cheatsheet.

Include:

- P0/P1/P2 priorities and a three-minute fallback;
- one-sentence company and role models;
- three priority business problems;
- five evidenced strengths with human-readable proof labels;
- three honest gaps expressed naturally rather than as audit disclaimers;
- 60-second introduction;
- up to five core stories with 30/60/120-second variants where useful;
- a nonlinear router by interviewer intent and bridge phrases;
- ten high-probability questions with follow-up risks;
- five accurate English phrases;
- five reverse-interview questions;
- work-sample talking points.

Every experience answer must link to candidate evidence in the internal answer map. Mark method-only responses as hypothetical there. Candidate speech must not contain IDs, schema labels, source citations, verification warnings, or coaching instructions.

## GLOSSARY.md

Include only abbreviations or specialist terms that appear in the reader-facing package. On first use in the cheatsheet, add a short inline explanation; use the glossary for fuller role-specific meaning.

## JOB_SEARCH_DASHBOARD.html

Generate with `scripts/build_dashboard.py`. Make this the primary candidate-facing artifact. It combines Markdown and CSV into a responsive offline page with priority cards, question routing, visual evidence summaries, filters, direct links, and the complete readable package. Hide audit IDs from the rendered interface.

## EVIDENCE_AND_BENCHMARKS.csv

Required columns:

```text
record_id,sample_type,name,market,language,platform,url,observed_date,
source_role,relevance,direct_evidence,inference,key_mechanism,public_metrics,
risk,transfer_lesson,interview_use,confidence
```

Use RFC 4180-compatible CSV, UTF-8, one header row, one record per row, direct URLs, ISO dates, and blank cells for unknown values. Never write `0` for missing data.

Use only these `sample_type` values:

```text
benchmark_brand | campaign | program | creator | account | content | prospect |
ad | listing | tool_or_platform | expert_case | discussion | policy | source_asset
```

Use only these `source_role` values:

```text
official | native_behavior | candidate_claim | user_supplied_job | user_voice |
practitioner_voice | authoritative | reporting | vendor | ai_lead
```

The CSV must contain the evidence behind benchmark lessons, not only the hiring company and individual accounts. Keep enum fields exact; put qualifiers and source-specific detail in `direct_evidence`, `risk`, or `inference`, not inside enum values.

## Required internal audit artifacts for Standard/Deep

- `work/job-run-state.yaml`
- `work/candidate-evidence.yaml`
- `work/answer-evidence-map.yaml`
- `outputs/EVIDENCE_AND_BENCHMARKS.csv`

The CSV is a structured ledger and Feishu/Base import source. It is not the primary reading experience.

## Optional internal audit artifacts

- `work/ROLE_OPERATING_MAP.md`
- `work/CANDIDATE_FIT_MATRIX.md`
- `work/CLAIM_BOUNDARY.md`
- role-specific shortlist CSV under `work/`

## Optional reader-facing artifacts

- `outputs/MOCK_INTERVIEW.md` using human story names and no audit IDs
- `ROLE_OPPORTUNITY_BRIEF.md` and generated `ROLE_OPPORTUNITY_BRIEF.html`
- `work/evidence-screenshots.json` plus 2–6 public-safe source screenshots when a role brief is created

Verify all created files exist, links open when access permits, CSV rows match headers, and blocked claims do not appear as achievements. For Standard or Deep runs, execute:

```bash
python scripts/build_dashboard.py <run-root>
python scripts/validate_run_package.py <run-root> --require-state --require-reader-layer
```

The run root normally contains `outputs/` and `work/`. A failed validation blocks delivery; do not mark a package structurally valid by manual assertion after the validator reports unresolved IDs or schema drift.

Before delivery, run a final GPT-style editorial review over the complete evidence packet even if another reasoning system performs it: check competitive coverage, source integrity, interviewer intent, spoken-answer naturalness, and cross-file consistency. This is a review role, not a new evidence source.

Run `python scripts/lint_interview_cheatsheet.py <path/to/INTERVIEW_CHEATSHEET.md>` and block delivery on any candidate-speech violation.
