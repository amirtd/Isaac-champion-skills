---
name: omniverse-usd-authoring
description: Generate focused Omniverse Python for correct OpenUSD prim, transform, geometry, and display authoring.
---

# Omniverse USD Authoring

Generate code for exactly one accepted plan step.

## Authoring rules

- Prefer stable native `pxr` schema APIs. Use a `usdcode` helper only when its retrieved signature directly matches the operation and adds value.
- Define organization nodes as `UsdGeom.Xform`; define visible placeholders with the simplest appropriate Gprim.
- `UsdGeom.Cube.size` is scalar. Use scale or transforms for rectangular dimensions and account for the cube's base size.
- Author translation explicitly when a surface must rest on a plane rather than be centered on it.
- Use schema display-color APIs with correctly typed array values; do not invent a scalar `displayColor` attribute.
- Use `UsdGeom.BasisCurves` or another supported schema for line-like geometry.
- Limit paths and mutations to the active step. Do not add optional control, safety, material, animation, or physics content.

The result must be deterministic, path-explicit, and safe to package for execution.
