---
name: omniverse-usd-planning
description: Convert a normalized Omniverse scene request into dependency-ordered, machine-checkable USD authoring steps.
---

# Omniverse USD Planning

Plan only from a normalized request, current stage facts, and any layout artifacts. Do not generate Python.

When present, consume and do not contradict: `WarehouseLayoutIntent`, `CellLayoutPlan`, `MaterialFlowGraph`, `ReachTransferContract`, and `StorageLayout`. Coordinates in plan steps must cite those constraints; do not invent XYZ that violate footprint, flow pairing, reach envelopes, or aisle widths.

## Plan rules

- One step owns one coherent component scope and can execute independently after its dependencies.
- Give every step an operation (`create`, `update`, `reuse`, or `remove`), exact prim paths, expected schemas, transforms, dimensions, and acceptance checks.
- Ensure expected schemas agree with planned geometry; an organization Xform must not be validated as a Cube.
- Make dimensions and tolerances numeric in stage units. Distinguish non-zero bounds from exact-dimension checks.
- Include rollback scope and an idempotency key for mutating steps.
- Keep requested content separate from optional enhancements. Do not execute optional work until accepted.
- If layout artifacts are missing but the request is spatial, stop and invoke the matching layout skill before planning.

Return a `UsdPlan` with `plan_id`, `stage_contract`, `steps`, and `success_criteria`. Each step includes `step_id`, `depends_on`, `scope`, `operations`, `acceptance`, `rollback_scope`, and `rag_queries`.
