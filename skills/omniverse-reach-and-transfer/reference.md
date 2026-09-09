# ReachTransferContract reference

## Schema

```json
{
  "contract_id": "reach-001",
  "manipulator": {
    "component_id": "robot_base",
    "asset_class": "placeholder",
    "vendor_id": null,
    "base_frame": "robot_base"
  },
  "envelope": {
    "shape": "horizontal_disk",
    "radius_m": null,
    "height_span_m": [null, null],
    "center_from": "robot_base",
    "provenance": "assumption"
  },
  "stations": [
    {
      "id": "pick",
      "flow_node": "pick",
      "must_be_inside_envelope": true,
      "status": "unverified"
    },
    {
      "id": "place_L",
      "flow_node": "build_L",
      "must_be_inside_envelope": true,
      "status": "unverified"
    }
  ],
  "transfer_heights": [
    {
      "id": "infeed_to_pallet",
      "a": {"ref": "inbound_conveyor_top", "z_m": null},
      "b": {"ref": "pallet_deck", "z_m": null},
      "tolerance_m": 0.02,
      "provenance": "open_question"
    }
  ],
  "assumptions": [],
  "open_questions": [
    "Supply reach envelope or accept labeled assumption before locking stations"
  ]
}
```

## Example (labeled assumptions only)

For a dual-zone cell with a placeholder robot:

| Field | Value | Provenance |
| --- | --- | --- |
| Envelope | Horizontal disk centered on robot base | assumption |
| Radius | Record only if user/spec supplies; else leave null | open |
| Pick station | On inbound product side inside envelope | constraint |
| Place L/R | Centers of build zones inside envelope | constraint |
| Conveyor top Z | User or equipment spec | required for validation |
| Pallet deck Z | Pallet thickness + floor contact | derived or specified |

Validation later checks: station XY inside envelope; `|z_a - z_b|` within tolerance for each transfer pair.
