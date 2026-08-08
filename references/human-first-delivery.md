# Human-first Delivery

Keep evidence rigor backstage and make every reader-facing artifact understandable without knowing the Skill's schema.

## Contents

- Separate three surfaces
- Build the candidate memory ladder
- Prepare for nonlinear interviews
- Explain abbreviations
- Make HTML the primary reading layer
- Create the employer-facing layer
- Validate the reader layer

## Separate three surfaces

| Surface | Reader | Purpose | May show stable IDs? |
| --- | --- | --- | --- |
| Audit layer | Agent or reviewer | Preserve joins, truth boundaries, source records, and validation | Yes |
| Candidate layer | Job seeker | Memorize priorities, navigate questions, and answer naturally | No |
| Employer layer | Interviewer or hiring team | See researched judgment and a bounded prospective work sample | No |

Store `EXP-001`, `AST-001`, `CLM-001`, `SRC-001`, and similar keys in CSV or YAML under `work/`. Do not print them in reader-facing Markdown, HTML, tables, headings, badges, or spoken answers. Use ordinary labels such as “内容复盘经历”, “公开账号数据”, or “品牌案例” when a human label is needed.

## Build the candidate memory ladder

Put these sections at the beginning of `INTERVIEW_CHEATSHEET.md` in this order:

1. **面试前 10 分钟:** the three messages the candidate must remember, the one-sentence positioning, the two strongest stories, and the two risks that must not be overstated.
2. **如果只剩 3 分钟:** one company sentence, one role sentence, three answer anchors, and three reverse-interview questions.
3. **乱序提问导航:** route by interviewer intent rather than by question order.
4. **Answer cards:** reusable stories and methods, then longer reference material.

Assign each item a priority:

- **P0 — must remember:** forgetting it would materially weaken or contradict the application.
- **P1 — should remember:** useful for the most likely questions.
- **P2 — lookup only:** detail that belongs in the dashboard, not working memory.

Do not create more than five P0 items or ten combined P0/P1 answer anchors.

## Prepare for nonlinear interviews

Classify any incoming question within a few seconds:

| Interviewer intent | Candidate should retrieve |
| --- | --- |
| Motivation and fit | company view + positioning anchor |
| Experience and ownership | strongest relevant story |
| Method and prioritization | operating-chain or decision anchor |
| Results and data | metric definition + learning anchor |
| Failure or conflict | reflection and correction anchor |
| Scenario or case | clarify → prioritize → propose → measure |
| Company or market | verified insight + implication + question |
| Gap or unfamiliar tool | closest evidence + honest gap + first validation step |

Use this response protocol:

```text
Direct answer → one anchor → role relevance → stop
```

If the wording is ambiguous, ask one short clarification question. If interrupted or redirected, answer the new intent directly instead of trying to finish the memorized script. Add bridge phrases that let the candidate reuse an anchor without sounding evasive.

## Explain abbreviations

On first meaningful use, write the full term and a short plain-language explanation, for example:

```text
KOL（Key Opinion Leader，关键意见领袖，通常指在特定领域有影响力的内容创作者）
GMV（Gross Merchandise Value，成交总额）
```

Also create `GLOSSARY.md` with only the terms that actually appear in the package. Explain what the term means in this role, not only its dictionary expansion. Prefer Chinese or ordinary verbs where an abbreviation adds no value.

## Make HTML the primary reading layer

Keep Markdown and CSV as source files, then run:

```bash
python scripts/build_dashboard.py <run-root>
```

Deliver `JOB_SEARCH_DASHBOARD.html` as the candidate's primary entry point. Use an Apple-inspired design language—large type, generous whitespace, neutral surfaces, restrained blue accents, subtle depth, and direct navigation—without copying a specific Apple page. It must be standalone, responsive, keyboard accessible, usable offline, and able to open the system print dialog for PDF export. It should contain:

- the P0/P1 memory ladder first;
- the nonlinear question router;
- visual evidence counts and filters;
- human-readable benchmark cards and direct links;
- the complete brief, cheatsheet, glossary, and other Markdown outputs;
- no visible audit IDs.

The CSV remains the structured evidence ledger and import source, but do not make the candidate open it to understand the research.

## Create the employer-facing layer

Create `ROLE_OPPORTUNITY_BRIEF.md` only after the Candidate Truth Gate. Then generate `ROLE_OPPORTUNITY_BRIEF.html`. Make it a second standalone file with its own embedded styling and PDF export control. Do not link the two HTML files to each other; the candidate decides which file to share.

Do not label the page “for the interviewer,” “candidate work sample,” “prospective,” or “not internal access.” Those are internal control concepts that make a professional brief look self-conscious. Use a business title such as `[Company] · [Role] Opportunity Brief`. Put a compact “Scope and assumptions” section at the end: explain that priorities use externally observable signals and should be calibrated with the company's goals, resources, baselines, and constraints before execution.

During research, capture 2–6 screenshots for the most decision-relevant public observations. Use original company, platform, ad, product, creator, or public discussion pages—not search snippets or AI-answer pages. Record each image in `work/evidence-screenshots.json` with the internal record ID, relative file path, human caption, source name, direct URL, observation date, and `include_in_role_brief` flag. Crop or frame the evidence so the supported signal is legible while retaining enough context to identify the source. Exclude login state, personal data, notifications, cookies, browser profiles, private dashboards, and unrelated browser chrome.

The builder embeds approved PNG, JPEG, or WebP screenshots as data URIs, so the HTML and exported PDF remain self-contained. Display the human caption, source name, date, and direct link; never display the internal record ID.

Keep it explainable in five minutes and include:

1. role and business understanding;
2. three evidence-backed observations;
3. one reconstructed benchmark mechanism;
4. a bounded 30-day proposal;
5. measurement and decision rules;
6. assumptions, missing internal data, and questions for the company;
7. direct public sources and 2–6 evidence screenshots.

Never include the resume, candidate evidence ledger, coach notes, prohibited claims, private files, hidden contact data, or claims of internal access. Keep the title and opening copy business-facing; communicate the public-information boundary only through the compact scope-and-assumptions section at the end. Default to HTML; create a PPT only when the user requests it and an appropriate presentation tool is available.

## Validate the reader layer

For Standard or Deep runs, execute:

```bash
python scripts/build_dashboard.py <run-root>
python scripts/validate_run_package.py <run-root> --require-state --require-reader-layer
```

Fail delivery when priority/navigation sections are missing, reader-facing IDs leak, abbreviations are unexplained, or the dashboard cannot be generated from the run package.
