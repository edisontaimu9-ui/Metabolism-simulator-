"""
metabosim.models.activity.base
=================================

Defines ``ActivityModel``, the common interface for strategies that
estimate Activity Energy Expenditure (AEE): the energy cost of
physical movement, *net* of resting metabolic rate.

Contract: every ``ActivityModel.calculate()`` returns AEE in kcal/day,
representing energy expenditure *above* BMR, not total expenditure.
This is what lets AEE be added directly to BMR (and, where valid, to
TEF) without double-counting -- see the crucial distinction documented
below.

The critical distinction this phase resolves (read before using
either concrete model)
---------------------------------------------------------------------
Two fundamentally different measurement paradigms produce an "activity
energy expenditure" number, and they are NOT interchangeable in how
safely they combine with a separately-computed TEF figure
(``metabosim.models.tef``):

1. **Bottom-up, MET-based** (``metabosim.models.activity.met_based``):
   built from direct/indirect calorimetry measurements of specific
   physical movements (the Ainsworth Compendium of Physical
   Activities). A MET-based AEE figure measures only the mechanical/
   physiological cost of movement -- it has no statistical
   relationship to food intake or digestion. It can be safely added to
   BMR *and* to an independently-computed TEF without double-counting
   anything: ``TDEE = BMR + AEE_met_based + TEF``.

2. **Top-down, PAL-ratio-based** (``metabosim.models.activity.iom_pal``,
   and Phase 5's ``metabosim.models.tdee.pal_multiplier``): derived
   from doubly-labeled-water studies as (measured total energy
   expenditure) / (measured or predicted BMR). Because the numerator
   of that ratio is *total* expenditure, it already contains an
   average TEF contribution baked in. A PAL-ratio-based AEE figure
   must NOT be added to a separately-computed TEF -- doing so would
   double-count food-processing energy cost, exactly the caveat
   raised in ``metabosim.models.tdee.pal_multiplier`` and
   ``metabosim.models.tef.base``.

Both models are implemented and both are legitimate -- the choice
depends on what data is available (a logged activity diary vs. only a
qualitative activity-level category) and on how the result will be
combined with other components. See
``metabosim.models.tdee.calculator.calculate_tdee_from_components`` for
the composition function that correctly exploits case (1) to finally
resolve the double-counting caveat raised in Phases 5 and 6.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from metabosim.domain.person import Person


class ActivityModel(ABC):
    """Abstract base class for Activity Energy Expenditure strategies.

    Subclasses must set the class attribute ``name`` and implement
    ``calculate``. See the module docstring for the critical
    distinction between MET-based and PAL-ratio-based strategies
    before combining a subclass's output with other energy components.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed Activity Model"

    #: Whether this strategy's output already implicitly includes an
    #: average thermic effect of food (True for PAL-ratio-based
    #: strategies) or is a "pure" movement-cost estimate safe to
    #: combine with a separately-computed TEF (False for MET-based
    #: strategies). Every concrete subclass MUST set this explicitly
    #: -- it is not given a default, so that forgetting to declare it
    #: is a loud ``AttributeError`` rather than a silent, potentially
    #: wrong assumption baked into a simulation.
    includes_average_tef: bool

    @abstractmethod
    def calculate(self, person: Person, bmr_kcal: float) -> float:
        """Calculate Activity Energy Expenditure in kilocalories/day.

        Parameters
        ----------
        person:
            The subject. MET-based strategies primarily use
            ``person.weight_kg``; PAL-ratio-based strategies primarily
            use ``person.activity_level``.
        bmr_kcal:
            A pre-computed BMR/RMR figure, in kcal/day. Required by
            PAL-ratio-based strategies (AEE = BMR * (PAL - 1));
            accepted but unused by MET-based strategies, which derive
            AEE independently of BMR. Kept as a required parameter on
            every strategy for a uniform call signature across the
            registry.

        Returns
        -------
        float
            Estimated AEE, in kcal/day, net of BMR (i.e. the
            "extra" energy attributable to physical movement, not
            total expenditure during activity). Always non-negative.
        """
        raise NotImplementedError

    def __call__(self, person: Person, bmr_kcal: float) -> float:
        """Convenience alias: ``model(person, bmr_kcal)`` is equivalent
        to ``model.calculate(person, bmr_kcal)``."""
        return self.calculate(person, bmr_kcal)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
