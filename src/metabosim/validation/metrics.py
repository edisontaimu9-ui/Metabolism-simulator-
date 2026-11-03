"""
metabosim.validation.metrics
===============================

Plain error metrics for comparing simulated values against reference
values. No scientific modeling; pure arithmetic.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def _check(simulated: Sequence[float], reference: Sequence[float]) -> None:
    if len(simulated) != len(reference):
        raise ValueError(
            f"simulated ({len(simulated)}) and reference ({len(reference)}) "
            "must have the same length."
        )
    if not simulated:
        raise ValueError("At least one value pair is required.")


def mean_bias(simulated: Sequence[float], reference: Sequence[float]) -> float:
    """Mean of ``simulated - reference``. Positive means the simulation
    runs higher than the reference on average."""
    _check(simulated, reference)
    return sum(s - r for s, r in zip(simulated, reference, strict=True)) / len(
        simulated
    )


def rmse(simulated: Sequence[float], reference: Sequence[float]) -> float:
    """Root mean squared error."""
    _check(simulated, reference)
    return math.sqrt(
        sum((s - r) ** 2 for s, r in zip(simulated, reference, strict=True))
        / len(simulated)
    )


def max_abs_error(simulated: Sequence[float], reference: Sequence[float]) -> float:
    """Largest absolute difference at any point."""
    _check(simulated, reference)
    return max(abs(s - r) for s, r in zip(simulated, reference, strict=True))
