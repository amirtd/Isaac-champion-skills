# Warehouse USD agent blog

Drafts for a technically credible series on warehouse automation scene generation in NVIDIA Isaac Sim, OpenUSD, and Omniverse.

The series teaches readers how to move from an informal warehouse request to a structured, validated USD scene without relying on one-shot prompting. It is based on sanitized aggregate failure evidence and the skills in this repository (core USD pipeline plus warehouse layout constraints).

**Thesis:** Reliable warehouse scene generation is not primarily a prompting problem. It is a staged engineering workflow.

## Article template

Every post uses a 13-part structure: three first-time-reader blocks, then a ten-section technical body. See [editorial-brief.md](editorial-brief.md) section 9.

1. The scene
2. The solution in simple terms
3. Why the AI picked this pattern
4. Warehouse problem
5. Observed failure
6. Root cause
7. Why the obvious repair fails
8. Reliable pattern
9. Minimal code example
10. Validation
11. Warehouse implication
12. Reusable checklist
13. Repository connection

## Tier 1 drafts

All five drafts share one palletizing-cell story. Each post peels a different failure layer.

| Draft | Title | Skills |
| --- | --- | --- |
| [01-usd-api-hallucinations.md](drafts/01-usd-api-hallucinations.md) | Why USD Agents Invent APIs—and How to Stop Them | `omniverse-rag-routing`, `omniverse-usd-authoring` |
| [02-exec-eval-trap.md](drafts/02-exec-eval-trap.md) | Valid Python, Failed Agent: The Hidden `exec()` vs. `eval()` Trap | `omniverse-code-packaging` |
| [03-units-and-gf-types.md](drafts/03-units-and-gf-types.md) | Meters, Centimeters, and Quaternion Types | `omniverse-stage-preflight`, `omniverse-usd-validation` |
| [04-palletizing-request-to-plan.md](drafts/04-palletizing-request-to-plan.md) | From a Palletizing Request to an Executable USD Plan | `omniverse-scene-request`, `omniverse-usd-planning` |
| [05-palletizing-case-study.md](drafts/05-palletizing-case-study.md) | Building a Palletizing Cell with an AI Agent: An Honest End-to-End Case Study | workflow plus packaging, request, plan, preflight, author, validate |

## Evidence

- [data/aggregate-error-counts.json](data/aggregate-error-counts.json) — interpreter-event counts from the editorial brief
- [data/sanitized-examples.json](data/sanitized-examples.json) — reconstructed failure/correction pairs
- [data/api-verification.json](data/api-verification.json) — Isaac Sim 5.0 / OpenUSD API cross-check

Do not place raw private logs under `docs/blog/data`. Only derived, reviewed, sanitized material belongs here.

## Target environment

Isaac Sim 5.0.0 (`VERSION` `5.0.0-rc.45`). USD Python bindings (`pxr`) load with Kit, not a standalone `python.exe`. Headless `python.bat -c "from pxr import Usd"` did not import `pxr` in this authoring session. Draft APIs follow OpenUSD 24.x schema documentation and in-tree Isaac Sim 5.0 usage (`UsdGeom.Cube.Define`, `stage.RemovePrim`, `UsdGeom.GetStageMetersPerUnit`, `UsdGeom.BBoxCache.ComputeWorldBound`, `UsdGeom.XformOp.PrecisionFloat`).

## Claims

Avoid “production ready,” “safe,” or “guaranteed.” Use “validated against these checks.” Placeholder geometry is not a production robot, conveyor, or safety system.
