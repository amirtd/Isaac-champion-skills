---
name: omniverse-scene-request
description: Normalize natural-language Omniverse scene requests against live outliner context before planning or code generation.
---

# Omniverse Scene Request

Produce a compact `SceneRequest` artifact. Do not author USD in this skill.

## Workflow

1. Separate explicit requirements from suggestions and defaults.
2. Reconcile the request with the outliner, selection, and added/removed-path delta. Mark each requested object as `create`, `update`, `reuse`, or `remove`; never infer removal from absence alone.
3. Normalize quantities, units, axes, dimensions, placement relationships, asset requirements, and acceptable placeholder geometry.
4. Surface only ambiguities that materially change geometry or behavior. Otherwise record a conservative assumption.
5. Reject scope expansion: requested robots, conveyors, pallets, and shelves do not imply PLCs, safety systems, animation, or simulation.

Return `request_id`, `intent`, `stage_observations`, `components`, `relationships`, `constraints`, `assumptions`, `open_questions`, and `out_of_scope`. Preserve source units alongside normalized stage-unit values.
