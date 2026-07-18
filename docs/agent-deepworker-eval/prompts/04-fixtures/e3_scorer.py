"""E3 evaluation scorer for multi-dimensional quality assessment."""

from __future__ import annotations

import math


def compute_dimension_score(ratings: list[float], weight: float = 1.0) -> float:
    """Compute weighted average score for a single evaluation dimension.

    Args:
        ratings: List of individual rating values (0.0-1.0).
        weight: Dimension weight for final score computation.

    Returns:
        Weighted average score, or 0.0 if ratings is empty.
    """
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings) * weight


def compute_overall_score(
    dimension_scores: dict[str, list[float]],
    weights: dict[str, float] | None = None,
) -> float:
    """Compute overall E3 score across all dimensions.

    Args:
        dimension_scores: Mapping of dimension name to list of ratings.
        weights: Optional mapping of dimension name to weight.
            Defaults to equal weight for all dimensions.

    Returns:
        Overall weighted score (0.0-1.0).
    """
    if not dimension_scores:
        return 0.0
    if weights is None:
        weights = dict.fromkeys(dimension_scores, 1.0)
    total_weight = sum(weights.get(k, 1.0) for k in dimension_scores)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(
        compute_dimension_score(v, weights.get(k, 1.0)) for k, v in dimension_scores.items()
    )
    return weighted_sum / total_weight


def grade_score(score: float) -> str:
    """Convert numeric score to letter grade.

    Args:
        score: Numeric score (0.0-1.0).

    Returns:
        Letter grade: A (>=0.9), B (>=0.8), C (>=0.7), D (>=0.6), F (<0.6).
    """
    if score >= 0.9:
        return "A"
    if score >= 0.8:
        return "B"
    if score >= 0.7:
        return "C"
    if score >= 0.6:
        return "D"
    return "F"


def compute_statistics(scores: list[float]) -> dict[str, float]:
    """Compute basic statistics for a list of scores.

    Args:
        scores: List of numeric scores.

    Returns:
        Dict with mean, std_dev, min, max, and count.
    """
    if not scores:
        return {"mean": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0, "count": 0.0}
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std_dev = math.sqrt(variance)
    return {
        "mean": mean,
        "std_dev": std_dev,
        "min": min(scores),
        "max": max(scores),
        "count": float(len(scores)),
    }


def format_report(
    dimension_scores: dict[str, list[float]],
    weights: dict[str, float] | None = None,
) -> str:
    """Generate a text report of E3 evaluation results.

    Args:
        dimension_scores: Mapping of dimension name to list of ratings.
        weights: Optional mapping of dimension name to weight.

    Returns:
        Formatted text report with per-dimension and overall results.
    """
    if weights is None:
        weights = dict.fromkeys(dimension_scores, 1.0)
    lines: list[str] = ["E3 Evaluation Report", "=" * 40]
    for dim, scores in dimension_scores.items():
        stats = compute_statistics(scores)
        dim_score = compute_dimension_score(scores, weights.get(dim, 1.0))
        grade = grade_score(dim_score / weights.get(dim, 1.0) if weights.get(dim, 1.0) > 0 else 0.0)
        lines.append(f"\n{dim}:")
        lines.append(f"  Score: {dim_score:.3f} (Grade: {grade})")
        lines.append(f"  Mean: {stats['mean']:.3f}, StdDev: {stats['std_dev']:.3f}")
        lines.append(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        lines.append(f"  Samples: {int(stats['count'])}")
    overall = compute_overall_score(dimension_scores, weights)
    lines.append(f"\n{'=' * 40}")
    lines.append(f"Overall Score: {overall:.3f} (Grade: {grade_score(overall)})")
    return "\n".join(lines)
