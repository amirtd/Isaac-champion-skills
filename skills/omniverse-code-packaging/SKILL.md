---
name: omniverse-code-packaging
description: Package generated Omniverse Python to match fenced-block, extraction, and interpreter input contracts.
---

# Omniverse Code Packaging

Apply after code generation and before execution.

## Contract

- Emit exactly one `python` fenced block when required by the executor.
- Put no prose, verification list, or second fence outside it.
- Preserve newlines and indentation through extraction.
- Do not reacquire a supplied `stage`.
- If the interpreter evaluates the final line, make it an expression such as `result`, not an assertion, assignment, return, or other statement.
- Keep checks before the final structured result expression.
- Reject empty, truncated, multi-block, or scope-expanding output before execution.

Return code hash, step id, expected final-value type, and extraction status separately from the executable text.
