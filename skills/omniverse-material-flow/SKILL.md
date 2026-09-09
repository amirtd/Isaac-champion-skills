---
name: omniverse-material-flow
description: Build a material-flow graph for warehouse and robot-cell layouts—inbound/outbound pairing, buffers, build zones, and transfer points—before coordinates. Produces MaterialFlowGraph; does not author USD.
---

# Omniverse Material Flow

Apply when conveyors, build zones, inbound/outbound lanes, buffers, staging, or dual-zone product/pallet paths exist.

Consume `SceneRequest` plus `CellLayoutPlan` and/or `WarehouseLayoutIntent` when present. Do not author USD. Reach envelopes and transfer heights belong in `omniverse-reach-and-transfer`.

## Workflow

1. Enumerate flow nodes: inbound_product, buffer, pick_station, build_zone, outbound_pallet, empty_pallet_staging, trash, and user-defined equivalents.
2. Resolve quantities explicitly. “2 conveyors” must become either two undifferentiated belts or two inbound plus two outbound—never leave it ambiguous.
3. Draw edges for product path vs pallet path. Dual-zone cells pair left/right build zones with corresponding outbound lanes.
4. Mark transfer points (node pairs where product or pallet changes equipment). Heights stay in `omniverse-reach-and-transfer`.
5. Reject adding PLC, sensors, or animation nodes unless requested.
6. Record assumptions and open questions that block coordinate assignment.

## Hard rules

- Product conveyors and pallet conveyors are different node roles.
- Dual build zones require explicit left/right (or A/B) pairing to outbound exits.
- Empty-pallet staging is not the same as a build zone.
- Do not invent buffers “for realism” when the request did not include them.
- Flow graph first; XYZ only as optional annotations that cite a satisfied constraint.

## Output

Return a `MaterialFlowGraph` artifact. See [reference.md](reference.md) for schema and a dual-zone example.

Required fields: `graph_id`, `nodes`, `edges`, `transfer_points`, `quantity_resolution`, `assumptions`, `open_questions`.
