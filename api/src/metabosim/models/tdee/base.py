"""
metabosim.models.tdee.base
=============================

Defines ``TDEEModel``, the common interface for strategies that turn a
Basal/Resting Metabolic Rate figure into Total Daily Energy
Expenditure.

Design note -- why ``calculate`` takes a pre-computed ``bmr_kcal``
rather than a ``BMRModel``:
    A ``TDEEModel`` should not need to know or care which BMR equation
    produced the BMR figure it's scaling up. This keeps BMR selection
    (``metabosim.models.bmr``) and TDEE composition
    (``metabosim.models.tdee``) independently swappable -- exactly the
    Strategy-pattern separation described in ``docs/architecture.md``.
    The two are wired together by
    ``metabosim.models.tdee.calculator.calculate_tdee``, which is the
    actual "TDEE engine" entry point most callers should use.

Design note -- why this doesn't yet take a TEF model:
    As of Phase 5, ``metabosim.models.tef`` does not exist yet
    (Phase 6). The current concrete ``TDEEModel`` implementation
    (``PALMultiplierTDEE``) uses a traditional PAL multiplier scheme
    whose published values implicitly bundle an average thermic effect
    of food into the activity multiplier -- see that module's
    docstring. When Phase 6 introduces an explicit,
    macronutrient-specific TEF model, ``calculate_tdee`` will be
    extended to optionally add a separately-computed TEF adjustment on
    top of a base TDEE, without needing to change this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.person import Person


class TDEEModel(ABC):
    """Abstract base class for BMR-to-TDEE scaling strategies.

    Subclasses must set the class attribute ``name`` and implement
    ``calculate``.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed TDEE Model"

    @abstractmethod
    def calculate(self, person: Person, bmr_kcal: float) -> float:
        """Calculate Total Daily Energy Expenditure in kilocalories/day.

        Parameters
        ----------
        person:
            The subject. Implementations read whichever ``Person``
            fields they need (typically ``activity_level``) but must
            NOT recompute or duplicate BMR themselves -- BMR is always
            supplied via ``bmr_kcal``.
        bmr_kcal:
            A pre-computed BMR/RMR figure, in kcal/day, typically
            produced by a ``metabosim.models.bmr.BMRModel``. Must be
            positive.

        Returns
        -------
        float
            Estimated TDEE, in kcal/day. Always >= ``bmr_kcal`` for
            any physiologically valid strategy, since TDEE is BMR plus
            (never minus) activity and food-processing energy costs.

        Raises
        ------
        ValueError
            If ``bmr_kcal`` is not positive.
        """
        raise NotImplementedError

    def __call__(self, person: Person, bmr_kcal: float) -> float:
        """Convenience alias: ``model(person, bmr_kcal)`` is equivalent
        to ``model.calculate(person, bmr_kcal)``."""
        return self.calculate(person, bmr_kcal)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
