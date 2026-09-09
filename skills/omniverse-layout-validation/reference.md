# LayoutValidationResult reference

## Schema

```json
{
  "result_id": "layout-val-001",
  "status": "failed",
  "artifacts_used": [
    "CellLayoutPlan",
    "MaterialFlowGraph",
    "ReachTransferContract"
  ],
  "checks": [
    {
      "id": "footprint_containment",
      "status": "passed",
      "evidence": {"outside_count": 0}
    },
    {
      "id": "inbound_outbound_counts",
      "status": "failed",
      "evidence": {
        "expected_inbound": 2,
        "found_inbound": 1,
        "expected_outbound": 2,
        "found_outbound": 1
      }
    },
    {
      "id": "transfer_height",
      "status": "blocked",
      "evidence": {"reason": "transfer_heights.z_m not specified"}
    },
    {
      "id": "reach_envelope",
      "status": "not_applicable",
      "evidence": {"reason": "envelope.radius_m null"}
    }
  ],
  "failed": ["inbound_outbound_counts"],
  "warnings": [],
  "evidence": {}
}
```

## Evidence table (example)

| Check | Criterion | Example evidence |
| --- | --- | --- |
| Footprint containment | All component bounds ⊆ cell footprint | `outside_count: 0` |
| Clearance pair | dist(A,B) ≥ min | `dist_m: 1.2`, `min_m: 1.0` |
| Transfer height | \|z_a − z_b\| ≤ tol | `delta_m: 0.01`, `tol_m: 0.02` |
| Zone non-overlap | Intersection area = 0 | `overlap_m2: 0` |
| Inbound/outbound | Counts and pairing match graph | `inbound: 2`, `outbound: 2` |
| Reach containment | Station XY inside envelope | `station: place_L`, `inside: true` |
| Placeholder label | `asset_class` still placeholder | `robot_base: placeholder` |
| Aisle width | Width ≥ min between faces | `width_m: 2.1`, `min_m: 2.0` |

## Relationship to USD validation

| `omniverse-usd-validation` | `omniverse-layout-validation` |
| --- | --- |
| Prim exists, schema, xform, exact bounds | Footprint, flow counts, reach, aisles |
| Step acceptance from `UsdPlan` | Contracts from layout artifacts |
| Expression-safe per step | Aggregate layout evidence after steps |

Run USD validation first for the authored step, then layout validation when layout artifacts exist.
