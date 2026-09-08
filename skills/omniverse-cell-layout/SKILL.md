---
name: omniverse-cell-layout
description: Design coherent industrial-cell layouts in Omniverse for robots, conveyors, pallets, racks, and safety clearances.
---

# Omniverse Cell Layout

Apply when industrial-cell spatial relationships must be inferred or checked. Propose layout facts; do not author USD.

## Guidance

- Treat vendor names and model numbers as asset identifiers, not permission to invent dimensions. Use supplied specifications or clearly labeled assumptions.
- Preserve access, robot reach, transfer heights, pallet footprints, rack loading faces, maintenance zones, and operator paths.
- Express placement as constraints and bounding regions before choosing coordinates.
- Check that components remain inside declared cell and floor extents.
- Distinguish two conveyors from two inbound plus two outbound conveyors.
- Keep placeholders distinct from production assets or articulated robots.
- Add safety, PLC, animation, or simulation only when requested or accepted as an extension.

Return transforms, orientations, clearance pairs, reach assumptions, and unresolved engineering constraints.
