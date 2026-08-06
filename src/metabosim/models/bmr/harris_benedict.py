"""
metabosim.models.bmr.harris_benedict
=======================================

Harris-Benedict BMR equation, in its 1984 revised form.

Reference
---------
Harris JA, Benedict FG. *A Biometric Study of Basal Metabolism in Man.*
Washington, DC: Carnegie Institution of Washington; 1919.

Revised coefficients: Roza AM, Shizgal HM. "The Harris Benedict
equation reevaluated: resting energy requirements and the body cell
mass." *Am J Clin Nutr.* 1984;40(1):168-182.

This module implements the 1984 Roza & Shizgal revision rather than
the original 1919 coefficients. The revision is the version in common
clinical and research use today, and corrects known biases identified
in the original 1919 sample.

Equation
--------
::

    Men:   BMR = 88.362 + 13.397*weight_kg + 4.799*height_cm - 5.677*age_years
    Women: BMR = 447.593 + 9.247*weight_kg + 3.098*height_cm - 4.330*age_years

Limitations
-----------
Tends to overestimate BMR in obese individuals relative to
Mifflin-St Jeor (see ``metabosim.models.bmr.mifflin_st_jeor``).
Retained in this package primarily for historical comparison and
because it remains widely referenced in clinical practice and older
research literature.
"""

from __future__ import annotations

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class HarrisBenedictBMR(BMRModel):
    """Harris-Benedict BMR equation (1919, revised Roza & Shizgal 1984).

    Sex-specific; does not require body composition data.
    """

    name = "Harris-Benedict (1919, rev. 1984)"
    requires_body_fat = False

    def calculate(self, person: Person) -> float:
        if person.sex == Sex.MALE:
            return (
                88.362
                + 13.397 * person.weight_kg
                + 4.799 * person.height_cm
                - 5.677 * person.age_years
            )
        return (
            447.593
            + 9.247 * person.weight_kg
            + 3.098 * person.height_cm
            - 4.330 * person.age_years
        )
