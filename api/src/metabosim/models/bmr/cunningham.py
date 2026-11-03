"""
metabosim.models.bmr.cunningham
==================================

Cunningham RMR equation (1980).

Reference
---------
Cunningham JJ. "A reanalysis of the factors influencing basal
metabolic rate in normal adults." *Am J Clin Nutr.* 1980;33(11):2372-2374.

Equation
--------
::

    RMR = 500 + 22 * lean_mass_kg

Like Katch-McArdle, this is a lean-mass-based, sex-independent
equation. It was derived from a reanalysis of pooled BMR data regressed
against fat-free mass, and tends to produce somewhat higher estimates
than Katch-McArdle for the same lean mass. It is frequently favored in
sports-nutrition contexts for lean, muscular individuals, where
weight-based equations (Mifflin-St Jeor, Harris-Benedict) are known to
underestimate metabolic rate.

Limitations
-----------
Same body-composition-measurement-accuracy dependency as
Katch-McArdle -- see
``metabosim.models.bmr.katch_mcardle`` for the general caveat about
propagated body-fat-percentage measurement error.
"""

from __future__ import annotations

from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class CunninghamBMR(BMRModel):
    """Cunningham (1980) RMR equation.

    Sex-independent; **requires** ``Person.body_fat_percent`` to be set.
    """

    name = "Cunningham (1980)"
    requires_body_fat = True

    def calculate(self, person: Person) -> float:
        if person.lean_mass_kg is None:
            raise ValueError(
                "CunninghamBMR requires Person.body_fat_percent to be "
                "set (it is used to derive lean_mass_kg); received a "
                "Person with body_fat_percent=None. Use a body-"
                "composition-independent model such as MifflinStJeorBMR "
                "if body fat percentage is unavailable."
            )
        return 500.0 + 22.0 * person.lean_mass_kg
