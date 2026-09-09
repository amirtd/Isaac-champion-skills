---
name: omniverse-storage-racking
description: Design storage rack and shelf layouts with bay, pitch, levels, loading face, and aisle constraints before coordinates. Produces StorageLayout; does not author USD.
---

# Omniverse Storage Racking

Apply when racks, shelves, bays, selective racking, or inventory shelving are requested inside a cell or warehouse zone.

Consume `WarehouseLayoutIntent` or `CellLayoutPlan` when present. Do not author USD. Do not drop anonymous rack cubes without bay counts and aisle constraints.

## Workflow

1. Distinguish `rack` (bay/pitch/levels, loading face) from `shelf` (lighter storage, still needs face and aisle).
2. Capture bay count, pitch, levels, and pallet or tote footprint when known. Preserve source units.
3. Orient each run’s loading face toward its service aisle.
4. Enforce zone containment and minimum aisle width from warehouse intent or labeled assumptions.
5. Reject inventing 60-bay racks from thin air when the request only said “shelving.”
6. Leave structural capacity, seismic, and fire code to `open_questions` / engineering review.

## Hard rules

- No guessed XYZ rack grids without: zone, face orientation, aisle width, and bay/level counts (or an explicit open question).
- Loading face must not point into a solid wall region without a documented exception.
- Aisle width is a constraint between opposing faces—not leftover space after placing cubes.
- Placeholder rack geometry remains placeholder; not a certified storage system.

## Output

Return a `StorageLayout` artifact. See [reference.md](reference.md) for schema and example.

Required fields: `layout_id`, `runs`, `aisles`, `zone_containment`, `assumptions`, `open_questions`.
