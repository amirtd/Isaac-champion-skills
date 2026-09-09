---
name: omniverse-cell-layout
description: Design coherent industrial-cell layouts in Omniverse for robots, conveyors, pallets, build zones, and clearances. Produces CellLayoutPlan constraints before coordinates; does not author USD.
---

# Omniverse Cell Layout

Apply when the request is a robot cell, palletizing cell, pick-and-place cell, or similar industrial workcell with spatial relationships. Propose layout facts; do not author USD.

Consume a normalized `SceneRequest` when available. Hand off to `omniverse-material-flow` and `omniverse-reach-and-transfer` when conveyors, dual zones, or pick/place heights matter. Hand off to `omniverse-storage-racking` when racks or shelves are in scope.

## Workflow

1. Extract footprint, origin convention, and up axis. Preserve source units next to stage units.
2. List components with quantities. Resolve conveyor ambiguity: two belts is not the same as two inbound plus two outbound.
3. Express placement as constraints and bounding regions before choosing coordinates.
4. Mark every component `placeholder` or `referenced_asset`. Vendor names and model numbers are asset identifiers only—not invented dimensions, reach, payload, or kinematics.
5. Keep safety fencing, PLC, controllers, laser curtains, materials, and animation out of scope unless requested or explicitly accepted.
6. Record clearance pairs and floor-containment checks. Leave unresolved engineering items in `open_questions`.

## Hard rules

- Dual build zones are left/right (or mirrored) regions relative to the robot base—not free XYZ guesses.
- Controller cabinets and fences are optional enhancements, not implied by “robot + conveyors.”
- Reject treating a placeholder arm as a rated manipulator.
- Do not invent coordinates that violate footprint containment or stated clearances.
- Constraints before coordinates. If a numeric placement is proposed, cite the constraint it satisfies.

## Output

Return a `CellLayoutPlan` artifact. See [reference.md](reference.md) for the schema and a dual-zone palletizing example.

Required top-level fields: `plan_id`, `footprint`, `origin`, `up_axis`, `units`, `components`, `regions`, `clearance_pairs`, `containment`, `out_of_scope`, `assumptions`, `open_questions`.
