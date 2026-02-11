# Superintendent Task Overview

Quick reference for the current project state.

## Critical Path

```
worktree-v2-45: Rename to superintendent [P0] [READY] ← START HERE
    │
    ├─→ Epic 26: Task Source Abstraction [P1]
    │   └─→ Epic 33: Execution Strategy [P1]
    │       └─→ Epic 40: Multi-Agent Orchestration [P2]
    │
    ├─→ Epic 22: V1 Feature Parity [P2]
    │
    ├─→ Epic ext: Testing [P3]
    │
    └─→ Epic cg0: Documentation [P4]
```

## Epics by Phase

### Phase: Foundation
| Epic | Title | Priority | Children |
|------|-------|----------|----------|
| 45 | Rename to superintendent | P0 | - |

### Phase: Sources
| Epic | Title | Priority | Children |
|------|-------|----------|----------|
| 26 | Task Source Abstraction | P1 | 27, 28, 29, 31, 32 |

### Phase: Strategy
| Epic | Title | Priority | Children |
|------|-------|----------|----------|
| 33 | Execution Strategy | P1 | 34, 35, 36, 37, 38, 39 |

### Phase: Orchestration
| Epic | Title | Priority | Children |
|------|-------|----------|----------|
| 40 | Multi-Agent Orchestration | P2 | 41, 42, 43 |

### Phase: Polish
| Epic | Title | Priority | Children |
|------|-------|----------|----------|
| 22 | V1 Feature Parity | P2 | 10, 11, 23, 24, 25 |
| ext | Testing | P3 | ext.1, ext.2, ext.3, ext.4 |
| cg0 | Documentation | P4 | cg0.1, cg0.2, cg0.3 |

## Quick Commands

```bash
# What can I work on?
bd ready

# Show epic with children
bd show worktree-v2-26

# Filter by phase
bd list --label phase:sources

# Start working on a task
bd update <id> --claim

# Complete a task
bd close <id> "what was done"

# Session end checklist
git status && git add . && bd sync && git commit -m "..." && git push
```

## Dependency Rules

1. **Rename (45) blocks everything** - Complete this first
2. **Sources (26) before Strategy (33)** - Need task abstraction for strategy
3. **Strategy (33) before Orchestration (40)** - Need decisions before spawning
4. **Core features before Polish** - Testing and docs come after functionality

## File Locations

After rename, code will be at:
- `src/superintendent/` - Main package
- `src/superintendent/orchestrator/` - Planner, Executor, Strategy
- `src/superintendent/backends/` - Docker, Git, Terminal, Auth
- `src/superintendent/sources/` - Beads, Markdown, SingleTask adapters
- `tests/` - All test files
