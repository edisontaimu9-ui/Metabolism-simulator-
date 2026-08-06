"""
metabosim.models.tef.base
============================

Defines ``TEFModel``, the common interface for strategies that
estimate the Thermic Effect of Food (TEF) -- the energy cost of
digesting, absorbing, and metabolizing consumed nutrients.

TEF is sometimes called "diet-induced thermogenesis" (DIT) in the
literature. It is the smallest of the three classical components of
total daily energy expenditure (BMR, activity, TEF), but it is not
negligible and, critically, it depends on *what* is eaten, not just
*how much* -- protein has a substantially higher thermic cost per
kcal than fat. This is why TEF is modeled as a function of
macronutrient composition (``metabosim.domain.diet.MacronutrientGrams``),
not of total energy intake alone (though one simplified strategy,
``FixedPercentageTEF``, does exactly that as a documented
approximation -- see that module).

Design note -- relationship to ``metabosim.models.tdee``:
    As documented in ``metabosim.models.tdee.pal_multiplier``, the
    Phase 5 PAL-multiplier TDEE model's published multipliers were
    derived against *total* measured energy expenditure, and therefore
    already implicitly bundle an average TEF. Adding this phase's
    explicit, macronutrient-specific TEF on top of that TDEE figure
    would double-count food-processing energy cost. Wiring TEF into
    the TDEE/energy-balance pipeline correctly (e.g. by decomposing
    TDEE into an activity-only component once
    ``metabosim.models.activity`` exists, Phase 7) is deferred --
    see ``docs/phase_notes/phase_06.md`` for the explicit plan. This
    module and its concrete strategies are fully correct and testable
    in isolation regardless of that pending integration work.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.diet import MacronutrientGrams


class TEFModel(ABC):
    """Abstract base class for Thermic Effect of Food strategies.

    Subclasses must set the class attribute ``name`` and implement
    ``calculate``.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed TEF Model"

    @abstractmethod
    def calculate(self, macros: MacronutrientGrams) -> float:
        """Calculate the Thermic Effect of Food, in kilocalories/day.

        Parameters
        ----------
        macros:
            The macronutrient composition of the intake being
            evaluated (typically one day's worth).

        Returns
        -------
        float
            Estimated TEF, in kcal/day. Always non-negative, and
            always strictly less than ``macros.energy_kcal`` for any
            physiologically plausible strategy (TEF is a *fraction* of
            the energy consumed, not the whole of it).
        """
        raise NotImplementedError

    def __call__(self, macros: MacronutrientGrams) -> float:
        """Convenience alias: ``model(macros)`` is equivalent to
        ``model.calculate(macros)``."""
        return self.calculate(macros)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
