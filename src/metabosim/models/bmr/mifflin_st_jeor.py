"""
metabosim.models.bmr.mifflin_st_jeor
=======================================

Mifflin-St Jeor BMR equation (1990).

Reference
---------
Mifflin MD, St Jeor ST, Hill LA, Scott BJ, Daugherty SA, Koh YO.
"A new predictive equation for resting energy expenditure in healthy
individuals." *Am J Clin Nutr.* 1990;51(2):241-247.

Validated on a healthy adult population spanning normal-weight to
obese subjects. Widely regarded -- including by the Academy of
Nutrition and Dietetics -- as the most broadly accurate general-
population BMR equation currently available, and it does not require
a body composition measurement.

Equation
--------
::

    Men:   BMR = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    Women: BMR = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161

Limitations
-----------
Derived from a predominantly North American adult sample; the source
study population was adults, so this equation is not validated for
subjects under approximately 19 years of age. May be less accurate for
individuals whose body composition deviates substantially from
population norms (e.g. very high muscularity), since it uses total
body weight rather than lean mass.
"""

from __future__ import annotations

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class MifflinStJeorBMR(BMRModel):
    """Mifflin-St Jeor (1990) BMR equation.

    Sex-specific; does not require body composition data.
    """

    name = "Mifflin-St Jeor (1990)"
    requires_body_fat = False

    def calculate(self, person: Person) -> float:
        base = (
            10.0 * person.weight_kg + 6.25 * person.height_cm - 5.0 * person.age_years
        )
        if person.sex == Sex.MALE:
            return base + 5.0
        return base - 161.0
