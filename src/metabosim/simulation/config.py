"""
metabosim.simulation.config
==============================

Declarative configuration for a day-by-day body weight simulation:
which model strategies to use, how many days to run, and (via
``DailyPlan``) what the subject eats and does each simulated day.

Why this couldn't be built until now
---------------------------------------------------------------------
``docs/phase_notes/phase_03.md`` deliberately deferred building this
object: a simulation config needs to reference concrete model
registry string IDs (``"mifflin_st_jeor"``, ``"tissue_energy_density"``,
etc.), none of which existed until Phases 4-8 built the relevant
registries. This module is that deferred piece, now buildable.

Why there is no ``activity_model_id`` option
---------------------------------------------------------------------
This simulator always drives Activity Energy Expenditure from a
per-day logged activity list (``DailyPlan.activity_entries``), via the
MET-based model (``metabosim.models.activity.met_based``). A
day-by-day activity log is exactly the input a MET-based model needs,
and exactly the input a PAL-ratio-based model
(``metabosim.models.activity.iom_pal.IOMPALActivityModel``) does not
use -- and PAL-ratio-based models are explicitly documented as unsafe
to combine with the real per-day BMR recompute this simulator performs
(see ``metabosim.models.activity.base``). Rather than expose an option
that could silently be misused, activity modeling is fixed to the
MET-based strategy. **``Person.activity_level`` is therefore NOT
consulted anywhere in this simulator** -- supply an empty
``activity_entries`` list for a day with no logged activity (net
Activity Energy Expenditure of zero for that day), not a particular
``ActivityLevel`` value.
"""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field, model_validator

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.models.energy_balance.registry import (
    get_model as get_energy_balance_model,
)
from metabosim.models.tdee.calculator import DEFAULT_BMR_MODEL_ID, DEFAULT_TEF_MODEL_ID

#: Default energy balance model ID. ``"tissue_energy_density"`` is
#: used (NOT ``"dynamic_quasi_exponential"``) specifically because this
#: simulator recomputes real BMR/TDEE at each day's updated weight,
#: which already supplies weight-dependent expenditure feedback from
#: actual physiology -- see ``metabosim.models.energy_balance.base``.
DEFAULT_ENERGY_BALANCE_MODEL_ID: str = "tissue_energy_density"


class DailyPlan(BaseModel):
    """One simulated day's diet and logged physical activity.

    Attributes
    ----------
    macros:
        The macronutrient composition of the day's food intake. Total
        energy intake for the day is ``macros.energy_kcal``.
    activity_entries:
        The day's logged activities (see
        ``metabosim.models.activity.met_based.ActivityEntry``). An
        empty list represents a day with no logged activity beyond
        BMR (net Activity Energy Expenditure of zero for that day).
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    macros: MacronutrientGrams
    activity_entries: list[ActivityEntry] = Field(default_factory=list)


class SimulationConfig(BaseModel):
    """Configuration for a ``metabosim.simulation.engine.Simulator`` run.

    Attributes
    ----------
    days:
        Number of days to simulate. Must be >= 1. The simulation
        produces ``days + 1`` states: an initial state (day 0, at the
        subject's starting weight) plus one state per simulated day.
    bmr_model_id:
        A key registered in ``metabosim.models.bmr.registry``,
        recomputed fresh each simulated day at that day's current
        weight. Defaults to ``"mifflin_st_jeor"``.
    tef_model_id:
        A key registered in ``metabosim.models.tef.registry``.
        Defaults to ``"macronutrient_specific"``.
    energy_balance_model_id:
        A key registered in ``metabosim.models.energy_balance.registry``.
        Must resolve to a model with
        ``includes_weight_dependent_feedback = False`` -- see module
        docstring and ``metabosim.models.energy_balance.base`` for why.
        Validated eagerly at construction time (fails fast rather than
        only when the simulation is run).
    start_date:
        Optional real calendar date for day 0. If provided, every
        produced ``SimulationState.date`` is populated; if omitted,
        all dates are left ``None``.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    days: int = Field(..., ge=1)
    bmr_model_id: str = DEFAULT_BMR_MODEL_ID
    tef_model_id: str = DEFAULT_TEF_MODEL_ID
    energy_balance_model_id: str = DEFAULT_ENERGY_BALANCE_MODEL_ID
    start_date: date_type | None = None

    @model_validator(mode="after")
    def _check_energy_balance_model_is_feedback_free(self) -> SimulationConfig:
        """Fail fast if ``energy_balance_model_id`` would double-count
        weight-dependent expenditure feedback against this
        simulator's own real per-day BMR recompute.

        Raises
        ------
        KeyError
            If ``energy_balance_model_id`` is not registered.
        ValueError
            If the resolved model has
            ``includes_weight_dependent_feedback = True``.
        """
        model = get_energy_balance_model(self.energy_balance_model_id)
        if model.includes_weight_dependent_feedback:
            raise ValueError(
                f"energy_balance_model_id={self.energy_balance_model_id!r} "
                f"resolves to {model.name!r}, which already implicitly "
                "includes weight-dependent expenditure feedback (its "
                "includes_weight_dependent_feedback attribute is True). "
                "This simulator recomputes real BMR/TDEE at each day's "
                "updated weight, which already supplies that feedback "
                "from actual physiology -- combining both would "
                "double-count it. Use a model with "
                "includes_weight_dependent_feedback = False instead, "
                "e.g. the default 'tissue_energy_density'."
            )
        return self
