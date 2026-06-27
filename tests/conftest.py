"""Shared pytest fixtures for workflows test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def skills_dir(project_root: Path) -> Path:
    """Return the skills directory."""
    return project_root / "skills"


@pytest.fixture
def agents_dir(project_root: Path) -> Path:
    """Return the agents directory."""
    return project_root / "agents"


@pytest.fixture
def scripts_dir(project_root: Path) -> Path:
    """Return the scripts directory."""
    return project_root / "scripts"
