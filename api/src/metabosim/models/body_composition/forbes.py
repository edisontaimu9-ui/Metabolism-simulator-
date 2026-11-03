"""
metabosim.models.body_composition.forbes
============================================

The Forbes fat-mass / fat-free-mass partitioning model: the fraction
of an incremental body mass change that is fat-free mass (FFM) depends
only on the subject's current fat mass (FM):

    dFFM/dBW = C / (C + FM)

where ``C`` (the "Forbes constant") is derived from the slope of the
cross-sectional log-linear FFM-vs-FM relationship Forbes fit to
stratified body composition data.

Reference
---------
Forbes GB. "Lean body mass-body fat interrelationships in humans."
*Nutr Rev.* 1987;45(9):225-231.

Forbes GB. "Body fat content influences the body composition response
to nutrition and exercise." *Ann N Y Acad Sci.* 2000;904:359-365.

Hall KD. "Body fat and fat-free mass inter-relationships: Forbes's
theory revisited." *Br J Nutr.* 2007;97(6):1059-1063. Hall's Equation
2 gives the infinitesimal differential form used directly here:
``dFFM/dBW = 10.4 / (10.4 + FM)``, with ``C = 10.4 kg`` derived from
Forbes' original female-only cross-sectional data.

Thomas D, Das SK, Levine JA, et al. "New fat free mass - fat mass
model for use in physiological energy balance equations."
*Nutr Metab (Lond).* 2010;7:39. Reports a separately-fit male
constant, ``C = 13.8 kg`` (from ``FFM = 13.8 ln(FM) + 16.9``), used
here as the default for male subjects. This male-specific value rests
on a smaller evidence base than Forbes' original female-derived
constant -- disclosed explicitly, not presented as equally
well-established.

What the constant means physically
-------------------------------------
``C`` is the fat mass at which a subject is predicted to gain or lose
fat mass and fat-free mass in exactly equal amounts. Below that fat
mass, a larger share of any change is fat-free mass; above it, a
larger share is fat. This has a real, checkable consequence used
directly in this module's tests: at ``current_fat_mass_kg == C``,
``ffm_fraction_of_change`` must equal exactly 0.5.

Design decision: per-day discrete application, not Hall's exact
macroscopic solution
---------------------------------------------------------------------
Forbes' equation above is, by construction, only strictly valid for
*infinitesimal* mass changes -- Hall (2007) derived a more precise
closed-form correction for large, discrete (macroscopic) changes,
needed for example when modeling the multi-kilogram single-step mass
changes seen after bariatric surgery. This project's simulation engine
(``metabosim.simulation``) instead advances in small daily steps
(typically well under 0.1 kg/day), and applies this infinitesimal
formula directly as a per-day Euler step -- consistent with how the
rest of the simulation already treats each day as one small
discrete-time step of an underlying continuous process. Hall's exact
macroscopic solution is not implemented here; it would be the natural
choice if this project ever needed to jump forward by large mass
changes in a single step rather than simulating day by day.
"""

from __future__ import annotations

from metabosim.domain.enums import Sex
from metabosim.models.body_composition.base import BodyCompositionModel

#: Forbes constant for female subjects, in kg. See module docstring.
FORBES_CONSTANT_FEMALE_KG: float = 10.4

#: Forbes constant for male subjects, in kg. See module docstring for
#: the weaker evidentiary basis of this value relative to the female
#: constant above.
FORBES_CONSTANT_MALE_KG: float = 13.8


class ForbesPartitionModel(BodyCompositionModel):
    """Partitions body mass change into fat/fat-free components using
    Forbes' cross-sectional FFM-vs-FM relationship. See module
    docstring for the model, its constants, and the per-day discrete
    application design decision.

    Parameters
    ----------
    forbes_constant_female_kg:
        ``C`` for female subjects. Defaults to 10.4 kg (Forbes,
        1987/2000; Hall, 2007).
    forbes_constant_male_kg:
        ``C`` for male subjects. Defaults to 13.8 kg (Thomas et al.,
        2010).
    """

    name = "Forbes Partitioning (Forbes, 1987/2000; Hall, 2007)"

    def __init__(
        self,
        forbes_constant_female_kg: float = FORBES_CONSTANT_FEMALE_KG,
        forbes_constant_male_kg: float = FORBES_CONSTANT_MALE_KG,
    ) -> None:
        if forbes_constant_female_kg <= 0.0:
            raise ValueError(
                "forbes_constant_female_kg must be positive; received "
                f"{forbes_constant_female_kg!r}."
            )
        if forbes_constant_male_kg <= 0.0:
            raise ValueError(
                "forbes_constant_male_kg must be positive; received "
                f"{forbes_constant_male_kg!r}."
            )
        self.forbes_constant_female_kg = forbes_constant_female_kg
        self.forbes_constant_male_kg = forbes_constant_male_kg

    def _forbes_constant_for(self, sex: Sex) -> float:
        """Return the sex-appropriate Forbes constant."""
        if sex == Sex.MALE:
            return self.forbes_constant_male_kg
        return self.forbes_constant_female_kg

    def ffm_fraction_of_change(self, current_fat_mass_kg: float, sex: Sex) -> float:
        if current_fat_mass_kg < 0.0:
            raise ValueError(
                "current_fat_mass_kg must be non-negative; received "
                f"{current_fat_mass_kg!r}."
            )
        c = self._forbes_constant_for(sex)
        return c / (c + current_fat_mass_kg)
