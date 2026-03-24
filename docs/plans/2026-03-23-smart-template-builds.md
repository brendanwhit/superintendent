# Plan: Repo-Aware Template Builds

## Problem

The sandbox template Dockerfile is hardcoded (Dolt + beads CLI). When an agent starts in a sandbox with a Python repo that has heavy C dependencies (GDAL, pyfarmhash, weasyprint, lxml, etc.), `pip install` compiles them from source during the agent's session. This wastes 10-30 minutes of agent time and frequently fails due to missing system libraries (e.g., `libgdal-dev`, `libfarmhash-dev`).

The template build step already runs *after* `create_worktree`, so the repo files are available for inspection. We should use them.

## Approach

Extend `_handle_prepare_template` to inspect the worktree and generate a repo-tailored Dockerfile. The key insight: we don't need to solve the general case. A curated mapping of "known heavy packages → system deps" handles the 80% case. Unknown packages just get installed at runtime as they do today.

## Changes

### 1. Add `detect_system_deps()` to `repo_info.py`

New function that scans dependency files and returns system packages to pre-install.

```python
# Known Python packages that need system libraries
PYTHON_SYSTEM_DEPS: dict[str, list[str]] = {
    "gdal": ["libgdal-dev", "gdal-bin"],
    "fiona": ["libgdal-dev", "gdal-bin"],
    "rasterio": ["libgdal-dev", "gdal-bin"],
    "pyfarmhash": ["libfarmhash-dev"],
    "weasyprint": ["libpango-1.0-0", "libpangocairo-1.0-0", "libgdk-pixbuf2.0-0"],
    "lxml": ["libxml2-dev", "libxslt1-dev"],
    "psycopg2": ["libpq-dev"],
    "pillow": ["libjpeg-dev", "libpng-dev", "zlib1g-dev"],
    "cryptography": ["libssl-dev", "libffi-dev"],
    "numpy": ["gfortran"],  # for building from source
    "scipy": ["gfortran", "libopenblas-dev"],
    "h5py": ["libhdf5-dev"],
    "pygraphviz": ["graphviz", "libgraphviz-dev"],
    "mysqlclient": ["libmysqlclient-dev"],
    "cffi": ["libffi-dev"],
}

def detect_system_deps(repo: Path) -> list[str]:
    """Scan repo dependency files and return apt packages to pre-install."""
```

**Parsing targets:**
- `pyproject.toml` — `[project.dependencies]` and `[project.optional-dependencies]`
- `requirements.txt` / `requirements/*.txt` — one package per line
- `setup.py` / `setup.cfg` — `install_requires` (best-effort regex)

**Returns:** Deduplicated, sorted list of apt package names.

### 2. Add `detect_package_manager()` to `repo_info.py`

```python
def detect_package_manager(repo: Path) -> str | None:
    """Detect which Python package manager the repo uses."""
```

Returns `"uv"`, `"pip"`, `"pipenv"`, or `None`. Detection:
- `uv.lock` → `"uv"`
- `Pipfile.lock` → `"pipenv"`
- `pyproject.toml` with `[tool.poetry]` → `"poetry"` (future)
- `requirements.txt` → `"pip"`

### 3. Update `_handle_prepare_template` in `step_handler.py`

Pass the worktree path (from `create_worktree` step output) to the new detection functions. Build a Dockerfile that includes system deps:

```python
def _handle_prepare_template(self, step: WorkflowStep) -> StepResult:
    wt_output = self._context.step_outputs.get("create_worktree")
    worktree_path = Path(wt_output["worktree_path"]) if wt_output else None

    # Detect system dependencies from repo
    system_deps: list[str] = []
    if worktree_path and worktree_path.is_dir():
        system_deps = detect_system_deps(worktree_path)

    # Build Dockerfile
    lines = [
        "FROM dolthub/dolt:latest AS dolt-binary",
        f"FROM {SANDBOX_BASE_IMAGE}",
        "COPY --from=dolt-binary /usr/local/bin/dolt /usr/local/bin/dolt",
    ]
    if system_deps:
        deps_str = " ".join(system_deps)
        lines.append(
            f"RUN apt-get update && apt-get install -y --no-install-recommends {deps_str} "
            "&& rm -rf /var/lib/apt/lists/*"
        )
    lines.append("RUN npm install -g @beads/bd")

    dockerfile = "\n".join(lines) + "\n"
    tag = "supt-sandbox:" + hashlib.sha256(dockerfile.encode()).hexdigest()[:12]
    # ... rest unchanged
```

The hash-based tag ensures different repos get different templates, and identical deps reuse cached images.

### 4. Add `RepoInfo.system_deps` field

Extend the existing `RepoInfo` dataclass:

```python
@dataclass
class RepoInfo:
    has_dockerfile: bool
    has_devcontainer: bool
    has_env_file: bool
    needs_auth: bool
    languages: list[str] = field(default_factory=list)
    system_deps: list[str] = field(default_factory=list)
    package_manager: str | None = None
    estimated_complexity: str = "simple"
```

Update `from_path()` to call the new detection functions. This makes the info available to the strategy layer too if needed later.

### 5. Pass worktree path through planner

Update the `prepare_template` step in the planner to not depend on step output at plan time — it already depends on `create_worktree` and the step handler reads the output at execution time. No planner changes needed.

### 6. Tests

**File:** `tests/test_repo_info.py`
- `test_detect_system_deps_from_pyproject_toml` — create tmp dir with pyproject.toml containing `gdal`, verify `libgdal-dev` in output
- `test_detect_system_deps_from_requirements_txt` — same with requirements.txt
- `test_detect_system_deps_empty_for_no_heavy_deps` — repo with only `requests`, `click`
- `test_detect_system_deps_deduplicates` — `gdal` and `fiona` both need `libgdal-dev`, only listed once
- `test_detect_package_manager_uv` — repo with `uv.lock`
- `test_detect_package_manager_pip` — repo with only `requirements.txt`
- `test_detect_package_manager_none` — repo with no Python files

**File:** `tests/test_step_handler.py` (or inline in existing test file)
- `test_prepare_template_with_system_deps` — mock worktree with pyproject.toml, verify Dockerfile contains `apt-get install`
- `test_prepare_template_without_system_deps` — verify Dockerfile unchanged when no heavy deps
- `test_prepare_template_tag_changes_with_deps` — verify hash changes when deps change

## Files Modified

- `src/superintendent/orchestrator/repo_info.py` — `detect_system_deps()`, `detect_package_manager()`, extended `RepoInfo`
- `src/superintendent/orchestrator/step_handler.py` — updated `_handle_prepare_template()`
- `tests/test_repo_info.py` — new detection function tests
- `tests/test_step_handler.py` or `tests/test_dry_run.py` — template step tests

## Out of Scope

- **Pre-installing Python packages in the template**: Too slow for template builds, too hard to version-match. Let `pip install` handle it at runtime.
- **Node.js system deps**: Less common; `npm install` rarely needs system packages.
- **Custom Dockerfile from repo**: If the repo has its own Dockerfile/devcontainer, that's a separate feature (use the repo's own image).
- **Package manager installation in template**: `uv`, `pip`, `poetry` are already available in the base image or trivially installable by the agent.

## Verification

```bash
uv run pytest tests/test_repo_info.py tests/test_dry_run.py -v
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Manual:
```bash
# Test with a repo that has heavy deps
superintendent run autonomous sandbox --repo /path/to/gdal-project --task "test" --dry-run
# Verify: Dockerfile in dry-run output includes apt-get install libgdal-dev
```
