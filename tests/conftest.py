"""Configure test path so superintendent packages are importable."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src/ to path so `from superintendent.orchestrator.models import ...` works
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@pytest.fixture(autouse=True)
def _no_spawn_terminal():
    """Prevent tests from opening real terminal windows."""
    with patch(
        "superintendent.orchestrator.step_handler._spawn_terminal",
        return_value=True,
    ):
        yield
