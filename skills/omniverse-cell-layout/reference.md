# CellLayoutPlan reference

## Schema

```json
{
  "plan_id": "cell-layout-001",
  "root_path": "/World/RoboticCell",
  "footprint": {
    "length_m": 8.0,
    "width_m": 6.0,
    "source": "user",
    "stage_extent": null
  },
  "origin": {
    "convention": "cell_center",
    "axes": "+X right, +Y forward, +Z up"
  },
  "up_axis": "Z",
  "units": {
    "source": "meters",
    "stage_meters_per_unit": "read_from_stage"
  },
  "components": [
    {
      "id": "robot_base",
      "role": "robot_base",
      "quantity": 1,
      "asset_class": "placeholder",
      "vendor_id": null,
      "notes": "Base region only; no invented kinematics"
    }
  ],
  "regions": [
    {
      "id": "build_zone_left",
      "role": "pallet_build_zone",
      "relation": "left_of_robot_base",
      "bounds_m": null
    }
  ],
  "clearance_pairs": [
    {
      "a": "robot_base",
      "b": "inbound_conveyor_A",
      "min_clearance_m": null,
      "status": "open_question"
    }
  ],
  "containment": {
    "rule": "all_components_inside_footprint",
    "exceptions": []
  },
  "out_of_scope": ["safety_fence", "PLC", "laser_curtains", "controller_cabinet"],
  "assumptions": [],
  "open_questions": []
}
```

Field notes:

- `asset_class` is `placeholder` or `referenced_asset`.
- `vendor_id` stores a model string when supplied; never treat it as permission to invent reach or size.
- `relation` values prefer topology (`left_of_robot_base`, `inbound_to_pick`) over XYZ until constraints are fixed.
- `stage_extent` is filled after preflight knows `metersPerUnit`.

## Dual-zone palletizing checklist

Sanitized pattern (not a vendor specification):

| Item | Resolve before XYZ |
| --- | --- |
| Footprint | e.g. 8 m × 6 m cell, source units preserved |
| Robot | Floor-mounted base region; placeholder vs referenced USD |
| Inbound | Product roller lanes count (e.g. 2 inbound) |
| Outbound | Pallet conveyor lanes count (e.g. 2 outbound) |
| Build zones | Dual L/R of robot; each holds one pallet class (e.g. EUR 1200×800) |
| Dispenser | Optional; side relative to robot if requested |
| Fence / laser / cabinet | Only if requested |
| Throughput / carton size | Validation targets for later skills—not geometry facts |

Constraint-first sequence:

1. Footprint and origin.
2. Robot base region at cell working center (or user-specified).
3. Left and right build-zone regions sized to pallet footprint + handling clearance.
4. Inbound lanes feeding pick side; outbound lanes leaving build zones.
5. Only then propose numeric centers that satisfy containment and clearance pairs.

## Example sketch (constraints then sample coords)

Assumptions labeled as such: cell 8×6 m, origin at cell center, Z-up, EUR pallet 1.2×0.8 m, dual build zones.

```text
regions:
  robot_base:     center near (0, 0), envelope TBD assumption
  build_zone_L:   left of robot, region fits 1.2 x 0.8 m pallet
  build_zone_R:   mirror of build_zone_L
  inbound_A/B:    forward of robot toward product infeed
  outbound_A/B:   aft or side exit from each build zone

sample_centers_m (only after constraints):
  robot_base:   (0.0, 0.0)
  build_zone_L: (-1.5, 0.0)
  build_zone_R: ( 1.5, 0.0)
```

These centers are layout proposals for `omniverse-usd-planning`, not engineering approval.
