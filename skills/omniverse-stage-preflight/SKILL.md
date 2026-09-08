---
name: omniverse-stage-preflight
description: Inspect an Omniverse USD stage before mutation, verifying units, axes, editability, hierarchy, and step preconditions.
---

# Omniverse Stage Preflight

Run immediately before an authoring step. Prefer the supplied global `stage`; do not fetch a different stage when the execution contract provides one.

## Checks

- Stage validity and writable edit target.
- Up axis, meters-per-unit, and plan conversion factors.
- Required parents and target path state: absent, compatible existing, or conflicting existing.
- Expected type, instanceability, references, variants, active state, and load state.
- Relevant outliner drift since the plan snapshot.

Return a non-mutating `PreflightResult` with `ok`, `stage_facts`, `path_states`, `conversion_factors`, `warnings`, and `blocking_errors`.
