# Deliverables

Use only the artifacts needed for the run. A Standard Run produces three files. Join all files with stable IDs.

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

IDs are relational keys, not decorative labels. Every `SRC/SMP/BRAND/CAM/TOOL` ID referenced by a published Markdown artifact must resolve to exactly one CSV row. Every `EXP/AST/CLM/CON` ID referenced by candidate-facing coach notes must resolve to the candidate-evidence record. Never reuse one ID for different objects or create a display-only alias that is absent from the evidence packet.

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

Keep readable in ten minutes and separate two surfaces:

```text
CANDIDATE SAYS: speakable answer with no IDs or control labels
COACH NOTES: evidence IDs, truth boundary, follow-up risk, and missing proof
```

Include:

- one-sentence company and role models;
- three priority business problems;
- five evidenced strengths and their IDs;
- three honest gaps expressed naturally rather than as audit disclaimers;
- 60-second introduction;
- up to five core stories with 30/60/120-second variants where useful;
- ten high-probability questions with follow-up risks;
- five accurate English phrases;
- five reverse-interview questions;
- prohibited or inflated claims;
- work-sample talking points.

Every experience answer must link to `EXP`, `AST`, or inspectable public evidence IDs in coach notes. Mark method-only responses as hypothetical in coach notes only. Candidate speech must not contain IDs, schema labels, source citations, verification warnings, or coaching instructions.

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

## Optional internal artifacts

- `job-run-state.yaml`
- `ROLE_OPERATING_MAP.md`
- `CANDIDATE_FIT_MATRIX.md`
- `CLAIM_BOUNDARY.md`
- `MOCK_INTERVIEW.md`
- role-specific shortlist CSV
- prospective work sample

Verify all created files exist, links open when access permits, CSV rows match headers, and blocked claims do not appear as achievements. For Standard or Deep runs, execute:

```bash
python scripts/validate_run_package.py <run-root> --require-state
```

The run root normally contains `outputs/` and `work/`. A failed validation blocks delivery; do not mark a package structurally valid by manual assertion after the validator reports unresolved IDs or schema drift.

Before delivery, run a final GPT-style editorial review over the complete evidence packet even if another reasoning system performs it: check competitive coverage, source integrity, interviewer intent, spoken-answer naturalness, and cross-file consistency. This is a review role, not a new evidence source.

Run `python scripts/lint_interview_cheatsheet.py <path/to/INTERVIEW_CHEATSHEET.md>` and block delivery on any candidate-speech violation.
