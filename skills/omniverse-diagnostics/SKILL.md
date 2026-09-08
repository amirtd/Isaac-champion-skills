---
name: omniverse-diagnostics
description: Normalize shared Omniverse workflow errors, warnings, alerts, validation failures, and retry outcomes.
---

# Omniverse Diagnostics

This is the single cross-workflow diagnostic model. Other skills emit events here rather than redefining error handling.

## Event model

Every event contains `event_id`, `run_id`, `step_id`, `phase`, `severity`, `category`, `message`, `source`, `code_hash`, `affected_paths`, `partial_mutation`, `retryable`, `normalized_signature`, and `evidence`.

Severities are `info`, `warning`, `error`, and `alert`. Reserve `alert` for possible persistent corruption, unsafe continuation, rollback failure, or a required user decision.

## Aggregation invariants

- Derive top-level counts from recorded events.
- A failed interpreter run increments execution errors even when validation was skipped.
- `skipped`, `passed`, `failed`, and `not_applicable` are distinct validation states.
- Preserve the original traceback while deduplicating repeated normalized signatures.
- Report partial mutation and rollback state with the error.
- A retry-limit event references all prior attempt ids and the final blocking cause.

Return machine-readable and user-facing summaries grounded in the same events.
