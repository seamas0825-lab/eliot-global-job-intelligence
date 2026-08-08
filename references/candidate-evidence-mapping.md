# Candidate Evidence Mapping and Truth Boundary

Candidate facts come from the candidate, supplied artifacts, or directly inspectable public work. The agent may normalize and translate them but may not complete missing details by plausibility.

## Ownership vocabulary

| Candidate statement | Meaning allowed |
| --- | --- |
| `independently_owned` | accountable for choices and result |
| `participated` | executed a defined portion with others |
| `assisted` | supported another owner |
| `observed` | learned by proximity; no execution claim |
| `used` | actually operated the named tool or process |
| `aware_not_used` | understands conceptually, no hands-on claim |
| `planned_learning` | future intent only |
| `no_experience` | no defensible experience |

## Claim states

- **VERIFIED:** direct job-task match plus explainable evidence.
- **TRANSFERABLE:** different label/context but the same causal mechanism; state the difference.
- **LEARNING GAP:** plausible to learn, not yet evidenced.
- **DO NOT CLAIM:** false, contradictory, untraceable, or likely to mislead.

## Evidence assets

Accept resumes as claims, not proof by themselves. Stronger assets include work files, public accounts, dashboards or screenshots with understandable definitions, briefs, research sheets, messages with sensitive data removed, CRM records, process docs, stakeholder feedback, and a live explanation of decisions and failures.

For every metric record:

```text
metric name; exact definition; source; date range; baseline;
candidate contribution; confounders; whether independently verifiable
```

If the definition or source is unclear, remove precision or mark the metric unverified.

## Fit-matrix row

```text
FIT ID:
JD requirement:
Actual operating task:
Candidate experience ID:
Ownership level:
Transfer mechanism:
Evidence asset IDs:
Gap:
Claim state:
Safe Chinese wording:
Safe English wording:
Likely follow-up:
```

The fit matrix and “safe wording” are audit-side controls. Keep their IDs in `work/answer-evidence-map.yaml`; do not paste them into the reader-facing cheatsheet or dashboard. Use human story names on the candidate surface, set the truth boundary backstage, then rewrite the answer for interviewer intent and natural first-person delivery.

## Automatic blocks

Block and rewrite any claim that:

- invents a project, client, creator, platform, tool, budget, metric, or result;
- changes participation into independent ownership;
- changes a lead, inquiry, meeting, or support role into closed revenue;
- changes views, engagement, or traffic into sales conversion;
- changes awareness into proficiency;
- hides contradictory dates, numbers, or responsibilities;
- uses “we” to imply personal ownership that cannot be specified.

## Resolving contradictions

Show the conflicting statements, ask the candidate which is accurate, and keep the claim blocked until resolved. Do not average numbers or select the version that fits the JD best.

Truthfulness should be achieved upstream through claim selection, not by making every spoken answer repeat a disclaimer. Keep verification status, metric warnings, prohibited claims, and stable IDs in the internal answer map unless the interviewer directly asks about the underlying fact.
