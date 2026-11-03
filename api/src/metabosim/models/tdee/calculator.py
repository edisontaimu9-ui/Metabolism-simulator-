"""
metabosim.models.tdee.calculator
====================================

The actual "TDEE engine" entry point: composes a chosen BMR model
(``metabosim.models.bmr``) with a chosen TDEE model
(``metabosim.models.tdee``) to go from a ``Person`` straight to a
fully-explained TDEE result, without the caller needing to touch
either registry directly.

This is deliberately a thin composition layer -- it contains no
scientific logic of its own, only wiring -- so that Phase 4's BMR
equations and Phase 5's TDEE strategies remain independently testable
and swappable, per the Strategy-pattern architecture in
``docs/architecture.md``.

Accepting a pre-built BMR model (Phase 14)
---------------------------------------------------------------------
``bmr_model_id`` on both functions in this module accepts either a
registry string ID (as in every prior phase) or an already-constructed
``BMRModel`` instance. This is what lets a
``metabosim.models.disease.DiseaseModifiedBMRModel`` -- which cannot
be described by a simple string ID, since it wraps a base model with
runtime-constructed disease modifiers -- be used anywhere a plain
equation-based model could be, with no change to any existing
string-based call site (they continue to work identically).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.person import Person
from metabosim.models.activity.registry import get_model as get_activity_model
from metabosim.models.bmr.base import BMRModel
from metabosim.models.bmr.registry import get_model as get_bmr_model
from metabosim.models.tdee.registry import get_model as get_tdee_model
from metabosim.models.tef.registry import get_model as get_tef_model

#: Default BMR model ID used by ``calculate_tdee`` when the caller
#: doesn't specify one. Mifflin-St Jeor is chosen as the default
#: because it is the equation most consistently found, across modern
#: validation studies, to have the smallest average bias against
#: measured RMR in healthy non-obese adults (the population most
#: simulations will initially target) -- see
#: ``docs/model_references.md``.
DEFAULT_BMR_MODEL_ID: str = "mifflin_st_jeor"

#: Default TDEE model ID. As of Phase 5, this is the only registered
#: strategy; see ``metabosim.models.tdee.pal_multiplier``.
DEFAULT_TDEE_MODEL_ID: str = "pal_multiplier"

#: Default Activity model ID used by ``calculate_tdee_from_components``.
#: MET-based is the default (rather than IOM PAL) specifically because
#: it is the only strategy safe to combine with a separately-computed
#: TEF figure -- see ``metabosim.models.activity.base``.
DEFAULT_ACTIVITY_MODEL_ID: str = "met_based"

#: Default TEF model ID used by ``calculate_tdee_from_components``.
DEFAULT_TEF_MODEL_ID: str = "macronutrient_specific"

#: The ``bmr_model_id`` value stored on result objects when the caller
#: passed a pre-built ``BMRModel`` instance rather than a registry
#: string ID (Phase 14) -- there is no ID to report in that case.
CUSTOM_BMR_MODEL_ID: str = "custom"


def _resolve_bmr_model(bmr_model: str | BMRModel) -> tuple[BMRModel, str]:
    """Resolve ``bmr_model`` (a registry string ID or a pre-built
    ``BMRModel`` instance) to ``(model_instance, id_for_reporting)``.

    See module docstring, "Accepting a pre-built BMR model."
    """
    if isinstance(bmr_model, str):
        return get_bmr_model(bmr_model), bmr_model
    return bmr_model, CUSTOM_BMR_MODEL_ID


class TDEEResult(BaseModel):
    """The fully-explained output of :func:`calculate_tdee`.

    Carrying both the final TDEE figure *and* the intermediate BMR
    figure plus which named strategies produced them means a report
    (Phase 16) can show "BMR: 1780 kcal (Mifflin-St Jeor) x 1.55
    (Moderate activity) = TDEE: 2759 kcal" rather than only the final
    number -- consistent with this project's goal of being a
    transparent scientific instrument, not just a calculator that
    outputs a single opaque figure.
    """

    model_config = ConfigDict(frozen=True)

    bmr_kcal: float
    tdee_kcal: float
    bmr_model_id: str
    bmr_model_name: str
    tdee_model_id: str
    tdee_model_name: str


def calculate_tdee(
    person: Person,
    bmr_model_id: str | BMRModel = DEFAULT_BMR_MODEL_ID,
    tdee_model_id: str = DEFAULT_TDEE_MODEL_ID,
) -> TDEEResult:
    """Calculate Total Daily Energy Expenditure for ``person``.

    This is the primary public entry point of the TDEE engine: it
    looks up the requested BMR model, computes BMR, looks up the
    requested TDEE model, scales BMR to TDEE, and returns both figures
    together with the names of the strategies used.

    Parameters
    ----------
    person:
        The subject to calculate for.
    bmr_model_id:
        A key registered in ``metabosim.models.bmr.registry``, e.g.
        ``"mifflin_st_jeor"``, ``"harris_benedict"``,
        ``"katch_mcardle"``, ``"cunningham"``, ``"elia_organ_based"``
        -- or a pre-built ``BMRModel`` instance (e.g. a
        ``metabosim.models.disease.DiseaseModifiedBMRModel``; Phase
        14). Note that the lean-mass-based equations require
        ``person.body_fat_percent`` to be set; see
        ``metabosim.models.bmr`` for details.
    tdee_model_id:
        A key registered in ``metabosim.models.tdee.registry``, e.g.
        ``"pal_multiplier"``.

    Returns
    -------
    TDEEResult
        The BMR figure, the TDEE figure, and the identifying names of
        both strategies used. ``bmr_model_id`` on the result is
        ``"custom"`` when a pre-built ``BMRModel`` instance was
        passed in, since there is no registry ID to report.

    Raises
    ------
    KeyError
        If either model ID is not registered.
    ValueError
        If the chosen BMR model requires data the ``person`` doesn't
        have (e.g. ``body_fat_percent`` for Katch-McArdle).

    Examples
    --------
    >>> from metabosim.domain import ActivityLevel, Person, Sex
    >>> person = Person(
    ...     sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80,
    ...     activity_level=ActivityLevel.MODERATE,
    ... )
    >>> result = calculate_tdee(person)
    >>> round(result.bmr_kcal, 2)
    1780.0
    >>> round(result.tdee_kcal, 2)
    2759.0
    """
    bmr_model, resolved_bmr_model_id = _resolve_bmr_model(bmr_model_id)
    bmr_kcal = bmr_model.calculate(person)

    tdee_model = get_tdee_model(tdee_model_id)
    tdee_kcal = tdee_model.calculate(person, bmr_kcal)

    return TDEEResult(
        bmr_kcal=bmr_kcal,
        tdee_kcal=tdee_kcal,
        bmr_model_id=resolved_bmr_model_id,
        bmr_model_name=bmr_model.name,
        tdee_model_id=tdee_model_id,
        tdee_model_name=tdee_model.name,
    )


class ComponentTDEEResult(BaseModel):
    """The fully-explained output of
    :func:`calculate_tdee_from_components`.

    Unlike :class:`TDEEResult` (which reports a single BMR-to-TDEE
    scaling factor from Phase 5's PAL-multiplier model), this result
    reports each of the three classical TDEE components -- BMR,
    Activity Energy Expenditure, and Thermic Effect of Food --
    computed *independently* and summed, which is only possible now
    that Phase 6 (TEF) and Phase 7 (Activity) both exist. This is the
    artifact that resolves the double-counting caveat flagged in
    ``docs/phase_notes/phase_05.md`` and ``phase_06.md``.
    """

    model_config = ConfigDict(frozen=True)

    bmr_kcal: float
    activity_kcal: float
    tef_kcal: float
    tdee_kcal: float
    bmr_model_id: str
    bmr_model_name: str
    activity_model_id: str
    activity_model_name: str
    tef_model_id: str
    tef_model_name: str


def calculate_tdee_from_components(
    person: Person,
    macros: MacronutrientGrams,
    bmr_model_id: str | BMRModel = DEFAULT_BMR_MODEL_ID,
    activity_model_id: str = DEFAULT_ACTIVITY_MODEL_ID,
    activity_model_kwargs: dict[str, Any] | None = None,
    tef_model_id: str = DEFAULT_TEF_MODEL_ID,
) -> ComponentTDEEResult:
    """Calculate TDEE as the independent sum of BMR + AEE + TEF.

    This is the composition the project's architecture always
    intended (``docs/architecture.md``: "models/tdee -- Combines BMR +
    activity + TEF"), now buildable because Phase 6 (TEF) and Phase 7
    (Activity) both exist. Contrast with :func:`calculate_tdee`, which
    uses a single bundled BMR-to-TDEE multiplier and does not attempt
    to separate out TEF at all.

    Safety check -- why this function can raise on a valid-looking
    activity model:
        Not every ``ActivityModel`` is safe to sum with an
        independently-computed TEF (see
        ``metabosim.models.activity.base`` module docstring for the
        full explanation: PAL-ratio-based strategies already
        implicitly include an average TEF; only MET-based strategies
        are "pure" movement-cost estimates). This function checks
        ``activity_model.includes_average_tef`` and raises
        ``ValueError`` rather than silently returning a
        double-counted, scientifically wrong TDEE figure.

    Parameters
    ----------
    person:
        The subject to calculate for.
    macros:
        The macronutrient composition of the intake being evaluated,
        used to compute the TEF component.
    bmr_model_id:
        A key registered in ``metabosim.models.bmr.registry`` -- or a
        pre-built ``BMRModel`` instance (e.g. a
        ``metabosim.models.disease.DiseaseModifiedBMRModel``; Phase
        14). See module docstring, "Accepting a pre-built BMR model."
    activity_model_id:
        A key registered in ``metabosim.models.activity.registry``.
        Must resolve to a model with ``includes_average_tef = False``
        (currently only ``"met_based"`` qualifies).
    activity_model_kwargs:
        Forwarded to the activity model's constructor. ``"met_based"``
        requires ``{"entries": [...]}`` -- a list of
        ``metabosim.models.activity.met_based.ActivityEntry``.
    tef_model_id:
        A key registered in ``metabosim.models.tef.registry``.

    Returns
    -------
    ComponentTDEEResult
        Each component figure, the summed TDEE, and the identifying
        names of all three strategies used. ``bmr_model_id`` on the
        result is ``"custom"`` when a pre-built ``BMRModel`` instance
        was passed in, since there is no registry ID to report.

    Raises
    ------
    KeyError
        If any model ID is not registered.
    ValueError
        If the chosen BMR model requires data the ``person`` doesn't
        have, or if the chosen activity model already implicitly
        includes an average TEF (see safety check above).
    TypeError
        If required constructor arguments for the chosen activity
        model were not supplied via ``activity_model_kwargs``.

    Examples
    --------
    >>> from metabosim.domain import ActivityLevel, MacronutrientGrams, Person, Sex
    >>> from metabosim.models.activity import ActivityEntry
    >>> person = Person(
    ...     sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80,
    ...     activity_level=ActivityLevel.MODERATE,
    ... )
    >>> macros = MacronutrientGrams(
    ...     protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30,
    ... )
    >>> entries = [ActivityEntry(met=6.0, duration_hours=1.0, label="jogging")]
    >>> result = calculate_tdee_from_components(
    ...     person, macros, activity_model_kwargs={"entries": entries},
    ... )
    >>> round(result.bmr_kcal, 1)
    1780.0
    >>> round(result.activity_kcal, 1)
    400.0
    >>> round(result.tef_kcal, 1)
    258.9
    >>> round(result.tdee_kcal, 1)
    2438.9
    """
    bmr_model, resolved_bmr_model_id = _resolve_bmr_model(bmr_model_id)
    bmr_kcal = bmr_model.calculate(person)

    activity_model = get_activity_model(
        activity_model_id, **(activity_model_kwargs or {})
    )
    if activity_model.includes_average_tef:
        raise ValueError(
            f"Activity model {activity_model.name!r} already implicitly "
            "includes an average thermic effect of food (its "
            "includes_average_tef attribute is True). Adding a "
            "separately-computed TEF component on top of it would "
            "double-count food-processing energy cost. Use a MET-based "
            "activity model instead (e.g. activity_model_id='met_based'), "
            "or use calculate_tdee() if you want a single bundled "
            "BMR-to-TDEE multiplier without a separate TEF breakdown."
        )
    activity_kcal = activity_model.calculate(person, bmr_kcal)

    tef_model = get_tef_model(tef_model_id)
    tef_kcal = tef_model.calculate(macros)

    tdee_kcal = bmr_kcal + activity_kcal + tef_kcal

    return ComponentTDEEResult(
        bmr_kcal=bmr_kcal,
        activity_kcal=activity_kcal,
        tef_kcal=tef_kcal,
        tdee_kcal=tdee_kcal,
        bmr_model_id=resolved_bmr_model_id,
        bmr_model_name=bmr_model.name,
        activity_model_id=activity_model_id,
        activity_model_name=activity_model.name,
        tef_model_id=tef_model_id,
        tef_model_name=tef_model.name,
    )
