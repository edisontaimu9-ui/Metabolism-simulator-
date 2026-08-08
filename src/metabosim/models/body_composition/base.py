"""
metabosim.models.body_composition.base
==========================================

Defines ``BodyCompositionModel``, the common interface for strategies
that partition a total body mass change into fat mass (FM) and
fat-free/lean mass (FFM) components, as a function of the subject's
*current* fat mass and sex.

Why this exists
------------------
Every prior phase's energy balance and stepper logic used a single
blended tissue energy density
(``metabosim.models.energy_balance.tissue_energy_density``, default
0.25 fat-free / 0.75 fat) as a static population-average assumption,
explicitly flagged in that module's docstring as a placeholder pending
"a dynamically computed, subject-specific fraction... via the Forbes
partitioning curve." This module is that dynamic replacement: real
body composition research (Forbes, 1987, 2000) shows the FFM fraction
of a weight change depends on how much fat mass the subject already
has -- leaner individuals lose or gain proportionally more lean mass
for the same total mass change; individuals with more fat mass change
almost purely fat.

Template method pattern
--------------------------
Concrete subclasses only need to implement ``ffm_fraction_of_change``.
``partition_mass_change_kg`` is implemented once, here, in terms of
that method -- guaranteeing that the two are always mutually
consistent (the fat/lean split always sums exactly to the total mass
change, and always agrees with whatever fraction a caller might query
separately via ``ffm_fraction_of_change``) without every subclass
needing to reimplement that arithmetic itself.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.enums import Sex


class BodyCompositionModel(ABC):
    """Abstract base class for fat/fat-free mass partitioning strategies.

    Subclasses must set ``name`` and implement
    ``ffm_fraction_of_change``.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed Body Composition Model"

    @abstractmethod
    def ffm_fraction_of_change(self, current_fat_mass_kg: float, sex: Sex) -> float:
        """The fraction (0.0-1.0) of an incremental body mass change
        (gain or loss) that is fat-free mass, given the subject's
        *current* fat mass.

        Parameters
        ----------
        current_fat_mass_kg:
            The subject's fat mass at the moment the change begins.
            Must be non-negative.
        sex:
            The subject's biological sex; some strategies use
            sex-specific parameters (see
            ``metabosim.models.body_composition.forbes``).

        Returns
        -------
        float
            A value in [0.0, 1.0]. The complementary fraction
            ``1 - result`` is the fat-mass fraction of the change.
        """
        raise NotImplementedError

    def partition_mass_change_kg(
        self,
        total_mass_change_kg: float,
        current_fat_mass_kg: float,
        sex: Sex,
    ) -> tuple[float, float]:
        """Split a total mass change into ``(delta_fat_kg, delta_lean_kg)``.

        Implemented once, here, in terms of ``ffm_fraction_of_change``
        -- see the "Template method pattern" note in the module
        docstring for why concrete subclasses should not normally
        need to override this.

        Parameters
        ----------
        total_mass_change_kg:
            The total body mass change to partition (positive for a
            gain, negative for a loss).
        current_fat_mass_kg:
            The subject's fat mass at the moment the change begins.
        sex:
            The subject's biological sex.

        Returns
        -------
        tuple[float, float]
            ``(delta_fat_kg, delta_lean_kg)``, which always sum
            exactly to ``total_mass_change_kg``.
        """
        ffm_fraction = self.ffm_fraction_of_change(current_fat_mass_kg, sex)
        delta_lean_kg = ffm_fraction * total_mass_change_kg
        delta_fat_kg = total_mass_change_kg - delta_lean_kg
        return delta_fat_kg, delta_lean_kg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
