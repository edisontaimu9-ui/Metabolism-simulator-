"""
metabosim.models.bmr.elia_organ_based
========================================

Organ-based BMR equation: a bottom-up alternative to the top-down
regression equations (Mifflin-St Jeor, Harris-Benedict, Katch-McArdle,
Cunningham) implemented elsewhere in this package.

Rather than fitting a formula directly to measured BMR from
anthropometric inputs, this model sums cited specific metabolic rates
for individual organs and tissues (brain, liver, heart, kidneys,
residual lean tissue, adipose tissue), applied to the subject's
tracked fat mass and lean mass. See
``metabosim.models.organ.elia`` module docstring for the full model,
citations (Elia, 1992; Wang et al., 2010; Molina & DiMaio, 2012), and
design decisions.

Reference
---------
Elia M. "Organ and tissue contribution to metabolic rate." In:
Kinney JM, Tucker HN, eds. *Energy Metabolism: Tissue Determinants and
Cellular Corollaries.* Raven Press; 1992:61-80.

Like Katch-McArdle and Cunningham, this equation is sex-independent
(it does not use sex directly -- though organ Ki values were derived
from mixed-sex populations) and **requires**
``Person.body_fat_percent`` to be set, since it needs both fat mass
and lean mass, not just total weight.

Why use this over the regression equations
-----------------------------------------------
This model provides an independent, mechanistically-motivated
cross-check: if this estimate and, say, Mifflin-St Jeor diverge
substantially for the same subject, that divergence itself is useful
diagnostic information (e.g. an atypical body composition for that
subject's weight). It is not presented as more accurate than the
regression equations -- both approaches have their own error sources
-- see ``docs/phase_notes/phase_13.md`` for a worked comparison.
"""

from __future__ import annotations

from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel
from metabosim.models.organ.elia import calculate_organ_bmr_breakdown_kcal


class EliaOrganBasedBMR(BMRModel):
    """Organ-based BMR equation (Elia, 1992).

    Sex-independent; **requires** ``Person.body_fat_percent`` to be
    set (to derive both fat mass and lean mass). Automatically uses
    age-adjusted specific metabolic rates (Wang et al., 2010) for
    subjects over 50 -- see
    ``metabosim.models.organ.elia.calculate_organ_bmr_breakdown_kcal``.
    """

    name = "Elia Organ-Based (1992)"
    requires_body_fat = True

    def calculate(self, person: Person) -> float:
        if person.fat_mass_kg is None or person.lean_mass_kg is None:
            raise ValueError(
                "EliaOrganBasedBMR requires Person.body_fat_percent to be "
                "set (it is used to derive fat_mass_kg and lean_mass_kg); "
                "received a Person with body_fat_percent=None. Use a "
                "body-composition-independent model such as "
                "MifflinStJeorBMR if body fat percentage is unavailable."
            )
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=person.fat_mass_kg,
            lean_mass_kg=person.lean_mass_kg,
            age_years=person.age_years,
        )
        return breakdown.total_kcal
