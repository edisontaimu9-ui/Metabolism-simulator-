"""
metabosim.models.bmr.katch_mcardle
=====================================

Katch-McArdle RMR equation.

Reference
---------
Katch VL, McArdle WD, Katch FI. *Exercise Physiology: Nutrition,
Energy, and Human Performance.* Lippincott Williams & Wilkins.

Equation
--------
::

    RMR = 370 + 21.6 * lean_mass_kg

Unlike Mifflin-St Jeor and Harris-Benedict, this equation is
sex-independent because it is driven entirely by fat-free (lean) mass
-- the body's primary metabolically active tissue compartment. This
makes it potentially more accurate for individuals whose body
composition deviates substantially from population averages (e.g.
very lean athletes, or individuals with unusually high fat mass), at
the cost of requiring a body fat percentage measurement that
Mifflin-St Jeor and Harris-Benedict do not.

Limitations
-----------
Accuracy is entirely dependent on the accuracy of the underlying body
fat percentage estimate; a poorly-measured body fat percentage (e.g.
from a low-accuracy consumer bioimpedance scale) propagates directly
into a biased RMR estimate.
"""

from __future__ import annotations

from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class KatchMcArdleBMR(BMRModel):
    """Katch-McArdle RMR equation.

    Sex-independent; **requires** ``Person.body_fat_percent`` to be set.
    """

    name = "Katch-McArdle"
    requires_body_fat = True

    def calculate(self, person: Person) -> float:
        if person.lean_mass_kg is None:
            raise ValueError(
                "KatchMcArdleBMR requires Person.body_fat_percent to be "
                "set (it is used to derive lean_mass_kg); received a "
                "Person with body_fat_percent=None. Use a body-"
                "composition-independent model such as MifflinStJeorBMR "
                "if body fat percentage is unavailable."
            )
        return 370.0 + 21.6 * person.lean_mass_kg
