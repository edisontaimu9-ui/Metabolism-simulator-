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
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from metabosim.domain.person import Person
from metabosim.models.bmr.registry import get_model as get_bmr_model
from metabosim.models.tdee.registry import get_model as get_tdee_model

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
    bmr_model_id: str = DEFAULT_BMR_MODEL_ID,
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
        ``"katch_mcardle"``, ``"cunningham"``. Note that the
        lean-mass-based equations require ``person.body_fat_percent``
        to be set; see ``metabosim.models.bmr`` for details.
    tdee_model_id:
        A key registered in ``metabosim.models.tdee.registry``, e.g.
        ``"pal_multiplier"``.

    Returns
    -------
    TDEEResult
        The BMR figure, the TDEE figure, and the identifying names of
        both strategies used.

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
    bmr_model = get_bmr_model(bmr_model_id)
    bmr_kcal = bmr_model.calculate(person)

    tdee_model = get_tdee_model(tdee_model_id)
    tdee_kcal = tdee_model.calculate(person, bmr_kcal)

    return TDEEResult(
        bmr_kcal=bmr_kcal,
        tdee_kcal=tdee_kcal,
        bmr_model_id=bmr_model_id,
        bmr_model_name=bmr_model.name,
        tdee_model_id=tdee_model_id,
        tdee_model_name=tdee_model.name,
    )
