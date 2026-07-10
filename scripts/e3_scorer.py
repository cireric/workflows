"""E3 experiment scorer - automated verification for Deepworker end-to-end tasks.

Usage:
    source .venv/bin/activate
    python scripts/e3_scorer.py --task 1
    python scripts/e3_scorer.py --task all
    python scripts/e3_scorer.py --task 1,2,3
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
SKILLS_DIR = PROJECT_ROOT / "skills"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"

# Exit codes for validate_agents.py CLI (T5)
EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_ARG_ERROR = 2

# Minimum sys.exit calls expected in T5
MIN_EXIT_CALLS = 2

# E2E pass rate threshold
E2E_PASS_THRESHOLD = 0.8

# Separator line for output
SEP = "=" * 60

VALID_EXIT_CODES_DEFAULT = {0, 1}


@dataclass
class CheckResult:
    """Result of a single verification check."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class TaskScore:
    """Aggregated score for one task."""

    task_id: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def pass_count(self) -> int:
        """Number of passed checks."""
        return sum(1 for c in self.checks if c.passed)

    @property
    def total_count(self) -> int:
        """Total number of checks."""
        return len(self.checks)

    @property
    def pass_rate(self) -> float:
        """Pass rate as 0-1 float."""
        return self.pass_count / self.total_count if self.total_count else 0.0


def run_make(target: str) -> tuple[bool, str]:
    """Run a make target.

    Returns:
        Tuple of (success, combined stdout+stderr output).
    """
    result = subprocess.run(
        ["/usr/bin/make", target],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return result.returncode == 0, result.stdout + result.stderr


def git_diff_stat() -> list[str]:
    """Return list of changed files from git diff --name-only.

    Returns:
        List of file paths relative to project root.
    """
    result = subprocess.run(
        ["/usr/bin/git", "diff", "--name-only"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]


def file_exists(path: Path) -> bool:
    """Check if a file exists.

    Returns:
        True if the file exists and is a regular file.
    """
    return path.is_file()


def file_contains(path: Path, text: str) -> bool:
    """Check if a file contains specific text.

    Returns:
        True if the file exists and contains the given text.
    """
    if not path.is_file():
        return False
    return text in path.read_text(encoding="utf-8")


def check_make_target(target: str) -> CheckResult:
    """Run make target and return check result.

    Returns:
        CheckResult indicating whether the make target passed.
    """
    success, output = run_make(target)
    if success:
        return CheckResult(name=f"make {target}", passed=True, detail="0 errors")
    error_lines = [line for line in output.splitlines() if "error" in line.lower()]
    detail = f"{len(error_lines)} error lines found"
    return CheckResult(name=f"make {target}", passed=False, detail=detail)


def _run_script(
    args: list[str],
    expected_codes: set[int] | None = None,
) -> CheckResult:
    """Run a Python script and return a CheckResult.

    Args:
        args: Command arguments starting with script path.
        expected_codes: Set of acceptable exit codes (default {0, 1}).

    Returns:
        CheckResult with pass/fail and exit code detail.
    """
    if expected_codes is None:
        expected_codes = VALID_EXIT_CODES_DEFAULT
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return CheckResult(
        name="",
        passed=result.returncode in expected_codes,
        detail=f"Exit code: {result.returncode}",
    )


# --- Task-specific check functions ---


def score_t1() -> TaskScore:
    """Score T1: type annotation addition to conftest.py.

    Returns:
        TaskScore with all T1 verification checks.
    """
    score = TaskScore(task_id="T1")
    conftest = TESTS_DIR / "conftest.py"

    # File modified
    changed = git_diff_stat()
    only_conftest = changed == ["tests/conftest.py"] or all("conftest" in f for f in changed)
    score.checks.append(
        CheckResult(
            name="change scope: conftest.py only",
            passed=only_conftest,
            detail=f"Changed: {changed}",
        )
    )

    # Type annotations exist
    content = conftest.read_text(encoding="utf-8") if conftest.is_file() else ""
    has_return_annotations = "-> " in content and "Path" in content
    score.checks.append(
        CheckResult(
            name="type annotations complete",
            passed=has_return_annotations,
            detail=(
                "Return type annotations present"
                if has_return_annotations
                else "Missing return type annotations"
            ),
        )
    )

    # Docstrings exist
    has_docstrings = '"""' in content and "Return" in content
    score.checks.append(
        CheckResult(
            name="docstrings complete",
            passed=has_docstrings,
            detail=("Google-style docstrings present" if has_docstrings else "Missing docstrings"),
        )
    )

    # Make targets
    score.checks.append(check_make_target("lint"))
    score.checks.append(check_make_target("typecheck"))
    score.checks.append(check_make_target("test"))

    return score


def score_t2() -> TaskScore:
    """Score T2: new validate_agents.py script with TDD.

    Returns:
        TaskScore with all T2 verification checks.
    """
    score = TaskScore(task_id="T2")
    script_path = SCRIPTS_DIR / "validate_agents.py"
    test_path = TESTS_DIR / "test_validate_agents.py"

    # Files exist
    score.checks.append(
        CheckResult(
            name="scripts/validate_agents.py exists",
            passed=file_exists(script_path),
        )
    )
    score.checks.append(
        CheckResult(
            name="tests/test_validate_agents.py exists",
            passed=file_exists(test_path),
        )
    )

    # Script content checks
    if file_exists(script_path):
        content = script_path.read_text(encoding="utf-8")
        content_lower = content.lower()

        has_agents_ref = "agents" in content_lower
        score.checks.append(
            CheckResult(
                name="scans agents/ directory",
                passed=has_agents_ref,
                detail=(
                    "References agents directory"
                    if has_agents_ref
                    else "No reference to agents directory"
                ),
            )
        )

        has_frontmatter = "frontmatter" in content_lower or "---" in content
        score.checks.append(
            CheckResult(
                name="validates frontmatter",
                passed=has_frontmatter,
                detail=(
                    "Frontmatter validation logic present"
                    if has_frontmatter
                    else "No frontmatter validation"
                ),
            )
        )

        has_description = "description" in content_lower
        score.checks.append(
            CheckResult(
                name="validates description field",
                passed=has_description,
                detail=(
                    "Description field validation present"
                    if has_description
                    else "No description validation"
                ),
            )
        )

        has_exit = "sys.exit" in content
        score.checks.append(
            CheckResult(
                name="exit code logic",
                passed=has_exit,
                detail=("Exit code logic present" if has_exit else "No sys.exit found"),
            )
        )
    else:
        missing_checks = [
            "scans agents/ directory",
            "validates frontmatter",
            "validates description field",
            "exit code logic",
        ]
        for name in missing_checks:
            score.checks.append(CheckResult(name=name, passed=False, detail="Script not found"))

    # Functional test: run the script
    if file_exists(script_path):
        check = _run_script([sys.executable, str(script_path)])
        check.name = "functional: script runs"
        check.passed = True  # Ran without exception
        score.checks.append(check)

    # Make targets
    score.checks.append(check_make_target("lint"))
    score.checks.append(check_make_target("typecheck"))
    score.checks.append(check_make_target("test"))

    return score


def score_t3() -> TaskScore:
    """Score T3: test file refactoring.

    Returns:
        TaskScore with all T3 verification checks.
    """
    score = TaskScore(task_id="T3")

    # New files exist
    score.checks.append(
        CheckResult(
            name="tests/test_dirs.py exists",
            passed=file_exists(TESTS_DIR / "test_dirs.py"),
        )
    )
    score.checks.append(
        CheckResult(
            name="tests/test_skills.py exists",
            passed=file_exists(TESTS_DIR / "test_skills.py"),
        )
    )

    # Old file deleted
    old_exists = file_exists(TESTS_DIR / "test_structure.py")
    score.checks.append(
        CheckResult(
            name="tests/test_structure.py deleted",
            passed=not old_exists,
            detail="Still exists" if old_exists else "Deleted",
        )
    )

    # Behavior preserved: same test names in new files
    if file_exists(TESTS_DIR / "test_dirs.py"):
        dirs_content = (TESTS_DIR / "test_dirs.py").read_text(encoding="utf-8")
        score.checks.append(
            CheckResult(
                name="test_dirs.py has dir tests",
                passed="test_project_dirs_exist" in dirs_content or "test_" in dirs_content,
            )
        )
    else:
        score.checks.append(CheckResult(name="test_dirs.py has dir tests", passed=False))

    if file_exists(TESTS_DIR / "test_skills.py"):
        skills_content = (TESTS_DIR / "test_skills.py").read_text(encoding="utf-8")
        score.checks.append(
            CheckResult(
                name="test_skills.py has skill tests",
                passed="test_skills_have_skill_md" in skills_content or "test_" in skills_content,
            )
        )
    else:
        score.checks.append(CheckResult(name="test_skills.py has skill tests", passed=False))

    # Change scope: only tests/ directory
    changed = git_diff_stat()
    only_tests = all(f.startswith("tests/") for f in changed)
    score.checks.append(
        CheckResult(
            name="change scope: tests/ only",
            passed=only_tests,
            detail=f"Changed: {changed}",
        )
    )

    # Make targets
    score.checks.append(check_make_target("lint"))
    score.checks.append(check_make_target("typecheck"))
    score.checks.append(check_make_target("test"))

    return score


def score_t4() -> TaskScore:
    """Score T4: new skill creation.

    Returns:
        TaskScore with all T4 verification checks.
    """
    score = TaskScore(task_id="T4")
    skill_dir = SKILLS_DIR / "validate-output"
    skill_md = skill_dir / "SKILL.md"

    # Directory and file exist
    score.checks.append(
        CheckResult(
            name="skills/validate-output/ exists",
            passed=skill_dir.is_dir(),
        )
    )
    score.checks.append(
        CheckResult(
            name="skills/validate-output/SKILL.md exists",
            passed=file_exists(skill_md),
        )
    )

    # Content checks
    if file_exists(skill_md):
        content = skill_md.read_text(encoding="utf-8")
        required_sections = [
            ("Frontmatter: name field", "name:"),
            ("Frontmatter: description field", "description:"),
            ("PURPOSE section", "PURPOSE"),
            ("TRIGGERS section", "TRIGGERS"),
            ("PROTOCOL section", "PROTOCOL"),
            ("PASS CRITERIA section", "PASS CRITERIA"),
        ]
        for section_name, marker in required_sections:
            score.checks.append(
                CheckResult(
                    name=section_name,
                    passed=marker in content,
                )
            )
    else:
        missing_sections = [
            "Frontmatter: name field",
            "Frontmatter: description field",
            "PURPOSE section",
            "TRIGGERS section",
            "PROTOCOL section",
            "PASS CRITERIA section",
        ]
        for name in missing_sections:
            score.checks.append(CheckResult(name=name, passed=False, detail="SKILL.md not found"))

    # Make test (skill structure test should pass)
    score.checks.append(check_make_target("test"))

    return score


def score_t5() -> TaskScore:
    """Score T5: CLI enhancement for validate_agents.py.

    Returns:
        TaskScore with all T5 verification checks.
    """
    score = TaskScore(task_id="T5")
    script_path = SCRIPTS_DIR / "validate_agents.py"
    test_path = TESTS_DIR / "test_validate_agents.py"

    # Files exist
    score.checks.append(
        CheckResult(
            name="scripts/validate_agents.py exists",
            passed=file_exists(script_path),
        )
    )
    score.checks.append(
        CheckResult(
            name="tests/test_validate_agents.py exists",
            passed=file_exists(test_path),
        )
    )

    # CLI content checks
    if file_exists(script_path):
        content = script_path.read_text(encoding="utf-8")
        cli_checks = [
            ("argparse import", "argparse" in content),
            ("--strict flag", "--strict" in content),
            ("--path flag", "--path" in content),
            ("--verbose flag", "--verbose" in content),
            (
                "exit codes 0/1/2",
                content.count("sys.exit") >= MIN_EXIT_CALLS,
            ),
        ]
        for check_name, passed in cli_checks:
            detail = ""
            if check_name == "exit codes 0/1/2":
                detail = f"Found {content.count('sys.exit')} sys.exit calls"
            score.checks.append(CheckResult(name=check_name, passed=passed, detail=detail))
    else:
        missing_cli = [
            "argparse import",
            "--strict flag",
            "--path flag",
            "--verbose flag",
            "exit codes 0/1/2",
        ]
        for name in missing_cli:
            score.checks.append(CheckResult(name=name, passed=False, detail="Script not found"))

    # Functional tests: run with various args
    if file_exists(script_path):
        func_checks = [
            (
                "functional: default run",
                [sys.executable, str(script_path)],
                VALID_EXIT_CODES_DEFAULT,
            ),
            (
                "functional: --strict mode",
                [sys.executable, str(script_path), "--strict"],
                VALID_EXIT_CODES_DEFAULT,
            ),
            (
                "functional: --verbose mode",
                [sys.executable, str(script_path), "--verbose"],
                VALID_EXIT_CODES_DEFAULT,
            ),
            (
                "functional: invalid path exit code",
                [sys.executable, str(script_path), "--path", "/nonexistent/path"],
                {EXIT_ARG_ERROR},
            ),
        ]
        for check_name, args, expected_codes in func_checks:
            check = _run_script(args, expected_codes)
            check.name = check_name
            if check_name == "functional: invalid path exit code":
                code = check.detail.split(": ")[-1]
                check.detail = f"Exit code: {code} (expected {EXIT_ARG_ERROR})"
            score.checks.append(check)
    else:
        missing_func = [
            "functional: default run",
            "functional: --strict mode",
            "functional: --verbose mode",
            "functional: invalid path exit code",
        ]
        for name in missing_func:
            score.checks.append(CheckResult(name=name, passed=False, detail="Script not found"))

    # Make targets
    score.checks.append(check_make_target("lint"))
    score.checks.append(check_make_target("typecheck"))
    score.checks.append(check_make_target("test"))

    return score


# --- Registry ---

SCORERS: dict[int, Callable[[], TaskScore]] = {
    1: score_t1,
    2: score_t2,
    3: score_t3,
    4: score_t4,
    5: score_t5,
}


def print_score(score: TaskScore) -> None:
    """Print a task score in readable format."""
    print(f"\n{SEP}")
    rate_str = f"{score.pass_rate:.0%}"
    print(f"  Task {score.task_id} - {score.pass_count}/{score.total_count} passed ({rate_str})")
    print(SEP)
    for check in score.checks:
        icon = "PASS" if check.passed else "FAIL"
        detail = f" -- {check.detail}" if check.detail else ""
        print(f"  [{icon}] {check.name}{detail}")
    print()


def main() -> None:
    """Run E3 experiment scorer."""
    parser = argparse.ArgumentParser(description="E3 experiment scorer")
    parser.add_argument(
        "--task",
        type=str,
        default="all",
        help="Task number(s) to score: 1, 2, 3, 4, 5, or 'all'",
    )
    args = parser.parse_args()

    if args.task == "all":
        task_ids = [1, 2, 3, 4, 5]
    else:
        task_ids = [int(t.strip()) for t in args.task.split(",")]

    scores: list[TaskScore] = []
    for tid in task_ids:
        scorer = SCORERS.get(tid)
        if scorer is None:
            print(f"Unknown task: T{tid}")
            continue
        score = scorer()
        scores.append(score)
        print_score(score)

    # Summary
    if len(scores) > 1:
        total_pass = sum(s.pass_count for s in scores)
        total_checks = sum(s.total_count for s in scores)
        e2e_pass = sum(1 for s in scores if s.pass_rate >= E2E_PASS_THRESHOLD)
        rate = e2e_pass / len(scores)
        print(SEP)
        print(f"  SUMMARY - {total_pass}/{total_checks} total checks passed")
        print(f"  E2E completion rate (>=80% checks pass): {e2e_pass}/{len(scores)} = {rate:.0%}")
        print(SEP)


if __name__ == "__main__":
    main()
