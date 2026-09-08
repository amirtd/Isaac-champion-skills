# Isaac Champion Skills

Reusable agent skills for planning, generating, executing, validating, and repairing OpenUSD Python workflows in NVIDIA Omniverse and Isaac Sim.

This repository turns a scene request into a bounded USD plan, retrieves only relevant context, generates one scoped Python step at a time, executes it safely, and records consistent validation and diagnostic evidence.

## Skill set

- `omniverse-scene-request` — normalizes the user request against stage context.
- `omniverse-usd-planning` — creates dependency-ordered, machine-checkable steps.
- `omniverse-stage-preflight` — verifies stage units, axes, editability, and path state.
- `omniverse-rag-routing` — selects compact step-specific OpenUSD context.
- `omniverse-usd-authoring` — generates focused OpenUSD Python.
- `omniverse-code-packaging` — enforces code-fence and interpreter contracts.
- `omniverse-safe-execution` — provides idempotency, snapshots, and rollback tracking.
- `omniverse-usd-validation` — verifies paths, schemas, transforms, bounds, and clearances.
- `omniverse-cell-layout` — handles industrial robot, conveyor, pallet, and rack layout.
- `omniverse-error-repair` — classifies failures and prevents duplicate retries.
- `omniverse-diagnostics` — provides the shared error, warning, and alert model.

The complete routing and artifact flow is defined in [`skill-set.yaml`](skill-set.yaml).

## Installation

Clone the repository, then copy the desired folders from `skills/` into your Codex skills directory. Each skill is self-contained and includes a `SKILL.md` entry point plus UI metadata in `agents/openai.yaml`.

Example on Windows:

```powershell
git clone https://github.com/amirtd/Isaac-champion-skills.git
Copy-Item -Path '.\Isaac-champion-skills\skills\omniverse-*' -Destination 'C:\Users\YOUR-NAME\.codex\skills' -Recurse
```

Restart or reload Codex after installation.

## Workflow

```text
request -> plan -> preflight -> RAG -> author -> package -> execute -> validate
                                      ^                    |
                                      +------ repair <-----+

diagnostics records every phase
```

`omniverse-cell-layout` is invoked only for industrial spatial reasoning. Error repair is invoked only after packaging, execution, or validation fails.

## Safety

- Review generated Python before using it on an important stage.
- Test mutating workflows on disposable or version-controlled USD layers first.
- Do not place API keys, repository tokens, or customer data in skill files.
- Placeholder geometry is not a substitute for production robot assets, articulation data, or engineering safety review.

## Status

Initial experimental release. The skills are designed to improve agent behavior but do not guarantee valid mechanical layouts or safe production-cell designs.

This is an independent community project and is not affiliated with or endorsed by NVIDIA or OpenAI.
