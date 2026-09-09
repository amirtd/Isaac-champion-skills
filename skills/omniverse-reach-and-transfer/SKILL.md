---
name: omniverse-reach-and-transfer
description: Define robot or gantry reach envelopes and transfer-height pairs as labeled assumptions or supplied specs—not fake IK. Produces ReachTransferContract; does not author USD.
---

# Omniverse Reach and Transfer

Apply when a robot, gantry, or similar manipulator must pick or place relative to conveyors, pallets, tables, or build zones.

Consume `CellLayoutPlan` and `MaterialFlowGraph` when present. Do not author USD and do not invent vendor kinematics, payload, or certified reach from a model number alone.

## Workflow

1. Identify the manipulator base frame and every pick/place station from the flow graph.
2. Represent reach as a labeled envelope (sphere, cylinder, or box) in cell coordinates. Mark numeric radius/extent as `assumption` unless a supplied specification exists.
3. Define transfer-height pairs: e.g. inbound conveyor top ↔ pallet deck; record source units.
4. Require every pick/place target to lie inside the envelope before accepting coordinates.
5. Keep placeholder manipulators labeled; a cube arm is not an articulated digital twin.
6. Hand measurable acceptance checks to `omniverse-layout-validation`.

## Hard rules

- Vendor model strings are asset IDs, not permission to invent reach or payload.
- Do not run or fabricate IK unless the user supplies a real robot asset and asks for it.
- Transfer height is a pair of Z (or up-axis) values with tolerance—not a single magic constant copied from unrelated scenes.
- If reach cannot be justified, leave stations as `open_questions` rather than guessing XYZ “inside reach.”

## Output

Return a `ReachTransferContract` artifact. See [reference.md](reference.md) for schema and example.

Required fields: `contract_id`, `manipulator`, `envelope`, `stations`, `transfer_heights`, `assumptions`, `open_questions`.
