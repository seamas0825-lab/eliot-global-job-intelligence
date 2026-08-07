# Mandatory Browser Capability Gate

Run before every authenticated, dynamic-platform, or web-AI branch. Documentation, remembered selectors, a prior run, or a tool registry is not proof of current capability.

## Gate sequence

1. Declare required capabilities: navigation, semantic readback, DOM evaluation, visual capture, authenticated state, user handoff, upload, or editor input.
2. Run the adapter's harmless public-page smoke test.
3. Invoke each required helper harmlessly; record runtime behavior.
4. On the target service, discover the current visible `textarea`, `contenteditable`, or appropriate text input from live state.
5. Insert a disposable nonsensitive marker, read it back from the intended surface, clear it, and verify empty state before entering a real prompt.
6. Verify visible account, model/mode, feature, target domain, and authentication state.
7. Use user handoff for login, CAPTCHA, 2FA, payment, consent, or ambiguous account selection.
8. Record PASS, DEGRADED, or FAIL before research.

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

