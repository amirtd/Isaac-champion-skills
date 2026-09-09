# From a Palletizing Request to an Executable USD Plan

**Status:** Draft  
**Primary audience:** Warehouse automation engineers and digital-twin teams converting layout language into Isaac Sim scenes  
**Target environment:** Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`)  
**Skills:** [`omniverse-scene-request`](../../skills/omniverse-scene-request/SKILL.md), [`omniverse-usd-planning`](../../skills/omniverse-usd-planning/SKILL.md)

Reconstructed examples are labeled. They are not copied from raw logs.

## The scene

Someone types: “Need a basic palletization cell with a robot arm and 2 conveyors and pallets and a shelf.”

An AI agent treats that sentence as a complete physics-sim spec. It one-shots a room: guessed coordinates, a cube for an arm, two boxes labeled conveyors, a stack of pallets, a shelf, sometimes extra PLC geometry, safety fencing, and materials nobody asked for. The viewport looks busy. Quantities are unresolved (how many pallets?). “Two conveyors” might mean two belts or two inbound plus two outbound. The placeholder arm is treated as if it had vendor reach. Isaac Sim will run something. It is not an engineering cell.

## The solution in simple terms

Do not generate the whole scene from the sentence. First write down what was actually requested, what is already on the stage, and what you are assuming. Then produce a dependency-ordered plan: cell and floor, then robot placeholder, conveyors, pallets, shelf, then validation. Each step has paths, schemas, and measurable acceptance. Execute only the first accepted step. Leave PLC, safety, animation, and real robot articulation out until someone accepts them.

## Why the AI picked this pattern

Language models are trained to be helpful and complete. A warehouse sentence is full of unspoken defaults; the model fills them instead of leaving them explicit. Chat-style generation is one-shot: produce the whole answer now. Constraints (transfer height, pallet class, wall orientation) are harder than coordinates, so the model emits coordinates. Scope expansion (materials, lighting, physics, safety) looks like quality in a demo and like contamination in a digital-twin handoff.

## 1. Warehouse problem

The operational request is a palletizing cell: robot, conveyors, pallets, shelf. Before CAD or vendor files arrive, the team wants a layout sketch in Isaac Sim that preserves:

- Component list and quantities
- Relationships (pallet on conveyor, shelf against a wall, robot covering pick/place)
- Units
- What is placeholder vs a referenced asset

They also need to know what the current outliner already contains so the agent does not rebuild a floor that exists or ignore a removed path from the last prompt.

## 2. Observed failure

Unresolved assumptions inside the one sentence:

| Phrase | Unresolved |
| --- | --- |
| “palletization cell” | Extent, origin, units, up axis |
| “a robot arm” | Vendor, reach, placeholder vs referenced USD, payload |
| “2 conveyors” | Two belts vs two in plus two out; length; transfer height |
| “pallets” | Count, 1200×1000 vs 1200×800, loaded or empty |
| “a shelf” | Rack vs shelf, bays, loading face, “against a wall” without a wall |

One-shot generated plans in the dataset mixed required scope with optional PLC, safety, material, and animation. Dimensional assumptions (8 m × 6 m, robot reach) appeared without being marked as assumptions. Later Python then guessed coordinates instead of applying those constraints.

## 3. Root cause

There is no typed artifact between “user sentence” and “Python.” Without a `SceneRequest`, quantity, unit, and outliner reconciliation are improvised inside the generator. Without a `UsdPlan`, the model authors robot, conveyors, and shelf in one block, so a floor failure still mutates later prims.

Schema/acceptance mismatch is a planning bug: an organization `Xform` planned as a `Cube`, or a conveyor placeholder validated only as “prim exists.” Unbounded plans have no rollback scope and no RAG query per step, so retrieval dumps the whole warehouse corpus into a floor authoring step.

## 4. Why the obvious repair fails

The obvious repair is a longer prompt: “also use meters, don’t add extras, think step by step.” The model still one-shots. Helpfulness still fills pallet count. A second repair is to generate a numbered list in prose (`1. Create floor 2. Create robot…`) without paths, schemas, or acceptance. That list is not machine-checkable; the next model call ignores it.

Retrying the full scene after a floor error re-authors everything, including components that already succeeded.

## 5. Reliable pattern

[`omniverse-scene-request`](../../skills/omniverse-scene-request/SKILL.md) produces `SceneRequest`: explicit vs default, outliner reconciliation (`create` / `update` / `reuse` / `remove`), units, relationships, assumptions, open questions, out of scope. Requested robots and conveyors do not imply PLCs or safety systems.

[`omniverse-usd-planning`](../../skills/omniverse-usd-planning/SKILL.md) consumes that artifact and returns `UsdPlan`: dependency-ordered steps, each with operation, prim paths, expected schemas, transforms, dimensions, acceptance, rollback scope, and RAG queries. Optional enhancements stay unexecuted.

Dependency order for this cell:

1. Cell root and floor
2. Robot placeholder or referenced asset
3. Conveyors
4. Pallets
5. Rack or shelf
6. Validation of the accepted scope

## 6. Minimal code example

Compact machine-readable plan (reconstructed). Execute only step `S1`.

```python
plan = {
    "plan_id": "palletizing-cell-001",
    "stage_contract": {
        "root": "/World/PalletizingCell",
        "source_units": "meters",
        "assume_meters_per_unit": "read_from_stage",
        "up_axis": "read_from_stage",
    },
    "steps": [
        {
            "step_id": "S1",
            "depends_on": [],
            "scope": ["/World/PalletizingCell", "/World/PalletizingCell/Floor"],
            "operations": [
                {"op": "create", "path": "/World/PalletizingCell", "schema": "UsdGeomXform"},
                {
                    "op": "create",
                    "path": "/World/PalletizingCell/Floor",
                    "schema": "UsdGeomCube",
                    "extent_m": [8.0, 6.0, 0.02],
                },
            ],
            "acceptance": {
                "type_name": "Cube",
                "extent_m": [8.0, 6.0, 0.02],
                "tolerance_m": 0.01,
            },
            "rollback_scope": ["/World/PalletizingCell/Floor"],
            "rag_queries": ["UsdGeom.Xform.Define", "UsdGeom.Cube.Define", "AddScaleOp PrecisionFloat"],
        },
        {
            "step_id": "S2",
            "depends_on": ["S1"],
            "scope": ["/World/PalletizingCell/RobotPlaceholder"],
            "operations": [
                {
                    "op": "create",
                    "path": "/World/PalletizingCell/RobotPlaceholder",
                    "schema": "UsdGeomXform",
                    "note": "placeholder geometry only; not vendor kinematics",
                }
            ],
            "acceptance": {"prim_valid": True, "type_name": "Xform"},
            "rollback_scope": ["/World/PalletizingCell/RobotPlaceholder"],
            "rag_queries": ["UsdGeom.Xform.Define"],
        },
    ],
    "success_criteria": "S1 bounds validated before S2 executes",
    "out_of_scope": ["PLC", "safety fencing", "materials", "articulation", "PhysX"],
}

# First step only — grounded authoring, expression-safe result.
from pxr import Gf, Usd, UsdGeom

cell = "/World/PalletizingCell"
floor_path = "/World/PalletizingCell/Floor"
UsdGeom.Xform.Define(stage, cell)
if stage.GetPrimAtPath(floor_path).IsValid():
    stage.RemovePrim(floor_path)
cube = UsdGeom.Cube.Define(stage, floor_path)
cube.GetSizeAttr().Set(1.0)
mpu = UsdGeom.GetStageMetersPerUnit(stage)
xf = UsdGeom.Xformable(cube.GetPrim())
xf.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(
    Gf.Vec3f(8.0 / mpu, 6.0 / mpu, 0.02 / mpu)
)
prim = stage.GetPrimAtPath(floor_path)
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
result = {
    "executed_step": "S1",
    "skipped_steps": ["S2"],
    "path": floor_path,
    "type_name": prim.GetTypeName(),
    "size_m": [float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu],
}
result
```

The plan prevents the model from building the robot while the floor is still unproven.

## 7. Validation

For `S1` only:

| Check | Criterion |
| --- | --- |
| Paths | `/World/PalletizingCell`, `/World/PalletizingCell/Floor` |
| Schemas | Xform parent, Cube child |
| Extent | 8.00 × 6.00 × 0.02 m ± 1 cm |
| Out of scope | no PLC or safety prims under the cell |
| Later steps | `RobotPlaceholder` absent until `S2` is accepted |

If `S2` prims exist after a run that claimed to execute only `S1`, the generator ignored the plan.

## 8. Warehouse implication

A one-shot cell trains everyone to argue with a picture. A plan makes the argument specific: we accepted an 8 m floor; we did not accept a vendor robot reach; “two conveyors” is still an open question. That is the difference between a sales viewport and a layout that can enter a review process.

Placeholder robots stay labeled. Constraints (reach envelope as a box, transfer height as a number) come before coordinates so guessed XYZ does not become a fake mechanical design.

## 9. Reusable checklist

- Extract requested components and quantities; mark unknowns.
- Reconcile the outliner and recent added/removed paths.
- Separate required scope from PLC, safety, materials, animation.
- Normalize units and placement relationships before XYZ.
- Assign stable paths under a cell root.
- Give every step schemas, dimensions, acceptance, rollback, and RAG queries.
- Execute one step; do not author later components prematurely.

## 10. Repository connection

Compare your current prompts with the artifacts these skills define:

- [`skills/omniverse-scene-request/SKILL.md`](../../skills/omniverse-scene-request/SKILL.md) — `SceneRequest`
- [`skills/omniverse-usd-planning/SKILL.md`](../../skills/omniverse-usd-planning/SKILL.md) — `UsdPlan`

The last Tier 1 post walks the same sentence from the original failed agent run through this workflow, including the four Python attempts that never got a floor.
