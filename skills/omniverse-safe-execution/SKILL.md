---
name: omniverse-safe-execution
description: Execute mutating Omniverse Python idempotently with scoped snapshots, rollback, and partial-mutation tracking.
---

# Omniverse Safe Execution

Use for every stage-mutating plan step.

## Protocol

1. Require passing preflight and packaged code tied to the same step and stage snapshot.
2. Snapshot the authored layer or exact target paths needed for recovery.
3. Use stable paths and update compatible prims; do not create suffixed duplicates on retry unless copies are requested.
4. Execute once, capture output, then validate independently.
5. On failure, record whether mutations occurred and roll back the step scope when supported and safe.
6. Do not describe a failed run as an unchanged stage unless snapshot comparison proves it.

Return `ExecutionResult` with `status`, `code_hash`, `changed_paths`, `partial_mutation`, `rollback_status`, `interpreter_output`, and validation evidence.
