"""Smoke test — verify project structure exists."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_project_dirs_exist(project_root: Path) -> None:
    """Core directories must exist."""
    for dirname in ("agents", "commands", "docs", "scripts", "skills"):
        assert (project_root / dirname).is_dir(), f"Missing directory: {dirname}"


def test_skills_have_skill_md(skills_dir: Path) -> None:
    """Each skill directory must contain a SKILL.md."""
    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir():
            assert (skill_path / "SKILL.md").is_file(), (
                f"Skill '{skill_path.name}' missing SKILL.md"
            )
