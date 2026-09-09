# Why USD Agents Invent APIs—and How to Stop Them

**Status:** Draft  
**Primary audience:** Isaac Sim and Omniverse developers generating USD with coding agents  
**Target environment:** Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`). OpenUSD Python bindings load with Kit, not a standalone `python.exe`. Examples follow OpenUSD 24.x schema documentation and in-tree Isaac Sim 5.0 usage.  
**Skills:** [`omniverse-rag-routing`](../../skills/omniverse-rag-routing/SKILL.md), [`omniverse-usd-authoring`](../../skills/omniverse-usd-authoring/SKILL.md)

Reconstructed examples below are labeled as such. They are derived from aggregate failure notes, not copied from raw agent logs.

## The scene

A warehouse team is standing up a palletizing cell in Isaac Sim: a floor, a placeholder robot, two conveyors, pallets, and a shelf. Before anyone talks reach or transfer height, they ask an AI agent to put a floor in the cell and then replace that floor with a slightly thicker one.

The agent replies with Python that looks like Omniverse. Names are capitalized the way USD names are capitalized. The snippet would pass a quick visual review in a chat window. The moment it runs, Isaac Sim raises `AttributeError`. There is no floor. There is no replacement. The physics sim never starts because the generated scene never exists.

## The solution in simple terms

Do not let the model invent USD calls. Before it writes Python, retrieve a verified signature for the exact operation. If that signature is not in official `pxr` APIs, schema docs, or a tested helper, do not emit the call. After generation, audit every callable against those sources. A missing API is a stop, not a prompt to guess a similar name.

## Why the AI picked this pattern

`UsdGeom.Cube` is real, so `UsdGeom.Rect` and `UsdGeom.Box` feel real. English says “rectangle” and “remove this path”; the model completes those words into method names. It is not looking up the bound Python module. When the prompt also contains lighting, materials, physics helpers, and unrelated examples, the model has even more plausible names to complete. The failure is pattern completion, not a warehouse misunderstanding.

## 1. Warehouse problem

The operational task is small and common: author a cell floor that later components sit on, then replace it when thickness or extent changes. Conveyors, pallet footprints, and a placeholder robot all inherit that floor’s frame. If the floor call is invented, nothing downstream can be measured. If a delete call is invented, a previous floor can remain while the agent reports that it “replaced” it.

Warehouse engineers do not need to memorize OpenUSD. They do need a floor whose path, schema, and bounds can be checked before anyone treats the viewport as a layout.

## 2. Observed failure

Reconstructed interpreter excerpt (not a raw log):

```python
from pxr import UsdGeom

floor = UsdGeom.Rect.Define(stage, "/World/PalletizingCell/Floor")
floor.GetSizeAttr().Set((800.0, 2.0, 600.0))
stage.RemovePrimPath("/World/PalletizingCell/Floor")
```

Typical result:

```text
AttributeError: type object 'Rect' has no attribute 'Define'
```

If the create call is patched to a cube and the replace path still uses `RemovePrimPath`, the next event is another `AttributeError` on `Usd.Stage`.

Across 65 substantive runs in the local dataset, there were 247 interpreter attempts: 110 successful events and 137 failed events. Those numbers count retries, not 137 independent user requests. `AttributeError` was the largest class: 53 events. Recurring invented names included `UsdGeom.Rect`, `UsdGeom.Box`, `UsdGeom.StageComputeMetrics`, `Stage.RemovePrimPath`, `Stage.GetStageFilePath`, `Stage.IsEditable`, `Sdf.Path.split`, `Sdf.Path.GetString`, `Sdf.Path.GetAllNames`, `BBox3d.ComposeAlignedRange`, `Xformable.GetXformOpByIndex`, and schema-specific calls on the wrong type such as `Cube.GetRadiusAttr`.

## 3. Root cause

OpenUSD is a large schema surface with Python bindings over C++. Nearby names are often real (`Cube`, `Sphere`, `Mesh`, `BasisCurves`). Nearby names that are not real still look like USD (`Rect`, `Box`, `RemovePrimPath`). Version differences add more near-misses. Attributes are schema-specific: a cube has `size` as a scalar; a sphere has `radius`; copying `GetRadiusAttr` onto a cube is a type error dressed as a method call.

The model does not execute `hasattr(UsdGeom, "Rect")` before printing code. Unless retrieval injects an exact signature, generation is unconstrained name completion.

Native discovery looks like this:

```python
from pxr import UsdGeom

print(hasattr(UsdGeom, "Rect"))   # False
print(hasattr(UsdGeom, "Box"))    # False
print(hasattr(UsdGeom, "Cube"))   # True
print(hasattr(stage, "RemovePrim"))      # True
print(hasattr(stage, "RemovePrimPath"))  # False
```

`UsdGeom.Cube.Define`, `stage.GetPrimAtPath`, and `stage.RemovePrim` are the calls this article uses for create and replace. They appear in Isaac Sim 5.0 in-tree code. They are not guessed from English.

## 4. Why the obvious repair fails

The obvious repair is to paste more USD documentation into the prompt. The same dataset shows why that fails. Large prompts repeatedly included material tracing, lighting, load rules, physics helpers, cache utilities, and unrelated navigation helpers while the active step only needed an Xform and a floor cube. System context ranged from roughly 78,000 characters to more than 427,000 characters.

More text increases the supply of plausible names. It does not rank `UsdGeom.Cube.Define` above `UsdGeom.Rect`. Lexical overlap (“floor”, “remove”, “box”, “physics”) pulls in the wrong catalog. The model then hallucinates helpers that appeared nearby rather than the schema that exists.

## 5. Reliable pattern

Use a retrieval hierarchy, then generate only from what it returned:

1. Exact official or local signature for the callable.
2. Exact schema documentation for the prim type.
3. A known, tested wrapper whose retrieved signature matches the operation.
4. Generate no call when evidence is absent.

[`omniverse-rag-routing`](../../skills/omniverse-rag-routing/SKILL.md) owns the bundle: query from the operation, schema, and failure signature; prefer native `pxr`; exclude unrelated materials, lighting, physics, and examples; cap context. [`omniverse-usd-authoring`](../../skills/omniverse-usd-authoring/SKILL.md) owns emission: one plan step, native schemas, no invented attributes, no optional physics or safety content.

Pre-generation: the RAG bundle must contain the create and remove signatures if those operations are in the step. Post-generation: every `UsdGeom.*`, `stage.*`, and `Sdf.*` call is either in the bundle or rejected.

## 6. Minimal code example

Hallucinated replace (do not run):

```python
stage.RemovePrimPath("/World/PalletizingCell/Floor")
UsdGeom.Box.Define(stage, "/World/PalletizingCell/Floor")
```

Grounded create, measure, replace. Assumes an existing writable `stage` (Isaac Sim supplies it). Cube `size` is a scalar; rectangular extent is scale. Isaac Sim stages are commonly Z-up; read the axis rather than assuming it.

```python
from pxr import Gf, Usd, UsdGeom

cell_path = "/World/PalletizingCell"
floor_path = "/World/PalletizingCell/Floor"

UsdGeom.Xform.Define(stage, cell_path)

existing = stage.GetPrimAtPath(floor_path)
if existing.IsValid():
    stage.RemovePrim(floor_path)

floor = UsdGeom.Cube.Define(stage, floor_path)
floor.GetSizeAttr().Set(1.0)
xform = UsdGeom.Xformable(floor.GetPrim())
# Stage units here are centimeters: 8 m x 6 m floor, 2 cm thick.
xform.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(Gf.Vec3f(800.0, 600.0, 2.0))
xform.AddTranslateOp(UsdGeom.XformOp.PrecisionFloat).Set(Gf.Vec3f(0.0, 0.0, 1.0))

prim = stage.GetPrimAtPath(floor_path)
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
box = cache.ComputeWorldBound(prim).ComputeAlignedBox()
size = box.GetSize()
mpu = UsdGeom.GetStageMetersPerUnit(stage)

result = {
    "path": floor_path,
    "valid": bool(prim.IsValid()),
    "type_name": prim.GetTypeName(),
    "schema": "UsdGeomCube",
    "size_stage": [float(size[0]), float(size[1]), float(size[2])],
    "size_m": [float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu],
    "meters_per_unit": mpu,
}
result
```

The last line is an expression so executors that `eval()` the final line still receive the dictionary. That contract is the next post; it is included here so this snippet is not itself an interpreter trap.

## 7. Validation

Viewport appearance is not enough. Record path, schema, and bounds.

| Check | Expected | Measured (example, cm stage, `metersPerUnit` 0.01) |
| --- | --- | --- |
| Prim exists | `/World/PalletizingCell/Floor` | valid |
| Type name | `Cube` | `Cube` |
| Schema | `UsdGeomCube` | `UsdGeomCube` |
| World extent | 8.00 m × 6.00 m × 0.02 m ± 1 cm | 8.00 × 6.00 × 0.02 m |
| After replace | same path, no duplicate `_1` suffix | single prim |

A cube that exists with non-zero bounds is not the same as an 8 m × 6 m floor. If `RemovePrim` never ran, validation must show the old thickness still present, not a model sentence that says the floor was replaced.

## 8. Warehouse implication

An invented create API leaves the cell without a floor. Conveyor heights, pallet contact, and placeholder robot placement have no datum. An invented delete API is worse in a live stage: the old floor can remain, a second prim can appear under a suffixed path, or later retries can add duplicate XformOps. Throughput studies and customer walkthroughs then inherit geometry that was never the requested cell.

Placeholder floors are still not production structure. They are a layout datum. If the datum is wrong, every later “physics sim” screenshot is a picture of the wrong room.

## 9. Reusable checklist

- List every callable in the generated snippet (`UsdGeom.*`, `stage.*`, `Sdf.*`, helper names).
- Confirm each one against official `pxr` docs or a retrieved local signature.
- Reject English-shaped names (`Rect`, `Box`, `RemovePrimPath`, `GetStageFilePath`) unless the signature exists.
- Confirm schema-specific attributes: cube `size` is scalar; do not call `GetRadiusAttr` on a cube.
- Retrieve only the active step (define floor, remove floor). Exclude lighting, materials, and physics catalogs.
- Stop when the signature is absent. Do not emit a near-miss.
- After execution, record path, type name, and measured bounds—not only a viewport grab.

## 10. Repository connection

Run your own generated snippets through that signature audit, then compare them with the two skills that split the work:

- [`skills/omniverse-rag-routing/SKILL.md`](../../skills/omniverse-rag-routing/SKILL.md) — phase- and step-specific retrieval; no call without evidence.
- [`skills/omniverse-usd-authoring/SKILL.md`](../../skills/omniverse-usd-authoring/SKILL.md) — one scoped step of native OpenUSD Python.

The next post in this series keeps the same floor and shows a different failure: valid Python that still dies because the interpreter `eval()`s the last line.
