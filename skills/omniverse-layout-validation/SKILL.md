---
name: omniverse-layout-validation
description: Validate an Omniverse stage against CellLayoutPlan, WarehouseLayoutIntent, MaterialFlowGraph, ReachTransferContract, and StorageLayout with measurable evidence. Produces LayoutValidationResult.
---

# Omniverse Layout Validation

Apply after `omniverse-usd-validation` when one or more layout artifacts were produced for the run. Measure layout contracts; do not re-check low-level USD schema rules (that is `omniverse-usd-validation`).

## Workflow

1. Collect active layout artifacts: `CellLayoutPlan`, `WarehouseLayoutIntent`, `MaterialFlowGraph`, `ReachTransferContract`, `StorageLayout`.
2. For each applicable check below, measure stage evidence (bounds, transforms, counts, distances).
3. Record pass/fail with numeric evidence—not viewport appearance alone.
4. Treat missing artifact fields as `not_applicable` or `blocked` with an open question—not as silent pass.
5. Emit diagnostics-compatible events for failures (`omniverse-diagnostics`).

## Checks

- Footprint containment: components/regions inside declared cell or warehouse extents.
- Clearance pairs: measured distance ≥ `min_clearance_m` when specified.
- Transfer-height deltas: within tolerance for each pair in `ReachTransferContract`.
- Zone non-overlap: warehouse zones do not occupy the same region unless allowed.
- Inbound/outbound counts and pairing: match `MaterialFlowGraph` quantity resolution.
- Reach-envelope containment: pick/place stations inside labeled envelope when envelope dims exist.
- Placeholder labeling: placeholder components not presented as production assets in evidence.
- Storage: runs inside zone; aisle widths ≥ minimum when both faces exist on stage.

## Output

Return a `LayoutValidationResult`. See [reference.md](reference.md) for schema and evidence table.

Required fields: `status`, `checks`, `evidence`, `failed`, `warnings`, `artifacts_used`.

Use statuses: `passed`, `failed`, `blocked`, `not_applicable`. Prefer “validated against these checks” over “correct” or “production-ready.”
