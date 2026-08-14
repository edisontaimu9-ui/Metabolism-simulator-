"""
metabosim.models.disease.base
================================

Defines ``DiseaseModifier``, the common interface for disease-specific
adjustments to an already-computed BMR figure, and
``DiseaseModifiedBMRModel``, the Decorator that composes a base
``BMRModel`` with one or more ``DiseaseModifier`` instances into a
single, fully substitutable ``BMRModel``.

This is exactly the extensibility point ``docs/architecture.md``
described from Phase 1 onward: "New diseases: add a decorator in
models/disease/, compose over any base model without modifying that
base model." Nothing about ``metabosim.models.bmr`` (or, transitively,
``metabosim.models.tdee``) needed to change to support this -- a
disease-modified model is just another ``BMRModel`` as far as any
caller is concerned.

Design: two small classes, not one
--------------------------------------
``DiseaseModifier`` holds only the adjustment logic (given a raw kcal
figure and a ``Person``, return the adjusted figure) -- independently
testable, with no notion of "being" a BMR model itself.
``DiseaseModifiedBMRModel`` is the actual Decorator: it wraps a base
``BMRModel``, applies one or more modifiers in sequence, and exposes
the standard ``BMRModel`` interface so it can be used anywhere a base
BMR model could be -- including, from this phase onward,
``metabosim.models.tdee.calculator.calculate_tdee_from_components``,
which now accepts either a registry string ID or a pre-built
``BMRModel`` instance (see that module for details).

Multiple comorbidities
-------------------------
``DiseaseModifiedBMRModel`` accepts a *list* of modifiers, applied in
the order given, since real patients often have more than one
condition simultaneously (e.g. hypothyroidism and a concurrent fever).
Each modifier only ever sees the running kcal total after all
previously-applied modifiers -- there is no attempt to model
interaction effects between conditions beyond simple sequential
composition, which is disclosed as a simplification in
``docs/phase_notes/phase_14.md``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class DiseaseModifier(ABC):
    """Abstract base class for a disease-specific BMR adjustment.

    Subclasses must set ``name`` and implement ``apply_to_bmr_kcal``.
    """

    #: Short, human-readable name of the modifier, used in reports and
    #: composed model names. Overridden by every concrete subclass.
    name: str = "Unnamed Disease Modifier"

    @abstractmethod
    def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
        """Given an already-computed BMR figure, return the
        disease-adjusted figure.

        Parameters
        ----------
        base_bmr_kcal:
            The BMR figure to adjust, in kcal/day -- either a raw
            equation output, or the running total after any
            previously-applied modifiers (see module docstring on
            multiple comorbidities). Must be positive.
        person:
            The subject, in case a modifier needs subject-specific
            information beyond the running kcal total (none of the
            modifiers in this phase do, but the interface allows it).

        Returns
        -------
        float
            The adjusted BMR figure, in kcal/day.
        """
        raise NotImplementedError

    def __call__(self, base_bmr_kcal: float, person: Person) -> float:
        """Convenience alias for ``apply_to_bmr_kcal``."""
        return self.apply_to_bmr_kcal(base_bmr_kcal, person)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class DiseaseModifiedBMRModel(BMRModel):
    """Decorator composing a base ``BMRModel`` with one or more
    ``DiseaseModifier`` instances into a single, fully substitutable
    ``BMRModel``. See module docstring.

    Parameters
    ----------
    base_model:
        Any ``BMRModel`` instance (e.g. ``MifflinStJeorBMR()``,
        ``EliaOrganBasedBMR()``) -- this decorator works with every
        BMR strategy in the project without modification.
    modifiers:
        One or more ``DiseaseModifier`` instances, applied in order.
        Must be non-empty.

    Raises
    ------
    ValueError
        If ``modifiers`` is empty.
    """

    requires_body_fat = False

    def __init__(self, base_model: BMRModel, modifiers: list[DiseaseModifier]) -> None:
        if not modifiers:
            raise ValueError(
                "modifiers must contain at least one DiseaseModifier; "
                "received an empty list. Use the base_model directly "
                "if no disease adjustment is needed."
            )
        self.base_model = base_model
        self.modifiers = list(modifiers)
        self.requires_body_fat = base_model.requires_body_fat
        modifier_names = " + ".join(modifier.name for modifier in self.modifiers)
        self.name = f"{base_model.name} (adjusted for: {modifier_names})"

    def calculate(self, person: Person) -> float:
        bmr_kcal = self.base_model.calculate(person)
        for modifier in self.modifiers:
            bmr_kcal = modifier.apply_to_bmr_kcal(bmr_kcal, person)
        return bmr_kcal
