# Building a Palletizing Cell with an AI Agent: An Honest End-to-End Case Study

**Status:** Draft  
**Primary audience:** Technical decision-makers and digital-twin teams judging whether generative USD authoring is ready for their review process  
**Target environment:** Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`)  
**Skills:** workflow in [`skill-set.yaml`](../../skill-set.yaml); this case emphasizes [`omniverse-code-packaging`](../../skills/omniverse-code-packaging/SKILL.md), [`omniverse-scene-request`](../../skills/omniverse-scene-request/SKILL.md), [`omniverse-usd-planning`](../../skills/omniverse-usd-planning/SKILL.md), [`omniverse-stage-preflight`](../../skills/omniverse-stage-preflight/SKILL.md), [`omniverse-usd-authoring`](../../skills/omniverse-usd-authoring/SKILL.md), [`omniverse-usd-validation`](../../skills/omniverse-usd-validation/SKILL.md)

Reconstructed timeline. Not copied from raw logs. Viewport images are omitted here; pair any future screenshot with the bounds table in section 7.

## The scene

This is the same palletizing request as the rest of the series, told as one run. A user asks for a basic palletization cell in Isaac Sim: robot arm, two conveyors, pallets, a shelf. An AI agent produces a plan, then Python. Chat-style status says the work succeeded, or that syntax failed, depending on the attempt. Four interpreter events never yield a validated floor. The live stage may still have changed. A first-time reader should come away with one distinction: **the agent’s success sentence is not a simulation.**

## The solution in simple terms

Treat generation as a pipeline with contracts, not as a single prompt. Normalize the request, plan steps, inspect the stage, retrieve only the APIs for this step, author one scoped Python block, package it for the interpreter, execute with mutation tracking, and validate with measurements. Accept, repair, or stop. If packaging is the cause, do not “fix the assert.” If the stage already mutated, do not retry the same code.

## Why the AI picked this pattern

Failures stacked. The model blamed assertion syntax while the executor `eval()`d the last line. Completeness bias filled pallet counts and optional extras. Completing plausible USD names and guessing centimeters showed up in other runs of the same dataset; this case’s blocking error was packaging. Retries mutated the live stage, so later evidence was ambiguous. The model is not a warehouse engineer and not an interpreter. It completes the next likely token unless each phase constrains it.

## 1. Warehouse problem

Original reconstructed request:

> Need a basic palletization cell with a robot arm and 2 conveyors and pallets and a shelf.

The operational job is a layout sketch for a palletizing cell that could later host physics, kinematics, or vendor assets. Today the need is: stable paths, a floor of known size, placeholders that are labeled placeholders, and a record of what was not requested (PLC, safety, articulation).

## 2. Observed failure

Dataset context (interpreter events, including retries, not unique requests): 65 substantive runs, 247 attempts, 110 successful events, 137 failed events, 29 runs with at least one interpreter failure, 9 runs at maximum retry. This case reconstructs a floor step with four failed Python attempts, consistent with the editorial brief’s terminal-assert / `eval` pattern (`SyntaxError` appears 21 times in the aggregate).

Reconstructed attempt shape (attempts 1–4):

```python
UsdGeom.Cube.Define(stage, "/World/PalletizingCell/Floor")
# ... scale / translate ...
assert stage.GetPrimAtPath("/World/PalletizingCell/Floor").IsValid()
```

Result: `SyntaxError` on the last line. Repair attempts renamed locals and restated the assert. Code hash of the final line did not change in kind.

## 3. Root cause

Root cause for the four failed attempts: **executor packaging**, not assertion syntax. Prefix lines may have already defined a cube. Top-level summaries in other runs of the dataset reported zero errors while failed interpreter events existed; validation marked `skipped` did not always surface in user-facing status. That is a diagnostics problem layered on the packaging bug.

Secondary issues in the surrounding workflow (not all required for this traceback, but present in the series):

- One-shot plan with scope expansion and dimensional assumptions
- API hallucination in sibling runs (`UsdGeom.Rect`, `RemovePrimPath`)
- Unit mistakes (8 m → 8000 cm)
- Duplicate retries (5 runs, 13 unnecessary retries)

Causal classification for this floor: `executor_contract`. An `eval(last_line)` failure on a valid statement is not `python_syntax`.

## 4. Why the obvious repair fails

Obvious repairs that were tried or would be tried:

| Repair | Why it fails |
| --- | --- |
| “Fix the assert syntax” | `assert` is valid; `eval` is the constraint |
| Retry the same snippet | Partial mutation; duplicate XformOps or paths |
| Add more USD docs | RAG overload; does not change the last line |
| Trust “Done” in chat | No bounds, no changed-path evidence |

## 5. Reliable pattern

Preferred workflow from this repository:

```text
request
  -> normalized scene request
  -> dependency-ordered USD plan
  -> stage preflight
  -> targeted RAG bundle
  -> one scoped Python authoring step
  -> interpreter-safe packaging
  -> idempotent execution
  -> independent validation evidence
  -> accept, repair, or stop

diagnostics observes and summarizes every phase
```

For this case, the first accepted implementation is `S1` (cell + floor) with an expression-safe `result`, units read from the stage, and no robot/conveyor/pallet/shelf prims until later steps pass preflight.

## 6. Minimal code example

Side-by-side timeline (reconstructed).

```text
Original run                         Skill-based rerun
---------------------------          ---------------------------
Sentence as spec                     SceneRequest (quantities open)
One-shot plan + extras               UsdPlan S1 only
No metersPerUnit read               Preflight reads MPU, up axis
Broad RAG dump                       RAG: Cube.Define, scale, bounds
Python ends with assert              Python ends with result
exec + eval last line                Same executor, last line is dict
SyntaxError x4                      Interpreter completes
Status: failed / skipped             Validation: path, Cube, extent
Stage: unknown mutation              changed_paths: Floor only
```

Correct `S1` implementation (Kit `stage`, last line is `result`):

```python
from pxr import Gf, Usd, UsdGeom

cell_path = "/World/PalletizingCell"
floor_path = "/World/PalletizingCell/Floor"
mpu = UsdGeom.GetStageMetersPerUnit(stage)
up = UsdGeom.GetStageUpAxis(stage)

UsdGeom.Xform.Define(stage, cell_path)
if stage.GetPrimAtPath(floor_path).IsValid():
    stage.RemovePrim(floor_path)

cube = UsdGeom.Cube.Define(stage, floor_path)
cube.GetSizeAttr().Set(1.0)
xf = UsdGeom.Xformable(cube.GetPrim())
xf.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(
    Gf.Vec3f(8.0 / mpu, 6.0 / mpu, 0.02 / mpu)
)
if up == UsdGeom.Tokens.z:
    xf.AddTranslateOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Vec3f(0.0, 0.0, (0.02 / mpu) * 0.5)
    )

prim = stage.GetPrimAtPath(floor_path)
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
size_m = [float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu]
tol = 0.01
extent_ok = (
    abs(size_m[0] - 8.0) <= tol
    and abs(size_m[1] - 6.0) <= tol
    and abs(size_m[2] - 0.02) <= tol
)
result = {
    "step_id": "S1",
    "status": "ok" if prim.IsValid() and extent_ok else "failed",
    "checks": {
        "prim_valid": bool(prim.IsValid()),
        "type_name_cube": prim.GetTypeName() == "Cube",
        "extent_m_ok": extent_ok,
    },
    "evidence": {
        "path": floor_path,
        "type_name": prim.GetTypeName(),
        "meters_per_unit": mpu,
        "up_axis": str(up),
        "size_m": size_m,
        "changed_paths": [floor_path],
    },
}
result
```

## 7. Validation

Evidence that would accept `S1` (example numbers at `metersPerUnit = 0.01`):

| Field | Value |
| --- | --- |
| Path | `/World/PalletizingCell/Floor` |
| Type name | `Cube` |
| Schema | `UsdGeomCube` |
| `metersPerUnit` | 0.01 |
| Size (m) | 8.00, 6.00, 0.02 |
| Transform | translation +½ thickness along up axis |
| Changed paths | floor only |
| Not present | robot, conveyors, pallets, shelf, PLC |

This is “validated against these checks,” not “the cell is correct.” Conveyor transfer height, pallet class, and robot reach were never in `S1`.

## 8. Warehouse implication

What still requires an automation engineer:

- Vendor robot kinematics, payload, collision, and safety
- Conveyor type, length, and true transfer height
- Pallet specification and rack loading orientation
- PhysX, sensors, and PLC
- Whether “2 conveyors” means two belts or dual-sided flow
- Production vs placeholder assets

AI agents can accelerate USD authoring of placeholders and layout datums. They do not replace engineering approval. A plausible Isaac Sim viewport is not a throughput study.

## 9. Reusable checklist

- Record the original request and outliner delta before planning.
- Classify failures (`executor_contract` vs `usd_api` vs `units_or_transform`) before editing code.
- Require a semantic patch; comments and renamed temps are not progress.
- Snapshot or compare paths so a failed interpreter event is not treated as an unchanged stage.
- Accept `S1` only with measured bounds.
- Stop after ineffective repairs with the same normalized error signature.
- Report issues with the diagnostic event fields (`phase`, `normalized_signature`, `partial_mutation`, `evidence`), not a screenshot alone.

## 10. Repository connection

The public suite starts at [README.md](../../README.md) and [`skill-set.yaml`](../../skill-set.yaml). This case used packaging as the blocking defect and request/plan/preflight/author/validate as the recovery path.

For reproducible reports, follow [`skills/omniverse-diagnostics/SKILL.md`](../../skills/omniverse-diagnostics/SKILL.md): derive error counts from events, keep `skipped` validation distinct from `passed`, and attach changed paths.

These drafts are not a claim that generative warehouse scenes are production-ready. They are a record of how staged contracts turn observed failures into a workflow you can implement with the model you already use.
