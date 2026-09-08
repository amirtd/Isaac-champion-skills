---
name: omniverse-rag-routing
description: Select compact, step-specific OpenUSD and Omniverse retrieval context for planning, generation, validation, or repair.
---

# Omniverse RAG Routing

Retrieve against the current phase and active step, not the whole project.

## Routing rules

- Build queries from operation, schema, transform, validation method, and exact failure signature.
- Prefer authoritative native `pxr` APIs and verified local helper signatures.
- Rank exact schema and operation matches above lexical or domain-word overlap.
- Exclude unrelated materials, lighting, load rules, physics, camera, selection, and examples.
- Deduplicate by callable or topic and cap results to the smallest sufficient set.
- Retrieve once per unchanged step. Reuse context on retry unless the failure identifies a concrete knowledge gap.
- Keep core rules separate from retrieved APIs and conversational retry history.

Return `RagBundle` with query purpose, selected items, rejected high-scoring items and reasons, source/version, and context size.
