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

Body composition tracking (Phase 10)
---------------------------------------------------------------------
If the ``Person`` passed to ``Simulator`` has ``body_fat_percent``
set, the simulator additionally tracks fat mass and lean mass
separately (populating ``SimulationState.fat_mass_kg`` /
``lean_mass_kg``), using ``body_composition_model_id`` to determine
what fraction of each day's mass change is fat vs. lean -- see
``metabosim.models.body_composition``. This also means the energy
balance calculation uses a *dynamically computed*, current-fat-mass-
dependent fraction (via
``metabosim.models.energy_balance.tissue_energy_density.TissueEnergyDensityModel``)
rather than that model's static 0.25 population-average default.

If ``body_fat_percent`` is not set, none of this activates and the
simulator behaves exactly as it did in Phase 9: ``fat_mass_kg`` /
``lean_mass_kg`` stay ``None`` throughout, and the energy balance
model's own static default fraction is used unchanged.

Adaptive thermogenesis (Phase 11)
---------------------------------------------------------------------
By default, this simulator's real per-day BMR recompute is the ONLY
source of weight-dependent expenditure change -- no additional
"metabolic adaptation" beyond that is modeled
(``adaptive_thermogenesis_model_id`` defaults to ``"none"``). Set it
to ``"threshold"`` or ``"proportional"`` to add a documented,
cited adjustment representing the *additional* expenditure suppression
(during loss) or increase (during gain) observed in the literature
beyond what mass change alone predicts -- see
``metabosim.models.adaptive_thermogenesis`` for the three-model
framework and why none of them is the default.
"""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field, model_validator

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.models.adaptive_thermogenesis.registry import (
    get_model as get_adaptive_thermogenesis_model,
)
from metabosim.models.body_composition.registry import (
    get_model as get_body_composition_model,
)
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

#: Default body composition model ID, used only when the subject's
#: ``body_fat_percent`` is known (see
#: ``metabosim.simulation.engine.Simulator`` and
#: ``metabosim.simulation.stepper.step`` for exactly when body
#: composition tracking activates).
DEFAULT_BODY_COMPOSITION_MODEL_ID: str = "forbes"

#: Default adaptive thermogenesis model ID. ``"none"`` is used --
#: not because the "no adaptation" model is believed most accurate,
#: but because the magnitude and dynamics of real adaptive
#: thermogenesis are less settled in the literature than every other
#: modeled component -- see
#: ``metabosim.models.adaptive_thermogenesis.base`` module docstring.
DEFAULT_ADAPTIVE_THERMOGENESIS_MODEL_ID: str = "none"


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
    body_composition_model_id:
        A key registered in ``metabosim.models.body_composition.registry``.
        Only consulted when the ``Person`` passed to ``Simulator`` has
        ``body_fat_percent`` set -- see
        ``metabosim.simulation.engine.Simulator`` for the exact
        activation rule. Defaults to ``"forbes"``. Validated eagerly at
        construction time.
    adaptive_thermogenesis_model_id:
        A key registered in
        ``metabosim.models.adaptive_thermogenesis.registry``. Defaults
        to ``"none"`` -- see module docstring above for why an
        explicit "no adaptation" default was chosen over one of the
        contested alternative magnitudes. Validated eagerly at
        construction time.
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
    body_composition_model_id: str = DEFAULT_BODY_COMPOSITION_MODEL_ID
    adaptive_thermogenesis_model_id: str = DEFAULT_ADAPTIVE_THERMOGENESIS_MODEL_ID
    start_date: date_type | None = None

    @model_validator(mode="after")
    def _check_adaptive_thermogenesis_model_is_registered(self) -> SimulationConfig:
        """Fail fast if ``adaptive_thermogenesis_model_id`` is not
        registered.

        Raises
        ------
        KeyError
            If ``adaptive_thermogenesis_model_id`` is not registered.
        """
        get_adaptive_thermogenesis_model(self.adaptive_thermogenesis_model_id)
        return self

    @model_validator(mode="after")
    def _check_body_composition_model_is_registered(self) -> SimulationConfig:
        """Fail fast if ``body_composition_model_id`` is not
        registered, even though it may never actually be used (only
        activates when a ``Person`` with ``body_fat_percent`` set is
        passed to ``Simulator``).

        Raises
        ------
        KeyError
            If ``body_composition_model_id`` is not registered.
        """
        get_body_composition_model(self.body_composition_model_id)
        return self

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
