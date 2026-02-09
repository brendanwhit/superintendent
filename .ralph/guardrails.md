# Guardrails

Learned failure patterns and things to avoid.

## Signs (Failure Patterns)

### Beads SQLite corruption in Docker sandbox
The beads SQLite database repeatedly corrupts in this Docker sandbox environment.
The pre-commit hook (`bd sync --flush-only`) fails with "database disk image is malformed".
**Fix**: Set `no-db: true` in `.beads/config.yaml` and remove any `beads.db*` files.
This switches beads to JSONL-only mode, which avoids SQLite entirely while keeping
the pre-commit hook and all bd commands working. Do NOT remove the pre-commit hook.

### Beads assume-unchanged hides JSONL from git
`bd init` sets `assume-unchanged` on `.beads/issues.jsonl`, making `git add` silently
ignore changes. **Fix**: `git update-index --no-assume-unchanged .beads/issues.jsonl`

### Module-level Path.cwd() freezes at import time
Never use `Path.cwd()` or `Path.home()` in module-level constants if tests use
`monkeypatch.chdir()`. Wrap in a function for lazy evaluation.

### CI needs git user config for commits in tests
Integration tests that run `git commit` will fail on CI runners without user config.
Always set `user.email` and `user.name` in test setup before committing.

### Do not use `from __future__ import annotations`
This project targets Python 3.11+ and avoids `__future__` annotations because they
silently change annotation semantics (making all annotations strings). Use quoted
strings for forward references instead. Ruff rule FA100 is ignored to prevent
suggestions to add it back.

### Run `ruff format` before pushing
CI checks `ruff format --check` separately from `ruff check`. Lint passing does
not mean format passes. Run both before pushing.

