# Mandatory Browser Capability Gate

Run before every authenticated, dynamic-platform, or web-AI branch. Documentation, remembered selectors, a prior run, or a tool registry is not proof of current capability.

## Platform and orchestration

### macOS preferred path

Use EGO Browser with the `ego-browser` Skill. For a Standard or Deep run, split only independent evidence jobs—such as company facts, competitor mechanisms, local-market signals, and creator/prospect samples—into separate EGO Task Spaces or parallel agent subtasks. Give each branch a bounded question and its own browser space, then converge on original URLs and deduplicate shared sources before synthesis.

Do not parallelize steps that write the same file, depend on the previous answer, require one shared user decision, or could compete for publication/login actions. Keep login, CAPTCHA, 2FA, payment, consent, and final publication under one controlled branch.

### Windows fallback

Use Browser Use together with Web Access. This Windows path currently cannot provide the same isolated multi-window parallel workflow as EGO, including EGO-equivalent task spaces and inherited login-state separation. Default to sequential or small-batch research, use Chrome/Edge remote debugging only when configured, and verify after every meaningful action. Mark the browser branch DEGRADED when the required authenticated or dynamic evidence cannot be recovered reliably.

## Gate sequence

1. Declare required capabilities: navigation, semantic readback, DOM evaluation, visual capture, authenticated state, user handoff, upload, or editor input.
2. Run the adapter's harmless public-page smoke test.
3. Invoke each required helper harmlessly; record runtime behavior.
4. On the target service, discover the current visible `textarea`, `contenteditable`, or appropriate text input from live state.
5. Insert a disposable nonsensitive marker, read it back from the intended surface, clear it, and verify empty state before entering a real prompt.
6. Verify visible account, model/mode, feature, target domain, and authentication state.
7. Use user handoff for login, CAPTCHA, 2FA, payment, consent, or ambiguous account selection.
8. Record PASS, DEGRADED, or FAIL before research.

## Public evidence screenshot protocol

When a role opportunity brief will be created, capture 2–6 screenshots while the original decision-relevant pages are open. Prefer the visible page area that directly supports the observation; retain source branding or context without filling the image with unrelated browser chrome. Record the source name, direct URL, observation date, human caption, relative file path, and public-safety decision in `work/evidence-screenshots.json`.

Do not capture or publish login state, account identifiers, notifications, cookies, browser profiles, private dashboards, personal messages, hidden contacts, or unrelated tabs. Do not use search snippets or AI-answer pages as screenshot evidence. If the page cannot be captured safely or legibly, keep the direct link in the audit layer and omit the image from the company-facing brief.

## Record

```text
Adapter/version and verified date:
Target service/URL:
Required capabilities:
Navigation proof:
Semantic readback proof:
DOM evaluation proof:
Visual capture proof/not required:
Visible editor discovered:
Disposable write/readback/clear:
Authentication/mode/account:
Fallback and claim restrictions:
Gate: PASS | DEGRADED | FAIL
```

- **PASS:** every required capability works live.
- **DEGRADED:** a named fallback preserves a narrower, defensible conclusion; list excluded claims.
- **FAIL:** block the branch and use open-web evidence, another verified adapter, or user handoff.

Visual capture is required only when visual state materially supports a claim. Never silently continue after a failed capability. Never use clipboard fallbacks that could overwrite user data without authorization. Re-observe after meaningful actions; an empty editor alone does not prove submission.
