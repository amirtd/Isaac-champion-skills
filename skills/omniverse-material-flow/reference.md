# MaterialFlowGraph reference

## Schema

```json
{
  "graph_id": "flow-001",
  "quantity_resolution": {
    "raw_phrase": "2 conveyors",
    "resolved": {
      "inbound_product": 2,
      "outbound_pallet": 2
    },
    "status": "resolved_from_context"
  },
  "nodes": [
    {"id": "in_A", "role": "inbound_product", "side": "A"},
    {"id": "in_B", "role": "inbound_product", "side": "B"},
    {"id": "pick", "role": "pick_station"},
    {"id": "build_L", "role": "build_zone", "side": "left"},
    {"id": "build_R", "role": "build_zone", "side": "right"},
    {"id": "out_L", "role": "outbound_pallet", "side": "left"},
    {"id": "out_R", "role": "outbound_pallet", "side": "right"}
  ],
  "edges": [
    {"from": "in_A", "to": "pick", "cargo": "product"},
    {"from": "in_B", "to": "pick", "cargo": "product"},
    {"from": "pick", "to": "build_L", "cargo": "product"},
    {"from": "pick", "to": "build_R", "cargo": "product"},
    {"from": "build_L", "to": "out_L", "cargo": "pallet"},
    {"from": "build_R", "to": "out_R", "cargo": "pallet"}
  ],
  "transfer_points": [
    {"id": "tp_pick", "from": "in_A", "to": "pick", "cargo": "product"},
    {"id": "tp_place_L", "from": "pick", "to": "build_L", "cargo": "product"}
  ],
  "assumptions": [],
  "open_questions": []
}
```

## Dual-zone pairing rules

- Left build zone pairs with left outbound pallet lane (or explicitly documented alternate).
- Right build zone pairs with right outbound pallet lane.
- Inbound product lanes may share one pick station or map A→left and B→right; record which.
- Pallet dispenser (if present) feeds empty pallets into build zones—not into product inbound.

## Quantity resolution examples

| Phrase | Bad resolution | Good resolution |
| --- | --- | --- |
| “2 conveyors” | two anonymous cubes | ask or choose: 2 product belts **or** 1 in + 1 out **or** 2 in + 2 out from fuller context |
| “2 inbound and 2 outbound” | collapse to 2 | four nodes with roles |
| “pallets” | one pallet | quantity + empty vs loaded + staging vs build |
