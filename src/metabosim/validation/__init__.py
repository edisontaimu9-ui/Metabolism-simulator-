"""
metabosim.validation
======================

Tools for comparing model output against published research (Phase 17).
Distinct from ``tests/unit`` in that these are tolerance-band
comparisons against empirical data, not exact-value regression tests.

  - ``metrics``   -- ``rmse``, ``mean_bias``, ``max_abs_error``.
  - ``reference`` -- ``ReferenceCurve`` (digitized published curves, with
    mandatory citation and extraction notes), ``load_curve``,
    ``compare_curve``, ``check_value``, ``ValidationResult``.
  - ``yoo2018``   -- ``run_yoo_2018_check``: a plausibility check against
    a published worked example. It rests on assumed inputs, so it is
    deliberately loose; read its module docstring before relying on it.

Only data digitized from real sources belongs in ``datasets/``; see the
README there. No digitized curve is bundled yet.
"""

from metabosim.validation.metrics import max_abs_error, mean_bias, rmse
from metabosim.validation.reference import (
    ReferenceCurve,
    ValidationResult,
    check_value,
    compare_curve,
    load_curve,
)
from metabosim.validation.yoo2018 import run_yoo_2018_check

__all__ = [
    "ReferenceCurve",
    "ValidationResult",
    "check_value",
    "compare_curve",
    "load_curve",
    "max_abs_error",
    "mean_bias",
    "rmse",
    "run_yoo_2018_check",
]
