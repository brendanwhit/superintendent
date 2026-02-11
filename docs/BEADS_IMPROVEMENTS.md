# Beads Task Improvements

Analysis and improvements for the worktree-v2 (superintendent) task tracking.

**Last Updated**: 2026-02-11

## Changes Applied

### Completed Fixes

1. **Parent-child relationships fixed** for all orphaned tasks:
   - Tasks 27-32 → Epic 26 (Task Source Abstraction)
   - Tasks 34-39 → Epic 33 (Execution Strategy)
   - Tasks 41-43 → Epic 40 (Multi-Agent Orchestration)
   - Tasks 10, 11, 23-25 → Epic 22 (V1 Feature Parity)

2. **Priorities aligned** with epic hierarchy:
   - Testing (ext) epic and children: P4 → P3
   - Documentation (cg0) children: P0 → P4

3. **Phase labels added** to all epics:
   - `phase:foundation` - rename task
   - `phase:sources` - task source abstraction
   - `phase:strategy` - execution strategy
   - `phase:orchestration` - multi-agent
   - `phase:polish` - testing, docs, V1 parity

## Current State Summary

| Category | Count |
|----------|-------|
| Total Open Issues | 38 |
| Ready to Work | 1 |
| Blocked by Rename | 37 |
| Open Epics | 6 |

## Remaining Issues

### 1. Bottleneck on Rename Task

**Problem**: `worktree-v2-45` (Rename to superintendent) blocks 27 other tasks.

**Impact**: No parallel development possible until rename completes.

**Recommendation**: Consider which tasks could actually proceed in parallel:
- Testing tasks (ext.1-4) test *existing* code - could run before rename
- Some documentation tasks describe concepts, not naming

**Decision Required**: Is the rename truly a hard blocker, or was this overly conservative?

### 2. Orphaned Tasks Without Epic Parents

**Problem**: 22 tasks have no parent-child relationship to their epics.

Tasks 27-45 use `blocked-by` to reference epics, but not `parent-child`. This means:
- `bd show <epic>` doesn't list them as children
- Epic completion status doesn't track them
- The task hierarchy is broken

**Affected Tasks**:
- worktree-v2-27 through 32 → should be children of Epic 26 (Task Sources)
- worktree-v2-34 through 39 → should be children of Epic 33 (Execution Strategy)
- worktree-v2-41 through 43 → should be children of Epic 40 (Multi-Agent)
- worktree-v2-44 → standalone (design doc)

**Fix Commands**:
```bash
# Task Source Abstraction children
bd update worktree-v2-27 --parent worktree-v2-26
bd update worktree-v2-28 --parent worktree-v2-26
bd update worktree-v2-29 --parent worktree-v2-26
bd update worktree-v2-31 --parent worktree-v2-26
bd update worktree-v2-32 --parent worktree-v2-26

# Execution Strategy children
bd update worktree-v2-34 --parent worktree-v2-33
bd update worktree-v2-35 --parent worktree-v2-33
bd update worktree-v2-36 --parent worktree-v2-33
bd update worktree-v2-37 --parent worktree-v2-33
bd update worktree-v2-38 --parent worktree-v2-33
bd update worktree-v2-39 --parent worktree-v2-33

# Multi-Agent Orchestration children
bd update worktree-v2-41 --parent worktree-v2-40
bd update worktree-v2-42 --parent worktree-v2-40
bd update worktree-v2-43 --parent worktree-v2-40
```

### 3. Inconsistent Priority Levels

**Problem**: Priorities don't reflect actual importance.

| Epic | Current Priority | Issue |
|------|-----------------|-------|
| cg0 (Documentation) | P4 (lowest) | Children are P0 |
| ext (Testing) | P4 (lowest) | Children are P0 |
| 22 (V1 Parity) | P2 | Reasonable |
| 26, 33 (Core) | P1 | Reasonable |
| 40 (Orchestration) | P2 | Reasonable |

**Fix**: Align child priorities with epic priorities:
```bash
# Documentation tasks should be P4 to match epic
bd update worktree-v2-cg0.1 -p 4
bd update worktree-v2-cg0.2 -p 4
bd update worktree-v2-cg0.3 -p 4

# Testing tasks should be P3 (more important than docs, less than features)
bd update worktree-v2-ext -p 3
bd update worktree-v2-ext.1 -p 3
bd update worktree-v2-ext.2 -p 3
bd update worktree-v2-ext.3 -p 3
bd update worktree-v2-ext.4 -p 3
```

### 4. Missing Phase Labels

**Problem**: No way to filter tasks by development phase.

**Recommendation**: Add labels for phases:

```bash
# Phase 1: Foundation (rename must happen first)
bd update worktree-v2-45 --add-label phase:foundation

# Phase 2: Task Sources
bd update worktree-v2-26 --add-label phase:sources
bd update worktree-v2-27 --add-label phase:sources
# ... (all 26 children)

# Phase 3: Execution Strategy
bd update worktree-v2-33 --add-label phase:strategy
# ... (all 33 children)

# Phase 4: Orchestration
bd update worktree-v2-40 --add-label phase:orchestration
# ... (all 40 children)

# Phase 5: Polish
bd update worktree-v2-22 --add-label phase:polish
bd update worktree-v2-cg0 --add-label phase:polish
bd update worktree-v2-ext --add-label phase:polish
```

### 5. V1 Feature Parity Tasks Not Visible

**Problem**: Epic 22 references tasks 10, 11, 23, 24, 25 but they weren't in my task listing.

**Check if these exist**:
```bash
bd show worktree-v2-10
bd show worktree-v2-11
bd show worktree-v2-23
bd show worktree-v2-24
bd show worktree-v2-25
```

## Recommended Epic Structure

```
worktree-v2-45: Rename to superintendent [P0] [CRITICAL BLOCKER]
│
├── worktree-v2-26: Task Source Abstraction [P1]
│   ├── worktree-v2-27: TaskSource protocol
│   ├── worktree-v2-28: BeadsSource adapter
│   ├── worktree-v2-29: MarkdownSource adapter
│   ├── worktree-v2-31: SingleTaskSource adapter
│   └── worktree-v2-32: Auto-detection logic
│
├── worktree-v2-33: Execution Strategy [P1]
│   ├── worktree-v2-34: ExecutionDecision models
│   ├── worktree-v2-35: RepoInfo analyzer
│   ├── worktree-v2-36: Mode decision logic
│   ├── worktree-v2-37: Target decision logic
│   ├── worktree-v2-38: Parallelism logic
│   └── worktree-v2-39: CLI --explain flag
│
├── worktree-v2-40: Multi-Agent Orchestration [P2]
│   ├── worktree-v2-41: Agent spawn/monitoring
│   ├── worktree-v2-42: Completion handling
│   └── worktree-v2-43: Progress reporting
│
├── worktree-v2-22: V1 Feature Parity [P2]
│   ├── worktree-v2-10: Resume by branch
│   ├── worktree-v2-11: Smart cleanup
│   ├── worktree-v2-23: Auto-create worktree
│   ├── worktree-v2-24: Auto-merge main
│   └── worktree-v2-25: ralph-token CLI
│
├── worktree-v2-ext: Testing [P3]
│   ├── worktree-v2-ext.1: Unit tests
│   ├── worktree-v2-ext.2: Integration tests
│   ├── worktree-v2-ext.3: E2E tests
│   └── worktree-v2-ext.4: Dry-run tests
│
├── worktree-v2-cg0: Documentation [P4]
│   ├── worktree-v2-cg0.1: CLAUDE.md
│   ├── worktree-v2-cg0.2: README
│   └── worktree-v2-cg0.3: Inline docs
│
└── worktree-v2-44: Architecture design doc [P1] (standalone)
```

## Task Description Template

Each task should follow this format:

```markdown
## Context
Why this task exists and how it fits in the larger picture.

## Implementation
What specifically needs to be built.

## Location
- Create: `path/to/new/file.py`
- Modify: `path/to/existing/file.py`

## Dependencies
- Requires: worktree-v2-XX (reason)
- Blocks: worktree-v2-YY (reason)

## Acceptance Criteria
- [ ] Specific, testable criterion
- [ ] Another criterion
- [ ] Tests pass: `uv run pytest tests/test_xxx.py`

## Notes
Any additional context, design decisions, or gotchas.
```

## Tasks Needing Description Improvements

### High Priority (Core Functionality)

| Task | Issue | Improvement Needed |
|------|-------|-------------------|
| 27 | Good | Add file location |
| 28 | Good | Add test expectations |
| 29 | Good | Add test expectations |
| 31 | Good | Add test expectations |
| 32 | Good | Add example output |

### Medium Priority (Strategy)

| Task | Issue | Improvement Needed |
|------|-------|-------------------|
| 34 | Good | Complete |
| 35 | Good | Complete |
| 36 | Good | Complete |
| 37 | Good | Complete |
| 38 | Good | Complete |
| 39 | Good | Complete |

### Lower Priority (Testing/Docs)

| Task | Issue | Improvement Needed |
|------|-------|-------------------|
| ext.1-4 | Detailed | Add specific test function names |
| cg0.1-3 | Reasonable | Add content outlines |

## Execution Plan

### Immediate (Do Now)
1. Fix parent-child relationships for tasks 27-43
2. Fix priority alignment (children match parents)
3. Add phase labels

### Before Starting Work
4. Review rename blocking - can any tasks proceed?
5. Verify V1 Parity tasks exist (10, 11, 23-25)

### Ongoing
6. Update task descriptions as work begins
7. Add context to close_reason when completing tasks

## Script to Apply Fixes

```bash
#!/bin/bash
# Run from worktree-v2 repo root

# Fix parent-child relationships
echo "Fixing parent-child relationships..."
bd update worktree-v2-27 --parent worktree-v2-26
bd update worktree-v2-28 --parent worktree-v2-26
bd update worktree-v2-29 --parent worktree-v2-26
bd update worktree-v2-31 --parent worktree-v2-26
bd update worktree-v2-32 --parent worktree-v2-26

bd update worktree-v2-34 --parent worktree-v2-33
bd update worktree-v2-35 --parent worktree-v2-33
bd update worktree-v2-36 --parent worktree-v2-33
bd update worktree-v2-37 --parent worktree-v2-33
bd update worktree-v2-38 --parent worktree-v2-33
bd update worktree-v2-39 --parent worktree-v2-33

bd update worktree-v2-41 --parent worktree-v2-40
bd update worktree-v2-42 --parent worktree-v2-40
bd update worktree-v2-43 --parent worktree-v2-40

# Fix priorities
echo "Aligning priorities..."
bd update worktree-v2-ext -p 3
bd update worktree-v2-ext.1 -p 3
bd update worktree-v2-ext.2 -p 3
bd update worktree-v2-ext.3 -p 3
bd update worktree-v2-ext.4 -p 3

bd update worktree-v2-cg0.1 -p 4
bd update worktree-v2-cg0.2 -p 4
bd update worktree-v2-cg0.3 -p 4

# Add phase labels
echo "Adding phase labels..."
bd update worktree-v2-45 --add-label phase:foundation
bd update worktree-v2-26 --add-label phase:sources
bd update worktree-v2-33 --add-label phase:strategy
bd update worktree-v2-40 --add-label phase:orchestration
bd update worktree-v2-22 --add-label phase:polish
bd update worktree-v2-ext --add-label phase:polish
bd update worktree-v2-cg0 --add-label phase:polish

echo "Done! Run 'bd sync' to save changes."
```
