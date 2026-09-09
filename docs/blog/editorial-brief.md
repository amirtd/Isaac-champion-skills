# Warehouse Automation + USD Agent Blog Program

## Editorial and Production Brief

**Status:** Ready for development in Cursor  
**Last updated:** 2026-09-08  
**Primary repository:** <https://github.com/amirtd/Isaac-champion-skills>  
**Internal evidence source:** Local agent-run JSON logs (not committed). Derived, reviewed counts live in `docs/blog/data/`.  

## 1. What We Are Building

We want to create a technically credible blog series for warehouse automation professionals who use NVIDIA Isaac Sim, OpenUSD, Omniverse, AI coding agents, or other language models to generate and modify USD scenes.

The series should teach readers how to move from an informal warehouse request—such as “create a palletizing cell with a robot, conveyors, pallets, and a rack”—to a structured, validated USD scene without relying on fragile one-shot prompting.

The blogs will be based on two concrete sources:

1. Real agent-run JSON logs that expose common generation, execution, retry, RAG, and validation failures.
2. The reusable skills published in the `Isaac-champion-skills` repository, which turn those observed failures into a more reliable workflow (core USD pipeline plus conditional warehouse layout skills).

The content should not read like generic AI advice. Every article should connect an actual failure pattern to an OpenUSD or warehouse-automation concept, demonstrate the operational consequence, and provide a reusable prevention or recovery technique.

## 2. Core Editorial Thesis

The central thesis is:

> Reliable warehouse scene generation is not primarily a prompting problem. It is a staged engineering workflow involving request normalization, scene planning, stage inspection, targeted retrieval, correct USD authoring, safe execution, evidence-based validation, and disciplined error recovery.

The blogs should consistently reinforce five ideas:

- A plausible-looking USD scene is not necessarily structurally, dimensionally, or mechanically correct.
- OpenUSD API correctness matters more than confident model output.
- Warehouse intent must be translated into constraints before coordinates are generated.
- Agent execution must be idempotent because retries can partially mutate a live stage.
- Validation evidence—not a model’s success statement—determines whether a step succeeded.

## 3. Target Audiences

### 3.1 Warehouse automation engineers

Readers who understand conveyors, pallet flow, robot cells, racking, controls, and safety but may not be OpenUSD specialists.

They need:

- Familiar warehouse examples.
- Clear explanations of coordinate systems and units.
- Confidence that generated layouts preserve operational constraints.
- A distinction between conceptual placeholder geometry and engineering-ready assets.

### 3.2 Isaac Sim and Omniverse developers

Readers who already build simulations but are experimenting with AI-generated Python and USD.

They need:

- Correct `pxr` API patterns.
- Reliable stage, layer, transform, and schema handling.
- Debugging techniques for `pxr.Tf.ErrorException`, `AttributeError`, and Boost.Python signature failures.
- Strategies for running generated code without corrupting the stage.

### 3.3 Digital-twin and simulation teams

Readers responsible for converting layout requirements, CAD data, process definitions, or customer documents into maintainable digital twins.

They need:

- Repeatable scene hierarchy conventions.
- Traceability between requirements, plan steps, generated code, and validation.
- Methods for detecting stale stage context and unexpected changes.
- Guidance for integrating AI into an existing review process.

### 3.4 Agent and RAG developers

Readers building model-agnostic systems around Codex, Claude, Gemini, local models, LangChain, or custom orchestration.

They need:

- Typed artifacts between workflow phases.
- Retrieval-quality and context-budget guidance.
- Retry classification and semantic deduplication.
- Consistent diagnostics and evaluation data.

### 3.5 Technical decision-makers

Engineering managers and innovation leaders assessing whether generative scene authoring is ready for production use.

They need:

- Honest failure rates and risk boundaries.
- A maturity model rather than a product demonstration.
- Clear separation between productivity acceleration and engineering approval.
- Practical adoption steps that do not require replacing the existing toolchain.

## 4. Evidence from the JSON Logs

The current dataset contains 155 JSON files, of which 65 are substantive runs and 90 are empty network shells. Across the substantive runs, the analysis found:

- 247 recorded interpreter attempts.
- 110 successful interpreter events and 137 failed interpreter events.
- 29 runs with at least one interpreter failure.
- 9 runs that reached a maximum-retry condition.
- 53 `AttributeError` events.
- 34 `pxr.Tf.ErrorException` events.
- 21 `SyntaxError` events.
- 6 Boost.Python argument-signature errors.
- 6 validation `AssertionError` events.
- 5 `RuntimeError` events.
- 4 `IndentationError` events.
- 3,019 retrieved metafunction records representing 486 unique method/class combinations.
- Five runs with semantically duplicate generated attempts, accounting for 13 unnecessary retries.

These counts represent interpreter events, including retries, rather than 137 independent user requests. Blog articles must explain this distinction whenever statistics are quoted.

### 4.1 Recurring API hallucinations

Examples include:

- `UsdGeom.Rect`
- `UsdGeom.Box`
- `UsdGeom.StageComputeMetrics`
- `Stage.RemovePrimPath`
- `Stage.GetStageFilePath`
- `Stage.IsEditable`
- `Sdf.Path.split`
- `Sdf.Path.GetString`
- `Sdf.Path.GetAllNames`
- `BBox3d.ComposeAlignedRange`
- `Xformable.GetXformOpByIndex`
- Schema-specific calls on the wrong type, such as `Cube.GetRadiusAttr`

This is the strongest evidence for articles about signature-grounded generation, native `pxr` APIs, and targeted RAG.

### 4.2 USD authoring failures

Observed problems include:

- Empty or non-absolute prim paths.
- Re-adding an XformOp that already exists in `xformOpOrder`.
- Authoring `GfQuatd` where an attribute expects `GfQuatf`.
- Passing `Gf.Vec3d` to an API requiring `Gf.Vec3f`.
- Accessing a schema on an invalid prim.
- Treating cube size as a three-dimensional vector.
- Creating raw scalar `displayColor` attributes instead of using the appropriate Gprim display-color API.
- Calling unsupported methods such as `SetInheritable`, `GetColorAttr`, or schema-level `SetCustomData`.

### 4.3 Code packaging and execution failures

The executor commonly ran all lines except the final line with `exec()` and then evaluated the final line with `eval()`. This caused valid statement syntax—especially terminal `assert` statements—to fail as `SyntaxError`.

Additional failures came from:

- Markdown or explanatory prose leaking into executable code.
- A JSON fence remaining inside a Python extraction.
- Unicode punctuation appearing as code.
- Broken f-strings.
- Missing indentation after generated function definitions.
- Models explaining a repair without making a meaningful code change.

### 4.4 Retry and mutation risks

Some failures occurred only after earlier lines had already modified the live stage. A reported failure therefore did not prove that the scene was unchanged. Re-running nearly identical code could then:

- Re-author existing prims.
- Add duplicate transform operations.
- Create suffixed duplicate paths.
- Leave partially configured components.
- Make later validation evidence ambiguous.

This supports a major content theme around idempotency, snapshots, rollback, changed-path evidence, and semantic retry detection.

### 4.5 Unit, scale, and layout errors

The logs show confusion among meters, centimeters, millimeters, and stage units. Examples include an 8 m × 6 m cell becoming 8,000 cm × 6,000 cm and implausible robot reach assumptions.

Other layout issues include:

- Components extending beyond the floor or cell boundary.
- A shelf described as being against a wall without a defined wall orientation.
- Ambiguity between two conveyors and two inbound plus two outbound conveyors.
- Robot placeholders being treated as though they represented real articulation or vendor reach.
- Validation that checked only non-zero bounds rather than exact dimensions and clearances.

### 4.6 RAG overload and poor retrieval relevance

Large prompts repeatedly included broad function catalogs and unrelated examples. Frequently retrieved items included material tracing, lighting, load rules, physics helpers, cache utilities, and Beckhoff-specific navigation functions, even when the active step only needed an Xform and a floor cube.

System context ranged from roughly 78,000 characters to more than 427,000 characters. The blog program should use this as evidence that retrieval quality, separation of concerns, and context budgets matter more than simply adding more documentation.

### 4.7 Diagnostics inconsistencies

Some runs contained multiple failed interpreter events while their top-level error summary still reported zero errors. Validation was sometimes marked `skipped` without being reflected in the final user-facing status.

This supports content about canonical event models, derived error counts, normalized signatures, partial-mutation status, and evidence-grounded reporting.

## 5. The Skills as the Solution Framework

The blogs should introduce the skills as reusable responsibilities rather than marketing them as magic prompts.

| Skill | Responsibility | Blog problems it addresses |
|---|---|---|
| `omniverse-scene-request` | Normalize intent and reconcile it with the outliner or scene delta. | Stale context, quantity ambiguity, scope expansion, unit ambiguity. |
| `omniverse-warehouse-layout-intent` | Normalize facility zones, flow axes, and aisle targets. | Zone floor plans jumping to guessed rack cubes; missing provenance. |
| `omniverse-cell-layout` | Produce `CellLayoutPlan` constraints for robot cells before XYZ. | Guessed coordinates, dual-zone ambiguity, scope expansion to fence/PLC. |
| `omniverse-material-flow` | Resolve inbound/outbound pairing, buffers, and transfer points. | “2 conveyors” ambiguity; product vs pallet path confusion. |
| `omniverse-reach-and-transfer` | Label reach envelopes and transfer-height pairs without fake IK. | Vendor-as-geometry; late reach checks; invented kinematics. |
| `omniverse-storage-racking` | Plan rack/shelf bays, loading faces, and aisle widths. | Anonymous rack cubes without bay/aisle constraints. |
| `omniverse-usd-planning` | Produce dependency-ordered, machine-checkable authoring steps. | One-shot generation, schema/acceptance mismatch, unbounded plans. |
| `omniverse-stage-preflight` | Inspect stage, units, axes, edit target, parents, and target paths. | Invalid prims, wrong units, incompatible existing paths. |
| `omniverse-rag-routing` | Select minimal phase- and step-specific API context. | Irrelevant retrieval, prompt bloat, helper hallucination. |
| `omniverse-usd-authoring` | Generate correct scoped OpenUSD Python. | Invented schemas, incorrect attributes, unsafe transform authoring. |
| `omniverse-code-packaging` | Match extraction and interpreter contracts. | Multiple fences, trailing prose, `exec`/`eval` final-line failures. |
| `omniverse-safe-execution` | Execute idempotently with snapshots and rollback awareness. | Partial mutation, duplicate paths, repeated XformOps. |
| `omniverse-usd-validation` | Measure prims, schemas, transforms, bounds, and clearances. | False success, non-zero-only validation, missing evidence. |
| `omniverse-layout-validation` | Measure footprint, flow, reach, and aisle contracts. | Prose-only clearances; unpaired inbound/outbound; unvalidated reach. |
| `omniverse-error-repair` | Classify causes and require meaningful repair changes. | Duplicate retries, wrong causal diagnosis, context growth. |
| `omniverse-diagnostics` | Provide a shared error, warning, alert, and aggregation model. | Zero-error summaries after failure, inconsistent statuses. |

The preferred workflow is:

```text
request
  -> normalized scene request
  -> layout constraints (intent / cell / flow / reach / racking as needed)
  -> dependency-ordered USD plan
  -> stage preflight
  -> targeted RAG bundle
  -> one scoped Python authoring step
  -> interpreter-safe packaging
  -> idempotent execution
  -> independent USD validation evidence
  -> layout validation evidence when layout artifacts exist
  -> accept, repair, or stop

diagnostics observes and summarizes every phase
```

## 6. Editorial Content Pillars

### Pillar A: From warehouse intent to a USD plan

Teach readers to translate operational language into components, paths, constraints, dependencies, and acceptance criteria.

Topics include:

- Normalizing a warehouse prompt.
- Separating requested scope from helpful but unrequested additions.
- Converting relationships into constraints before coordinates.
- Creating executable plan steps.
- Tracking changes when the user revises the prompt.

### Pillar B: Correct OpenUSD authoring

Teach model users enough USD semantics to recognize plausible-looking but invalid generated code.

Topics include:

- Schema discovery.
- Prim paths and hierarchy.
- XformOps and transform order.
- Scalar versus vector attributes.
- Gf type precision.
- Display color and materials.
- Stage units and up axis.

### Pillar C: Safe agent execution

Treat generated code as a stage mutation that requires lifecycle controls.

Topics include:

- Packaging contracts.
- `exec()` versus `eval()`.
- Idempotency.
- Snapshots and rollback.
- Partial mutation detection.
- Retry budgets and semantic change detection.

### Pillar D: Warehouse validation

Connect USD measurements to warehouse automation requirements.

Topics include:

- Exact dimensions and tolerance.
- Robot reach assumptions.
- Conveyor transfer height.
- Rack loading orientation.
- Pallet footprint.
- Component containment.
- Clearances and collision proxies.
- Placeholder versus production assets.

### Pillar E: RAG and agent architecture

Explain how to build a model-independent system rather than relying on a single large prompt.

Topics include:

- Phase-specific retrieval.
- Function signature verification.
- Context budgets.
- Typed artifacts.
- Shared diagnostics.
- Evaluation sets built from failed runs.

## 7. Prioritized Blog Backlog

### Tier 1: Publish first

1. **Why USD Agents Invent APIs—and How to Stop Them**  
   Use the recurring `AttributeError` examples to explain API hallucination, schema verification, and signature-grounded retrieval.

2. **Valid Python, Failed Agent: The Hidden `exec()` vs. `eval()` Trap**  
   Reconstruct the terminal-assert failure and show an expression-safe validation result.

3. **Meters, Centimeters, and Quaternion Types: Unit Bugs in Warehouse Digital Twins**  
   Explain `metersPerUnit`, stage-unit normalization, cube dimensions, and Gf precision types.

4. **From “Build a Palletizing Cell” to an Executable USD Plan**  
   Convert a robot–conveyor–pallet–shelf request into scoped, dependency-ordered steps.

5. **Building a Palletizing Cell with an AI Agent: An Honest End-to-End Case Study**  
   Present the complete journey from prompt through failure analysis to a validated workflow.

### Tier 2: Reliability series

6. **Idempotent USD Authoring: Making Agent Retries Safe**
7. **How to Read `pxr.Tf.ErrorException` Without Guessing**
8. **The Cube Is Not a Box: USD Primitive Semantics for AI Agents**
9. **Preflight Before Python: Inspecting an Isaac Sim Stage Before Mutation**
10. **Beyond “The Prim Exists”: Validating an AI-Generated Warehouse Scene**
11. **Rollback for Generative USD: What Happens After Partial Failure?**
12. **Stop Retrying the Same Code: Semantic Retry Detection for USD Agents**

### Tier 3: Architecture and warehouse practice

13. **RAG Overload in USD Agents: Why More Context Can Produce Worse Code**
14. **Scene Deltas Matter: What Changed Since the User’s Last Prompt?**
15. **Placeholder Robot or Real Digital Twin? Setting Expectations for Generated Scenes**
16. **Designing Conveyors, Pallets, and Racks with Constraints Instead of Guessed Coordinates**
17. **One Error Model for the Whole USD Agent Pipeline**
18. **A Model-Agnostic Architecture for Warehouse USD Agents**
19. **Turning Failed Agent Runs into a USD Evaluation Dataset**
20. **A Production-Readiness Checklist for AI-Generated Warehouse Scenes**

## 8. Detailed Briefs for the First Five Posts

## Post 1: Why USD Agents Invent APIs—and How to Stop Them

### Reader promise

The reader will learn why a model can produce convincing but nonexistent USD calls and how to design generation and retrieval so every important callable is grounded in a real schema or verified helper signature.

### Hook

Open with a short piece of generated code using `UsdGeom.Rect` or `Stage.RemovePrimPath`. Ask why code that looks completely reasonable fails immediately inside Isaac Sim.

### Suggested outline

1. What API hallucination looks like in USD.
2. Why OpenUSD is particularly vulnerable: broad schema surface, Python/C++ bindings, version differences, schema-specific attributes, and plausible naming conventions.
3. Examples from the logs.
4. Native schema discovery versus speculative method construction.
5. A retrieval hierarchy:
   - Exact official/local signature.
   - Exact schema documentation.
   - Known tested wrapper.
   - Generate no call when evidence is absent.
6. Pre-generation checks and post-generation static review.
7. How `omniverse-rag-routing` and `omniverse-usd-authoring` divide responsibility.
8. A small before/after example.

### Demonstration

Create a floor and delete or replace it using verified APIs. Contrast hallucinated calls with `UsdGeom.Cube.Define`, `stage.GetPrimAtPath`, and `stage.RemovePrim` where appropriate.

### CTA

Invite readers to run their own generated snippets through a signature audit and review the public RAG-routing and authoring skills.

## Post 2: Valid Python, Failed Agent: The Hidden `exec()` vs. `eval()` Trap

### Reader promise

The reader will understand how the code-interpreter contract changes what counts as valid generated output and how to design a structured final expression that carries validation evidence.

### Hook

Use the floor example where four attempts failed on a syntactically valid `assert` because the interpreter applied `eval()` to the last line.

### Suggested outline

1. Why the same code succeeds in a `.py` file and fails in an agent executor.
2. Statements versus expressions.
3. How code extraction, fencing, and newline preservation affect execution.
4. Common contaminants: prose, JSON fences, Unicode punctuation, and incomplete functions.
5. The wrong repair: rename a variable but leave the final statement unchanged.
6. The correct patterns:
   - Run assertions before the last line.
   - End with a result dictionary expression.
   - Or change the executor to use `exec()` consistently.
7. Pre-execution packaging checks.
8. How to report validation separately from execution.

### Demonstration

Show a minimal code block that authors one cube, measures its bounds, stores checks in `result`, and ends with `result`.

### CTA

Link readers to `omniverse-code-packaging` and invite them to test their executor with statement-only final lines.

## Post 3: Meters, Centimeters, and Quaternion Types

### Reader promise

The reader will be able to prevent scale errors that make a warehouse cell 10× or 100× too large and avoid binding errors caused by incorrect Gf value types.

### Hook

Compare an intended 8 m × 6 m cell with a generated 8,000 cm × 6,000 cm boundary.

### Suggested outline

1. Physical units versus numeric USD stage values.
2. Reading `metersPerUnit` before authoring.
3. Preserving source units in the normalized request.
4. Cube base size and rectangular scaling.
5. Centered geometry versus floor-contact placement.
6. `Vec3f` versus `Vec3d` and `Quatf` versus `Quatd`.
7. Tolerance-based dimension validation.
8. Warehouse sanity checks for pallet, conveyor, rack, cell, and robot dimensions.

### Demonstration

Author the same floor on stages with different unit metadata and prove that the world-space physical size remains consistent.

### CTA

Offer a unit-normalization checklist derived from `omniverse-stage-preflight` and `omniverse-usd-validation`.

## Post 4: From a Palletizing Request to an Executable USD Plan

### Reader promise

The reader will learn to decompose a warehouse request into independent scene-authoring steps with explicit dependencies and acceptance contracts.

### Hook

Start with: “Need a basic palletization cell with a robot arm and 2 conveyors and pallets and a shelf.” Show how many unresolved assumptions exist inside that one sentence.

### Suggested outline

1. Extract requested components and quantities.
2. Reconcile the request with the current outliner.
3. Separate required scope from optional PLC, safety, material, and animation enhancements.
4. Normalize units and placement relationships.
5. Establish hierarchy and stable paths.
6. Plan in dependency order:
   - Cell root and floor.
   - Robot placeholder or referenced asset.
   - Conveyors.
   - Pallets.
   - Rack or shelf.
   - Validation.
7. Give every step measurable acceptance criteria.
8. Add rollback scope and RAG queries.

### Demonstration

Present a compact machine-readable plan and execute only the first step. Show how the plan prevents the model from building later components prematurely.

### CTA

Ask readers to compare their current prompts with the `SceneRequest` and `UsdPlan` artifacts used by the public skills.

## Post 5: Honest End-to-End Palletizing Cell Case Study

### Reader promise

The reader will see both the benefits and limitations of agent-generated warehouse scenes, including failures, repair decisions, and final evidence.

### Suggested outline

1. The original warehouse request.
2. Existing scene context and removed-path delta.
3. The first generated plan.
4. What the plan did well.
5. Scope expansion and dimensional assumptions.
6. The four failed Python attempts.
7. Root cause: executor packaging, not assertion syntax.
8. The revised skill-based workflow.
9. Correct step implementation.
10. Validation evidence: paths, schemas, dimensions, transforms, and changed paths.
11. What still requires an automation engineer’s approval.
12. Lessons for other models and orchestration frameworks.

### Demonstration

Include a side-by-side timeline of the original agent run and the improved pipeline. If possible, include viewport images of the initial stage, partial state, and validated scene.

### CTA

Direct readers to the complete public skill suite and invite reproducible issue reports using the normalized diagnostic format.

## 9. Standard Article Structure

Every technical article uses **13 parts**. The first three are for readers who have never touched OpenUSD or agent internals. The next ten are the specialist body.

Opening 3 and body section 3 will overlap if they are not split: **opening 3 = model behavior in English; body 3 = bound API / interpreter / units evidence.**

### Opening (plain language, no API tour)

1. **The scene:** A human-readable story of an Omniverse / Isaac Sim warehouse physics simulation and an AI agent that tried to generate it. Name the cell (robot, conveyors, pallets, rack/shelf, floor). Say what a person would see go wrong (crash, oversized cell, no floor, “success” with a broken stage). Do not claim placeholder robots have real PhysX, kinematics, or safety.
2. **The solution in simple terms:** One short paragraph: what to do instead. Prefer operational language (inspect the stage, retrieve a real API, end with a result object, convert units, plan before coordinates). Skill names can wait until body sections 5 and 10.
3. **Why the AI picked this pattern:** Causal, not moral. Models complete plausible names, emit `.py`-file Python, treat numbers as labels, and one-shot “helpful” scenes.

### Body (warehouse to repository)

4. **Warehouse problem:** Begin with a real scene-building task or operational requirement.
5. **Observed failure:** Show a small sanitized log or code excerpt. Label aggregate counts as interpreter events, including retries, not unique user requests.
6. **Root cause:** Identify the exact USD, executor, RAG, or workflow cause.
7. **Why the obvious repair fails:** Address the most likely superficial fix.
8. **Reliable pattern:** Present the prevention or recovery technique, tied to one or two skills.
9. **Minimal code example:** Use the smallest complete example that demonstrates the principle.
10. **Validation:** Show measured evidence, not only viewport appearance.
11. **Warehouse implication:** Explain why the issue matters for layout, simulation, throughput analysis, or handoff.
12. **Reusable checklist:** Give the reader a compact action list.
13. **Repository connection:** Link only to the specific relevant skills, not the full skill set by default.

Series frame: the same palletizing cell, each post peeling one failure layer. Physics sim means Isaac Sim warehouse simulation, not a claim that the generated cell is engineering-approved.

## 10. Technical Editorial Standards

### 10.1 Accuracy

- Verify every `pxr` method and schema against the actual target Isaac Sim/OpenUSD environment.
- State the tested Isaac Sim and USD versions in each code-heavy article.
- Do not claim that a placeholder robot has real kinematics, reach, payload, collision, or safety properties.
- Distinguish USD validity, visual correctness, simulation readiness, and production engineering approval.
- Do not present an inferred dimension as a vendor specification.

### 10.2 Units

- Show the user’s source unit and the normalized stage value.
- Read stage unit metadata in examples rather than assuming centimeters.
- Use physical-unit sanity checks for common warehouse objects.
- State whether dimensions describe full extent, radius, diameter, half extent, or scale.

### 10.3 Code

- Prefer short, executable examples.
- Use native `pxr` schemas unless the article specifically evaluates a wrapper.
- Avoid hidden globals other than an explicitly supplied `stage`.
- Do not end interpreter examples with a statement when the demonstrated executor evaluates the final line.
- Make retries idempotent.
- Capture actual measured values in the validation result.

### 10.4 Logs and privacy

- Never publish raw JSON logs.
- Remove local paths, user names, customer names, model credentials, UUIDs, and proprietary document contents.
- Rewrite prompts when necessary to preserve the technical issue without exposing private data.
- Use aggregate counts and short sanitized excerpts.
- Clearly label reconstructed examples.

### 10.5 Claims

- Avoid broad claims such as “production ready,” “safe,” or “guaranteed.”
- Use “validated against these checks” instead of “correct.”
- Explain whether statistics count runs, attempts, retries, or unique error signatures.
- Separate observations from the local dataset from general conclusions.

## 11. Visual and Demonstration Strategy

Each major article should contain at least two of the following when practical:

- An Isaac Sim viewport image.
- A compact outliner before/after view.
- A code before/after comparison.
- A plan-step or typed-artifact example.
- A measured bounds or transform table.
- A pipeline diagram.
- A failure/repair timeline.
- A retrieval relevance comparison.

Viewport images alone are insufficient for validation articles. Pair them with hierarchy, schema, transform, or bound evidence.

## 12. Suggested Repository Content Organization

If the blog source will live inside this repository, use:

```text
docs/
  blog/
    README.md
    editorial-brief.md
    drafts/
      01-usd-api-hallucinations.md
      02-exec-eval-trap.md
      03-units-and-gf-types.md
      04-palletizing-request-to-plan.md
      05-palletizing-case-study.md
    assets/
      diagrams/
      screenshots/
      code/
    data/
      aggregate-error-counts.json
      sanitized-examples.json
```

Do not place raw private logs under `docs/blog/data`. Only derived, reviewed, sanitized material should be committed.

## 13. Twelve-Week Publishing Roadmap

### Weeks 1–2: Establish authority

- Publish the API-hallucination article.
- Publish the `exec()` versus `eval()` article.
- Add a short repository page explaining the skill workflow (core pipeline plus layout constraints).

### Weeks 3–4: Solve physical-scene problems

- Publish the units and Gf-types article.
- Publish the cube and primitive-semantics article.

### Weeks 5–6: Introduce the workflow

- Publish prompt-to-plan.
- Publish stage preflight.

### Weeks 7–8: Reliability

- Publish idempotent retries.
- Publish USD validation beyond prim existence.

### Weeks 9–10: Retrieval and diagnostics

- Publish RAG overload.
- Publish the unified-diagnostics article.

### Weeks 11–12: Integrate the story

- Publish the end-to-end palletizing case study.
- Publish the production-readiness checklist.

## 14. Success Metrics

Track metrics that indicate useful technical adoption rather than only page views:

- Repository visitors and skill-folder views.
- GitHub stars, forks, clones, and issues.
- Readers who copy or reference a specific skill.
- Newsletter or update subscriptions.
- Qualified questions from warehouse, robotics, or digital-twin teams.
- Reproducible bug reports using the diagnostic event format.
- Reduction in duplicate questions after publishing foundational posts.
- Search traffic for exact failure terms such as `pxr.Tf.ErrorException`, `xformOp already exists`, `UsdGeom Cube size`, and `Sdf.Path split`.

## 15. Definition of Done for Each Post

A draft is ready for publication only when:

- It identifies one primary audience and one primary problem.
- Every API in the code sample has been tested in the stated environment.
- The example preserves correct units and expected schema types.
- The failure excerpt is sanitized.
- The root cause is separated from secondary symptoms.
- The repair is materially different from the failed attempt.
- Validation includes recorded evidence.
- Warehouse implications are explained.
- The article links to only the relevant skill files.
- The title, description, headings, and code terms support technical search discovery.
- The article includes a clear next action for the reader.

## 16. Immediate Next Steps in Cursor

1. Create `docs/blog/drafts` and `docs/blog/assets` in the chosen publication repository.
2. Copy this brief to `docs/blog/editorial-brief.md` if the blog will live with the skill repository.
3. Build a sanitized evidence file containing error category, frequency, representative failure, corrected pattern, and relevant skill.
4. Draft Post 1 using the detailed brief above.
5. Test every Post 1 code snippet in the actual Isaac Sim Python environment.
6. Capture one clean API-hallucination failure and one corrected viewport/outliner result.
7. Review the draft for private paths and proprietary content.
8. Add links to the relevant public skills.
9. Publish the first article, collect technical feedback, and use it to refine the remaining briefs.

## 17. Suggested Cursor Handoff Prompt

Use the following request when beginning implementation in Cursor:

```text
Read WAREHOUSE_USD_AGENT_BLOG_BRIEF.md and the public skill definitions in
https://github.com/amirtd/Isaac-champion-skills.

Create the blog source structure described in the brief and draft the first post,
“Why USD Agents Invent APIs—and How to Stop Them.” Use only sanitized aggregate
evidence from the brief. Do not copy raw private JSON logs into the repository.
Verify every OpenUSD API used in example code against the local Isaac Sim/OpenUSD
environment. Keep the article focused on warehouse automation and connect the
solution specifically to omniverse-rag-routing and omniverse-usd-authoring.
```

## 18. Intended Outcome

The final blog program should make the public skill repository useful in three ways:

1. **Education:** Help warehouse automation teams understand the real technical failure modes of AI-generated USD.
2. **Adoption:** Give teams a staged workflow they can implement with their preferred model or orchestration framework.
3. **Credibility:** Demonstrate that the skill design came from observed failures, measured evidence, and practical Isaac Sim scene-building requirements.

The content should leave readers with a realistic conclusion: AI agents can accelerate warehouse USD authoring, but dependable results require explicit contracts, constrained retrieval, safe execution, and independent validation.
