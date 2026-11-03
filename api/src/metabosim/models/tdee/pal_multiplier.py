"""
metabosim.models.tdee.pal_multiplier
=======================================

PAL (Physical Activity Level) multiplier TDEE model.

TDEE = BMR x activity_multiplier

Reference
---------
The five-tier activity multiplier scheme implemented here (1.2 /
1.375 / 1.55 / 1.725 / 1.9) is the traditional clinical/practical PAL
table long used in dietetics practice to scale a measured or
predicted BMR up to an estimated TDEE. It is widely reproduced across
clinical nutrition references, including Mahan LK, Raymond JL, eds.
*Krause's Food & the Nutrition Care Process.* Elsevier. (Table of
activity factors for estimating total energy needs.)

Multiplier table
-----------------
::

    Sedentary     1.200   little or no exercise
    Light         1.375   light exercise/sports 1-3 days/week
    Moderate      1.550   moderate exercise/sports 3-5 days/week
    Active        1.725   hard exercise/sports 6-7 days/week
    Very active   1.900   very hard daily exercise and/or physical job

Important limitation -- read before using this model
------------------------------------------------------
This is NOT the only published PAL scheme. The Institute of Medicine
(IOM, 2005) Dietary Reference Intakes use a different, narrower-banded
four-tier PAL system derived from doubly-labeled-water studies. The
table above is deliberately used here because it maps directly onto
this project's five-tier ``metabosim.domain.enums.ActivityLevel``
(itself modeled on common clinical categorization), and because it is
the scheme most familiar to dietetics practitioners.

These published multipliers also implicitly bundle an *average*
thermic effect of food into the activity factor -- they were derived
from and validated against total measured energy expenditure, not
BMR + explicit TEF + explicit activity as separately-modeled
components. Consequently, this model's TDEE output should NOT be
additionally incremented by a separate TEF calculation
(``metabosim.models.tef``, Phase 6) without first re-deriving or
re-validating the combination -- doing so naively would double-count
food-processing energy cost. This caveat is revisited in Phase 6's
design notes once an explicit TEF model exists.

When ``metabosim.models.activity`` (Phase 7) is built with MET-based,
IOM-consistent activity energy modeling, this multiplier table is
expected to be superseded (or offered as an explicit alternative,
clearly labeled as the traditional scheme) rather than being the only
option -- see ``docs/phase_notes/phase_05.md`` for the migration plan.
"""

from __future__ import annotations

from metabosim.domain.enums import ActivityLevel
from metabosim.domain.person import Person
from metabosim.models.tdee.base import TDEEModel

#: Traditional clinical PAL multiplier table, keyed by
#: ``ActivityLevel``. See module docstring for citation and caveats.
_ACTIVITY_MULTIPLIERS: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.200,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.550,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.900,
}


class PALMultiplierTDEE(TDEEModel):
    """Scales BMR up to TDEE using the traditional five-tier PAL
    multiplier table (see module docstring).
    """

    name = "PAL Multiplier (traditional clinical activity factors)"

    def calculate(self, person: Person, bmr_kcal: float) -> float:
        if bmr_kcal <= 0.0:
            raise ValueError(
                f"bmr_kcal must be positive; received {bmr_kcal!r}. "
                "Compute BMR with a metabosim.models.bmr.BMRModel first."
            )
        multiplier = _ACTIVITY_MULTIPLIERS[person.activity_level]
        return bmr_kcal * multiplier


def get_activity_multiplier(activity_level: ActivityLevel) -> float:
    """Return the traditional PAL multiplier for a given
    ``ActivityLevel``, without requiring a full ``Person`` instance.

    Exposed as a standalone function (in addition to being used
    internally by ``PALMultiplierTDEE.calculate``) so callers -- e.g.
    a future CLI/report that wants to display "your activity
    multiplier is 1.55" -- don't need to construct a dummy ``Person``
    just to look up a constant.
    """
    return _ACTIVITY_MULTIPLIERS[activity_level]
