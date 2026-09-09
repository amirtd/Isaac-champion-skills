# StorageLayout reference

## Schema

```json
{
  "layout_id": "storage-001",
  "runs": [
    {
      "id": "rack_run_A",
      "kind": "rack",
      "zone_id": "BULK",
      "bays": null,
      "pitch_m": null,
      "levels": null,
      "loading_face": "+Y",
      "footprint_per_bay_m": null,
      "asset_class": "placeholder"
    }
  ],
  "aisles": [
    {
      "id": "aisle_1",
      "between": ["rack_run_A", "rack_run_B"],
      "min_width_m": 2.0,
      "provenance": "assumption"
    }
  ],
  "zone_containment": {
    "rule": "all_runs_inside_declared_zone",
    "zones": ["BULK"]
  },
  "assumptions": [],
  "open_questions": [
    "Bay count, pitch, and levels not specified"
  ]
}
```

## Checklist before coordinates

| Question | If unknown |
| --- | --- |
| Rack vs shelf? | Ask or record assumption |
| How many bays and levels? | `open_questions` — do not invent large grids |
| Pallet/tote footprint? | Needed for bay pitch |
| Loading face direction? | Toward aisle; record axis |
| Aisle min width? | From warehouse intent or assumption |
| Zone bounds? | Must exist before placing runs |

## Bad vs good

| Bad | Good |
| --- | --- |
| 60 cubes named `Rack_01` at random XYZ | `StorageLayout` with bay/level open questions first |
| Aisle = leftover gap | `min_width_m` constraint between faces |
| Shelf against wall with no wall orientation | Wall/face orientation in zone intent first |
