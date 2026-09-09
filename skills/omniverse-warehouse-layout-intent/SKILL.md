---
name: omniverse-warehouse-layout-intent
description: Normalize facility-scale warehouse layout intent into zones, flow axes, and aisle targets before cell or USD planning. Produces WarehouseLayoutIntent; does not author USD.
---

# Omniverse Warehouse Layout Intent

Apply when the request or documents imply a multi-area warehouse, docks, aisles, storage vs process zones, or a facility floor plan—not only a single robot cell.

Consume `SceneRequest`. Do not author USD. Cell-scale detail belongs in `omniverse-cell-layout`. Flow between zones belongs in `omniverse-material-flow`. Racks belong in `omniverse-storage-racking`.

## Workflow

1. Separate facility-scale intent from single-cell requests. Prefer root `/World/WarehouseLayout` for facilities and `/World/RoboticCell` for cells.
2. List zones with roles: storage, process, staging, dock, trash, empty_pallet, packaging, bulk, or user-named equivalents.
3. Record overall extents and flow axes (e.g. +X receive→ship, +Y front→back). Preserve source units.
4. Capture aisle and service-lane targets as constraints or labeled assumptions—not freehand gaps between racks.
5. Mark each fact `from_user`, `from_document`, or `assumption`. Surface only ambiguities that change geometry or flow.
6. Reject scope expansion into PLC, safety systems, animation, or photoreal clutter unless requested.

## Hard rules

- Named zones are regions with roles, not an excuse to drop rack cubes at guessed XYZ.
- Do not invent site dimensions from vendor marketing or unrelated examples.
- Customer document content must be summarized into structured fields; do not paste proprietary text into the artifact.
- If both a facility and an embedded cell exist, keep zone intent here and defer cell internals to `omniverse-cell-layout`.

## Output

Return a `WarehouseLayoutIntent` artifact. See [reference.md](reference.md) for schema and a sanitized multi-zone example.

Required fields: `intent_id`, `root_path`, `extents`, `flow_axes`, `zones`, `aisles`, `embedded_cells`, `out_of_scope`, `assumptions`, `open_questions`, `provenance`.
