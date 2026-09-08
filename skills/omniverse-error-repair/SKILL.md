---
name: omniverse-error-repair
description: Classify and repair failed Omniverse Python executions while preventing ineffective duplicate retries.
---

# Omniverse Error Repair

Use the smallest relevant evidence set: code, traceback, executor contract, changed paths, and failed checks.

## Classification

Classify first as `packaging`, `python_syntax`, `executor_contract`, `usd_api`, `stage_state`, `units_or_transform`, `validation`, or `unknown`. An `eval(last_line)` failure on a valid statement is an executor-contract problem, not malformed assertion syntax.

## Retry policy

- State the causal hypothesis and expected observable change.
- Produce a minimal semantic patch; comments or renamed temporary variables are not progress.
- Compare code hash and behavior with prior attempts.
- Do not retry unchanged code for the same normalized error signature.
- Re-run RAG only when missing API knowledge caused the failure.
- Stop after two ineffective repairs, or sooner when mutation safety is uncertain.

Use `omniverse-diagnostics` for event recording; do not define a second error taxonomy.
