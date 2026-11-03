"""
metabosim.validation.reference
=================================

Data structures and comparison functions for checking simulation output
against published reference data.

Two kinds of reference are supported:

  - ``ReferenceCurve``: a digitized weight-versus-day curve from a
    publication, loaded from a JSON file in ``validation/datasets/``.
    Every dataset must carry its citation and a description of how its
    values were extracted, so a reader can judge its reliability.
  - A single expected value with a tolerance (see
    ``metabosim.validation.yoo2018``), compared with ``check_value``.

No dataset is bundled that was not digitized from a real source. See
``validation/datasets/README.md`` for how to add one.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from metabosim.domain.simulation_state import SimulationState
from metabosim.validation.metrics import max_abs_error, mean_bias, rmse


class ReferenceCurve(BaseModel):
    """A digitized published weight trajectory.

    Attributes
    ----------
    id:
        Short identifier, e.g. ``"keys_1950_minnesota"``.
    description:
        What the curve shows and under which conditions.
    citation:
        Full citation of the source.
    extraction_note:
        How the values were obtained (table copied, figure digitized
        with a named tool, and so on), including known uncertainty.
    days:
        Day indices (0 = start), strictly increasing.
    weight_kg:
        Published weight at each day.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    citation: str = Field(..., min_length=1)
    extraction_note: str = Field(..., min_length=1)
    days: list[int] = Field(..., min_length=1)
    weight_kg: list[float] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _check_shape(self) -> ReferenceCurve:
        if len(self.days) != len(self.weight_kg):
            raise ValueError("days and weight_kg must have the same length.")
        if any(d < 0 for d in self.days):
            raise ValueError("days must be non-negative.")
        if any(b <= a for a, b in zip(self.days, self.days[1:], strict=False)):
            raise ValueError("days must be strictly increasing.")
        return self


class ValidationResult(BaseModel):
    """Outcome of one validation check.

    ``passed`` is ``True`` when the error measure is within
    ``tolerance``. For a curve check the measure is RMSE (kg); for a
    value check it is the absolute difference.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    passed: bool
    tolerance: float
    unit: str
    detail: str
    rmse: float | None = None
    mean_bias: float | None = None
    max_abs_error: float | None = None
    expected: float | None = None
    observed: float | None = None


def load_curve(path: str | Path) -> ReferenceCurve:
    """Load a ``ReferenceCurve`` from a JSON file."""
    return ReferenceCurve.model_validate(
        json.loads(Path(path).read_text(encoding="utf-8"))
    )


def compare_curve(
    states: list[SimulationState],
    curve: ReferenceCurve,
    tolerance_rmse_kg: float,
) -> ValidationResult:
    """Compare simulated weight with a reference curve.

    The simulation is sampled at the curve's day indices. Passes when
    RMSE is at most ``tolerance_rmse_kg``.

    Raises
    ------
    ValueError
        If ``tolerance_rmse_kg`` is not positive, or the simulation is
        shorter than the curve's last day.
    """
    if tolerance_rmse_kg <= 0:
        raise ValueError("tolerance_rmse_kg must be positive.")
    last_day = curve.days[-1]
    if last_day > len(states) - 1:
        raise ValueError(
            f"Reference curve extends to day {last_day} but the simulation "
            f"only reaches day {len(states) - 1}."
        )
    simulated = [states[d].weight_kg for d in curve.days]
    error = rmse(simulated, curve.weight_kg)
    return ValidationResult(
        name=curve.id,
        passed=error <= tolerance_rmse_kg,
        tolerance=tolerance_rmse_kg,
        unit="kg RMSE",
        detail=f"Compared {len(curve.days)} points against {curve.citation}",
        rmse=error,
        mean_bias=mean_bias(simulated, curve.weight_kg),
        max_abs_error=max_abs_error(simulated, curve.weight_kg),
    )


def check_value(
    name: str,
    observed: float,
    expected: float,
    tolerance: float,
    unit: str,
    detail: str,
) -> ValidationResult:
    """Compare one observed value with an expected value.

    Passes when ``abs(observed - expected) <= tolerance``.
    """
    if tolerance <= 0:
        raise ValueError("tolerance must be positive.")
    return ValidationResult(
        name=name,
        passed=abs(observed - expected) <= tolerance,
        tolerance=tolerance,
        unit=unit,
        detail=detail,
        expected=expected,
        observed=observed,
    )
