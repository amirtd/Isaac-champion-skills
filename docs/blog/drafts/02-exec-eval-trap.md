# Valid Python, Failed Agent: The Hidden `exec()` vs. `eval()` Trap

**Status:** Draft  
**Primary audience:** Isaac Sim and Omniverse developers, plus anyone wiring a code interpreter to a USD agent  
**Target environment:** Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`). Examples assume a Kit-supplied `stage`.  
**Skills:** [`omniverse-code-packaging`](../../skills/omniverse-code-packaging/SKILL.md)

Reconstructed examples are labeled. They are not copied from raw logs.

## The scene

Same palletizing cell. Same request: put a floor in Isaac Sim so the rest of the warehouse sim has something to stand on. This time the agent does not invent `UsdGeom.Rect`. It writes a cube, measures something, and ends with `assert floor_prim.IsValid()`.

That is legal Python. You can paste it into a `.py` file and it runs. The Omniverse interpreter still fails. It executed every line except the last with `exec()`, then handed the last line to `eval()`. `assert` is a statement. Four retries, four `SyntaxError` events, still no floor. The physics sim is waiting on a cell that never appeared.

## The solution in simple terms

Match generated code to the executor contract. If the last line is evaluated as an expression, do not end with `assert`, assignment, or `return`. Run checks first. End with a result object—a dictionary of paths, schemas, and measurements. Alternatively, change the executor so the entire block runs with `exec()`. Do not treat a traceback on `assert` as proof that the assertion was written wrong.

## Why the AI picked this pattern

Models generate file-style Python. In a file, a terminal `assert` is normal. The model has no built-in picture of “this runtime `eval`s the last line.” When the traceback says `SyntaxError`, the repair loop “fixes” names, comments, or formatting and leaves the `assert` in place. The model explains the repair without changing the line that the executor cannot evaluate.

## 1. Warehouse problem

The warehouse need is still a floor with a known path and thickness. Validation belongs in the same step: the prim exists, it is a cube, it has expected bounds. The team wants that evidence in the agent’s result, not a chat sentence that says “the floor is done.”

If packaging is wrong, the floor may already exist on the stage while the interpreter reports failure. Later retries then stack transforms or duplicate paths. The operational problem is not “Python syntax.” It is an untrusted mutation of the cell with no trustworthy status.

## 2. Observed failure

Reconstructed block that is valid as a script and invalid as an `eval` final line:

```python
from pxr import UsdGeom

floor = UsdGeom.Cube.Define(stage, "/World/PalletizingCell/Floor")
floor.GetSizeAttr().Set(1.0)
prim = stage.GetPrimAtPath("/World/PalletizingCell/Floor")
assert prim.IsValid()
```

Reconstructed executor behavior:

```text
# lines 1-5: exec()
# last line: eval("assert prim.IsValid()")
SyntaxError: invalid syntax
```

Across 65 substantive runs there were 21 `SyntaxError` interpreter events. Those events include retries, not 21 separate warehouse requests. Four attempts on one floor step, all dying on a terminal `assert`, is the pattern this article reconstructs. Other packaging failures in the same dataset included markdown or prose leaking into executable text, a JSON fence remaining inside a Python extraction, Unicode punctuation in code, broken f-strings, and missing indentation after generated function definitions.

## 3. Root cause

Python has statements and expressions. `eval()` accepts an expression. `assert`, `import` (as used in some blocks), assignment, `return`, and some `if` forms are statements. `exec()` accepts a suite.

A common agent executor splits a snippet, runs the prefix with `exec()`, and uses `eval()` on the last non-empty line so it can return a value to the orchestrator. That contract is invisible in the generated source. Newline preservation matters: if extraction collapses the block, the “last line” may be a different statement than the author intended. A fence such as ` ```json ` inside the Python string is also not an expression.

The failure is an interpreter contract, not malformed assertion syntax. Classifying it as `python_syntax` sends the repair loop to the wrong edit.

## 4. Why the obvious repair fails

The obvious repair is to rename a variable, add a comment, or “simplify” the assert:

```python
floor_prim = stage.GetPrimAtPath("/World/PalletizingCell/Floor")
assert floor_prim.IsValid()  # still a statement
```

The last line is unchanged in kind. The executor still `eval()`s it. A second obvious repair is to paste the traceback back into the model with “fix the syntax.” The model restates that `assert` is valid Python—which is true in a file—and regenerates the same shape.

A third failure mode: the model explains the packaging issue in prose and emits the same `assert` anyway. Explanation without a semantic patch is not a repair.

## 5. Reliable pattern

[`omniverse-code-packaging`](../../skills/omniverse-code-packaging/SKILL.md) applies after generation and before execution:

- Exactly one `python` fence when the executor requires a fence.
- No trailing prose, verification list, or second fence.
- Preserve newlines and indentation.
- If the interpreter evaluates the final line, that line must be an expression such as `result`.
- Keep checks before that expression.
- Reject empty, truncated, multi-block, or contaminated output before execution.

Correct patterns:

1. Run assertions or `if` checks before the last line; end with `result`.
2. Or change the executor to `exec()` the entire suite and read a well-known name from the namespace.
3. Report validation separately from execution status. A skipped validation is not a zero-error run.

## 6. Minimal code example

Author one cube, store checks in `result`, end with `result`.

```python
from pxr import Gf, Usd, UsdGeom

floor_path = "/World/PalletizingCell/Floor"
UsdGeom.Xform.Define(stage, "/World/PalletizingCell")

if stage.GetPrimAtPath(floor_path).IsValid():
    stage.RemovePrim(floor_path)

floor = UsdGeom.Cube.Define(stage, floor_path)
floor.GetSizeAttr().Set(1.0)
UsdGeom.Xformable(floor.GetPrim()).AddScaleOp(
    UsdGeom.XformOp.PrecisionFloat
).Set(Gf.Vec3f(800.0, 600.0, 2.0))

prim = stage.GetPrimAtPath(floor_path)
valid = bool(prim.IsValid())
type_ok = prim.GetTypeName() == "Cube"

cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
checks = {
    "prim_valid": valid,
    "type_is_cube": type_ok,
    "extent_nonzero": float(size[0]) > 0.0 and float(size[1]) > 0.0,
}

result = {
    "status": "ok" if valid and type_ok else "failed",
    "path": floor_path,
    "checks": checks,
    "evidence": {
        "type_name": prim.GetTypeName(),
        "size_stage": [float(size[0]), float(size[1]), float(size[2])],
    },
}
result
```

`extent_nonzero` is a packaging demo check only. Exact 8 m × 6 m tolerance belongs in the units and validation posts.

## 7. Validation

Execution success and validation evidence are different fields.

| Field | After `eval` trap | After expression-safe result |
| --- | --- | --- |
| Interpreter status | `SyntaxError` | completed |
| `result["status"]` | missing | `ok` or `failed` |
| Prim path | maybe mutated, unreported | `/World/PalletizingCell/Floor` |
| Type name | unreported | `Cube` |
| Validation | often `skipped` while chat says zero errors | recorded in `checks` |

If the prefix already defined the cube before `eval` failed, `changed_paths` can be non-empty. Do not describe that run as an unchanged stage.

## 8. Warehouse implication

A floor step that “failed” four times may still have a cube on the stage, or four overlapping transform ops, or nothing. A controls engineer who trusts the agent’s error summary can sign off a cell that has no floor, or a floor that was authored twice. Pallet transfer height and conveyor alignment are then measured against an unknown datum.

Packaging is not a style preference. It is how you know whether the warehouse sim was mutated.

## 9. Reusable checklist

- Document whether the executor `eval()`s the last line.
- End generated snippets with an expression (`result`) if it does.
- Put `assert` and other statements above that line.
- Strip markdown, JSON fences, and Unicode punctuation before execution.
- Preserve newlines and indentation through extraction.
- Treat “I fixed it” prose with an unchanged code hash as a failed repair.
- Record validation in the result object; do not infer success from the absence of a traceback.

## 10. Repository connection

Test your executor with a statement-only final line (`assert True`) and with a dictionary expression (`result`). Only the second should return a value if you use `eval` on the last line.

The packaging contract lives in [`skills/omniverse-code-packaging/SKILL.md`](../../skills/omniverse-code-packaging/SKILL.md). The next post keeps this floor and shows a different class of silent failure: the cell is 10× too large because units and Gf types were guessed.
