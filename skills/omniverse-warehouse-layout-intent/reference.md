# WarehouseLayoutIntent reference

## Schema

```json
{
  "intent_id": "warehouse-intent-001",
  "root_path": "/World/WarehouseLayout",
  "extents": {
    "length_m": null,
    "width_m": null,
    "source_units": "meters",
    "status": "open_question"
  },
  "flow_axes": {
    "primary": "+X receive_to_ship",
    "secondary": "+Y front_to_back",
    "up": "+Z"
  },
  "zones": [
    {
      "id": "BULK",
      "role": "storage",
      "bounds_m": null,
      "provenance": "assumption"
    }
  ],
  "aisles": [
    {
      "id": "main_aisle",
      "min_width_m": 2.0,
      "role": "travel",
      "provenance": "assumption"
    }
  ],
  "embedded_cells": [],
  "out_of_scope": ["PLC", "safety_certification", "photoreal_props"],
  "assumptions": [],
  "open_questions": [],
  "provenance": {
    "from_user": [],
    "from_document": [],
    "assumptions": []
  }
}
```

## Sanitized facility-zone example

Illustrative only—not from a customer document:

| Zone id | Role | Notes |
| --- | --- | --- |
| BULK | storage | Bulk inventory; racking deferred to storage skill |
| PACKAGING | process | May embed a palletizing cell |
| EMPTY_PALLET_STAGING | staging | Empty pallet buffer |
| TRASH | trash | Waste / reject |
| DOCK | dock | Optional; only if requested |

Aisle targets (assumptions unless specified): travel aisle ≥ 2.0 m; service lane ≥ 2.5 m.

Constraint-first sequence:

1. Overall extents and origin.
2. Non-overlapping zone regions along flow axes.
3. Aisle corridors between storage faces.
4. Embed cell footprints inside process zones without resolving robot XYZ here.
5. Hand racks to `omniverse-storage-racking` and cell detail to `omniverse-cell-layout`.
