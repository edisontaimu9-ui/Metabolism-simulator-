"""
metabosim.models.bmr.base
============================

Common interface for all BMR (Basal Metabolic Rate) / RMR (Resting
Metabolic Rate) model strategies.

Every concrete BMR model in this package implements ``BMRModel`` and
is registered under a string ID in ``metabosim.models.bmr.registry``,
so callers -- and, from Phase 5 onward, ``metabosim.models.tdee`` --
can select an equation at runtime rather than being compile-time-bound
to one particular formula.

Design note on "BMR vs RMR": the literature uses these terms loosely.
Mifflin-St Jeor and Harris-Benedict were derived under strict basal
conditions and are usually labeled BMR; Katch-McArdle and Cunningham
are more commonly described as RMR equations. This package does not
enforce that distinction structurally -- all four implement the same
interface and return a daily kcal figure -- but each model's own
docstring states which label the source literature uses.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.person import Person


class BMRModel(ABC):
    """Abstract base class for all BMR/RMR calculation strategies.

    Subclasses must set the class attributes ``name`` and
    ``requires_body_fat``, and implement ``calculate``.
    """

    #: Short, human-readable name of the equation, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed BMR Model"

    #: Whether this model requires ``Person.body_fat_percent`` to be
    #: set (true for lean-mass-based equations such as Katch-McArdle
    #: and Cunningham). Overridden by every concrete subclass.
    requires_body_fat: bool = False

    @abstractmethod
    def calculate(self, person: Person) -> float:
        """Calculate BMR/RMR in kilocalories per day.

        Parameters
        ----------
        person:
            The subject to calculate for.

        Returns
        -------
        float
            Estimated BMR/RMR, in kcal/day. Always positive for any
            physiologically valid ``Person``.

        Raises
        ------
        ValueError
            If ``person`` is missing data this specific model requires
            (e.g. ``body_fat_percent`` for lean-mass-based equations).
            Subclasses must raise this explicitly rather than letting
            an ``AttributeError``/``TypeError`` propagate, so the
            failure is self-explanatory to a caller who picked the
            wrong model for the data they have.
        """
        raise NotImplementedError

    def __call__(self, person: Person) -> float:
        """Convenience alias so model instances are directly callable:
        ``model(person)`` is equivalent to ``model.calculate(person)``.
        """
        return self.calculate(person)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
