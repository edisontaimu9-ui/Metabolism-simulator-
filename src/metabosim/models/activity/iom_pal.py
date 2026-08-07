"""
metabosim.models.activity.iom_pal
====================================

IOM (Institute of Medicine) Physical Activity Level (PAL) ratio based
Activity Energy Expenditure model -- a top-down estimate that scales
BMR by an activity-level-dependent multiplier, requiring only a
qualitative activity category (no logged activity diary).

    AEE = BMR * (PAL - 1)

IMPORTANT -- read before combining this model's output with TEF
---------------------------------------------------------------------
This model's PAL multipliers are derived from doubly-labeled-water
studies as (measured total energy expenditure) / (measured or
predicted BMR). Because that ratio's numerator is *total* expenditure,
it already contains an average thermic-effect-of-food contribution.
``includes_average_tef = True`` on this class reflects that: its AEE
output must NOT be added to a separately-computed
``metabosim.models.tef`` figure, or food-processing energy cost would
be double-counted. This is the same caveat documented in
``metabosim.models.tdee.pal_multiplier`` for Phase 5's traditional
activity-factor table. Contrast with
``metabosim.models.activity.met_based.METBasedActivityModel``, which
IS safe to combine with a separate TEF figure -- see that module's
docstring for why.

Reference and the five-tier interpolation
---------------------------------------------------------------------
Institute of Medicine (US). *Dietary Reference Intakes for Energy,
Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino
Acids.* National Academies Press; 2005. IOM (2005) defines PAL using
**four** quantitative bands:

::

    Sedentary     1.0  to <1.4
    Low Active    1.4  to <1.6
    Active        1.6  to <1.9
    Very Active   1.9  to <2.5

This project's ``metabosim.domain.enums.ActivityLevel`` has **five**
qualitative tiers (sedentary / light / moderate / active /
very_active), chosen in Phase 3 to match common clinical
categorization rather than IOM's four bands directly (this mismatch
was flagged explicitly in that phase's design notes). The table below
is this project's own interpolation of representative point values
across the IOM bands onto five tiers -- it is NOT an official IOM
table, and is documented as such:

::

    SEDENTARY     1.20   (IOM Sedentary band midpoint)
    LIGHT         1.40   (IOM Sedentary/Low Active boundary)
    MODERATE      1.60   (IOM Low Active/Active boundary)
    ACTIVE        1.80   (within IOM Active band)
    VERY_ACTIVE   2.20   (IOM Very Active band midpoint)

Anyone citing this model's output in a publication should cite this
interpolation choice explicitly, not attribute the five specific
values to IOM (2005) itself.
"""

from __future__ import annotations

from metabosim.domain.enums import ActivityLevel
from metabosim.domain.person import Person
from metabosim.models.activity.base import ActivityModel

#: This project's five-tier interpolation of IOM (2005) PAL bands.
#: See module docstring for the full citation and interpolation
#: rationale -- these values are NOT verbatim IOM table entries.
_PAL_VALUES: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.20,
    ActivityLevel.LIGHT: 1.40,
    ActivityLevel.MODERATE: 1.60,
    ActivityLevel.ACTIVE: 1.80,
    ActivityLevel.VERY_ACTIVE: 2.20,
}


class IOMPALActivityModel(ActivityModel):
    """Estimates AEE as BMR * (PAL - 1), using this project's five-tier
    interpolation of IOM (2005) PAL bands. See module docstring for
    the crucial TEF double-counting caveat before combining this
    model's output with a separately-computed TEF figure.
    """

    name = "IOM PAL Ratio (2005, 5-tier interpolation)"
    includes_average_tef = True

    def calculate(self, person: Person, bmr_kcal: float) -> float:
        if bmr_kcal <= 0.0:
            raise ValueError(
                f"bmr_kcal must be positive; received {bmr_kcal!r}. "
                "Compute BMR with a metabosim.models.bmr.BMRModel first."
            )
        pal = _PAL_VALUES[person.activity_level]
        return bmr_kcal * (pal - 1.0)


def get_pal_value(activity_level: ActivityLevel) -> float:
    """Return this project's interpolated IOM PAL value for a given
    ``ActivityLevel``, without requiring a full ``Person`` instance.

    See module docstring for the interpolation rationale.
    """
    return _PAL_VALUES[activity_level]
