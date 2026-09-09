# Meters, Centimeters, and Quaternion Types

**Status:** Draft  
**Primary audience:** Warehouse automation engineers and Isaac Sim developers authoring cell geometry with agents  
**Target environment:** Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`). USD bindings load with Kit.  
**Skills:** [`omniverse-stage-preflight`](../../skills/omniverse-stage-preflight/SKILL.md), [`omniverse-usd-validation`](../../skills/omniverse-usd-validation/SKILL.md)

Reconstructed examples are labeled. They are not copied from raw logs.

## The scene

The request is an 8 m × 6 m palletizing cell in Isaac Sim: floor, placeholder robot, conveyors, pallets, shelf. The agent authors numbers it saw in the prompt—8 and 6—then multiplies as if the stage were already in centimeters and the source were millimeters, or it writes 8000 and 6000 because “USD is in cm.”

The viewport shows a cell the size of a parking lot. A placeholder arm sits in the corner with an implied reach that no industrial robot has. Conveyor height relative to pallet deck is fiction. A second class of crash appears when orientation is authored: `GfQuatd` or `Gf.Vec3d` where the bound attribute expects float types. The sim looks dramatic. It is not the requested room.

## The solution in simple terms

Read the stage’s unit metadata before writing coordinates. Keep the user’s unit next to the normalized stage value. Convert once, then prove world-space size with a tolerance. Use the Gf precision the schema actually binds—float versus double is not a style choice. If a number is a guess (robot reach, vendor pallet height), label it as an assumption, not a specification.

## Why the AI picked this pattern

Models treat numbers as labels. “8 by 6” is completed with the unit that appears most often in training text and USD snippets, often centimeters, sometimes millimeters. Quaternion and vector types look interchangeable in Python until Boost.Python rejects the signature. The model does not read `metersPerUnit` unless the workflow forces that read. Centered cubes vs floor-contact placement is another completion: `Cube` defaults to centered at the origin, so a 2 cm thick floor can sit half above and half below z = 0 unless translation is authored.

## 1. Warehouse problem

An 8 m × 6 m cell is a layout constraint: aisle space, robot envelope, inbound/outbound conveyors, rack face, pallet footprint. If those meters become 80 m × 60 m, every clearance is wrong. Robot reach assumptions become theater. A shelf “against a wall” has no wall orientation and no units, so it cannot be a loading face.

Warehouse engineers need the user’s meter (or inch) and the stage number shown together. They also need to know whether a dimension is full extent, half extent, cube `size`, or scale.

## 2. Observed failure

Reconstructed mismatch from the editorial brief: intended 8 m × 6 m boundary, generated 8,000 cm × 6,000 cm. If `metersPerUnit` is 0.01, 8000 cm is 80 m.

Reconstructed type error:

```python
from pxr import Gf

# Attribute or XformOp authored as double where the binding expects float.
orient.Set(Gf.Quatd(1.0, 0.0, 0.0, 0.0))
scale.Set(Gf.Vec3d(8000.0, 6000.0, 2.0))
```

The dataset includes 6 Boost.Python argument-signature errors among interpreter events. Unit bugs also show up as “successful” runs whose bounds are non-zero but 10× or 100× too large. Validation that only checks non-zero bounds will pass those cells.

Cube-size confusion appears in the same family: treating cube `size` as a three-dimensional vector instead of one scalar, then stacking an extra scale.

## 3. Root cause

USD numeric values are not meters. They are stage units. `UsdGeom.GetStageMetersPerUnit(stage)` is the conversion to meters. Isaac Sim 5.0 in-tree code uses that call before comparing bounds.

Physical size:

```text
size_meters = size_stage_units * metersPerUnit
```

If the user said 8 m and the stage is centimeters (`metersPerUnit = 0.01`), the authored extent should be 800, not 8 and not 8000.

`UsdGeom.Cube.size` is one scalar (the cube’s edge in local space, default 2.0 in many USD versions). Rectangular floors use `size = 1.0` (or 2.0 with half-scale) plus `AddScaleOp`. Mixing “size as Vec3” with a second scale doubles the error.

Gf precision: `Gf.Vec3f` / `Gf.Quatf` vs `Gf.Vec3d` / `Gf.Quatd`. XformOps created with `PrecisionFloat` expect float types. Passing `Gf.Vec3d` can raise a signature error rather than convert silently. Display-color arrays have the same class of mistake (scalar vs array, float vs double).

Up axis: Isaac Sim is commonly Z-up; other Omniverse stages may be Y-up. Read `UsdGeom.GetStageUpAxis(stage)` before choosing which scale component is thickness.

## 4. Why the obvious repair fails

The obvious repair is “Isaac Sim is always centimeters, so multiply by 100.” That is sometimes right and often wrong. A stage can be meters (`metersPerUnit = 1.0`). Multiplying 8 m by 100 on a meter stage yields an 800 m cell.

The second obvious repair is “check that the prim has bounds.” Non-zero bounds pass a stadium-sized floor. Exact dimension plus tolerance is the check that fails.

The third is to switch `Quatd` to `Quatf` in one place and leave `Vec3d` on a float scale op. Signature errors then move to the next line.

## 5. Reliable pattern

[`omniverse-stage-preflight`](../../skills/omniverse-stage-preflight/SKILL.md) runs before mutation: stage validity, edit target, up axis, `metersPerUnit`, conversion factors, parent paths.

[`omniverse-usd-validation`](../../skills/omniverse-usd-validation/SKILL.md) measures after execution: exact dimensions with declared tolerances; non-zero bounds are insufficient when dimensions were specified.

Preserve source units in the normalized request (`8 m` plus `800` stage units at `0.01`). Convert in one place. Sanity-check warehouse objects before accepting the step (see checklist).

## 6. Minimal code example

Author the same 8 m × 6 m floor on two unit metadatas and compare world-space meters. This is a demonstration of conversion, not a claim that both unit systems are equally common in Isaac Sim.

```python
from pxr import Gf, Usd, UsdGeom

def author_floor(stage, floor_path, length_m, width_m, thickness_m):
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    length_u = length_m / mpu
    width_u = width_m / mpu
    thick_u = thickness_m / mpu
    if stage.GetPrimAtPath(floor_path).IsValid():
        stage.RemovePrim(floor_path)
    cube = UsdGeom.Cube.Define(stage, floor_path)
    cube.GetSizeAttr().Set(1.0)
    xf = UsdGeom.Xformable(cube.GetPrim())
    xf.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Vec3f(float(length_u), float(width_u), float(thick_u))
    )
    # Z-up: lift by half thickness so the slab sits on z = 0.
    xf.AddTranslateOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Vec3f(0.0, 0.0, float(thick_u) * 0.5)
    )
    return mpu

def world_size_m(stage, prim_path):
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    prim = stage.GetPrimAtPath(prim_path)
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
    return (float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu)

path = "/World/PalletizingCell/Floor"
UsdGeom.Xform.Define(stage, "/World/PalletizingCell")

# Demonstration only: two in-memory unit systems, same physical floor.
# On a live Isaac Sim stage, read metersPerUnit; do not SetStageMetersPerUnit
# unless that change is an accepted plan step.

cm_stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(cm_stage, 0.01)
UsdGeom.SetStageUpAxis(cm_stage, UsdGeom.Tokens.z)
author_floor(cm_stage, path, 8.0, 6.0, 0.02)
cm_size = world_size_m(cm_stage, path)

m_stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(m_stage, 1.0)
UsdGeom.SetStageUpAxis(m_stage, UsdGeom.Tokens.z)
author_floor(m_stage, path, 8.0, 6.0, 0.02)
m_size = world_size_m(m_stage, path)

tol_m = 0.01
same = all(abs(a - b) <= tol_m for a, b in zip(cm_size, m_size))
result = {
    "cm_stage_size_m": list(cm_size),
    "m_stage_size_m": list(m_size),
    "physical_match": same,
    "expected_m": [8.0, 6.0, 0.02],
}
result
```

On a live Isaac Sim `stage`, skip `CreateInMemory` and `SetStageMetersPerUnit`. Read metadata, convert, author, measure.

## 7. Validation

| Object | Sanity range (order of magnitude) | Fail if |
| --- | --- | --- |
| Palletizing cell | ~5–20 m typical training cell | 80 m from 8 m × 1000 |
| Pallet footprint | ~1.0–1.2 m × 0.8–1.2 m class | 10 m “pallet” |
| Conveyor width | ~0.3–1.2 m | 8 m belt as “width” |
| Floor thickness | centimeters, not meters | 2 m slab for a 2 cm deck |
| Placeholder robot | labeled placeholder | used as vendor reach |

Tolerance example: expected 8.00 m × 6.00 m, tolerance 1 cm. Non-zero-only checks are not this table.

## 8. Warehouse implication

A 10× cell invalidates robot placement, conveyor transfer height, rack loading orientation, and any throughput story that used travel distance. A quaternion type crash can leave a half-rotated conveyor after a partial mutation. Customer digital-twin reviews then argue about a room that was never specified.

Placeholder geometry remains placeholder. Correct meters do not turn a cube arm into a rated manipulator.

## 9. Reusable checklist

- Read `UsdGeom.GetStageMetersPerUnit` and `UsdGeom.GetStageUpAxis` before authoring.
- Store source unit and stage value side by side (`8 m` → `800` at `0.01`).
- Treat cube `size` as a scalar; use scale for rectangular extent.
- Author translation so the floor contacts z = 0 (or y = 0) instead of remaining centered.
- Match `Gf.Vec3f`/`Quatf` to float XformOps; do not mix `Quatd` into a float op.
- Validate exact extents with tolerance, not only non-zero bounds.
- Sanity-check pallet, conveyor, rack, cell, and robot numbers against warehouse ranges.

## 10. Repository connection

The unit-normalization checks above are the preflight and validation skills:

- [`skills/omniverse-stage-preflight/SKILL.md`](../../skills/omniverse-stage-preflight/SKILL.md) — inspect units, axes, and path state before mutation.
- [`skills/omniverse-usd-validation/SKILL.md`](../../skills/omniverse-usd-validation/SKILL.md) — measured bounds, schemas, and clearances.

The next post steps back from a single floor and shows how the original one-sentence palletizing request should become a plan before any coordinate is generated.
