---
name: omniverse-usd-validation
description: Validate authored Omniverse USD steps with structured evidence for paths, schemas, transforms, bounds, hierarchy, and clearances.
---

# Omniverse USD Validation

Validate the active step's acceptance contract plus invariants needed to detect collateral changes. For footprint, flow counts, reach envelopes, and aisle contracts, use `omniverse-layout-validation` after this skill when layout artifacts exist.

## Checks

- Prim existence, validity, active state, and exact schema compatibility.
- Parent-child hierarchy and operation-specific path counts.
- Local and world transforms.
- Exact dimensions with declared tolerances; non-zero bounds alone are insufficient when dimensions are specified.
- Surface contact, containment, overlap, reach, and clearance constraints when present in the plan.
- Unexpected prims or changed paths outside the step scope.

Return an expression-safe `ValidationResult` dictionary with `status`, `checks`, `checked_prims`, `failed_prims`, `warnings`, and measured `evidence`. Do not rely solely on terminal assertions.
