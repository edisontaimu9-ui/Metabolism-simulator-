"""
metabosim.models.activity.met_based
======================================

MET (Metabolic Equivalent of Task) based Activity Energy Expenditure
model -- a bottom-up estimate built from a logged diary of specific
activities, each with a published MET value and duration.

Definitions and formula
------------------------
One MET is conventionally defined as the energy cost of sitting
quietly, standardized (by convention, not as a literal universal
constant) to **1 kcal per kilogram of body weight per hour**. Source:
Jette M, Sidney K, Blumchen G. "Metabolic equivalents (METS) in
exercise testing, exercise prescription, and evaluation of functional
capacity." *Clin Cardiol.* 1990;13(8):555-565.

Gross energy expenditure during an activity of a given MET value,
body weight, and duration:

    gross_kcal = MET * weight_kg * duration_hours

Net (activity-only) energy expenditure -- the portion attributable to
the movement itself, above what would have been expended at rest for
the same duration:

    net_kcal = (MET - 1) * weight_kg * duration_hours

``ActivityEntry.net_energy_kcal`` and this module's
``METBasedActivityModel`` use the **net** formula, since AEE (Activity
Energy Expenditure) is defined, throughout this codebase, as energy
*above* BMR -- see ``metabosim.models.activity.base`` module
docstring. The gross formula is also exposed
(``ActivityEntry.gross_energy_kcal``) for completeness and for callers
who want total energy expended during a specific activity (e.g. for
a workout log display), not for composing into a TDEE breakdown.

MET values themselves (which specific activities correspond to which
MET value) come from the Compendium of Physical Activities:
Ainsworth BE, Haskell WL, Herrmann SD, et al. "2011 Compendium of
Physical Activities: a second update of codes and MET values."
*Med Sci Sports Exerc.* 2011;43(8):1575-1581. This module does not
hard-code a lookup table of activity-name -> MET value (the
Compendium contains hundreds of entries and is a licensed/maintained
external dataset); callers supply the MET value directly per
``ActivityEntry``, sourced from the Compendium or an equivalent
reference.

Why this is the strategy that resolves the Phase 5/6 double-counting
caveat
---------------------------------------------------------------------
MET values are derived from indirect calorimetry measuring the O2 cost
of specific movements -- a measurement paradigm entirely independent
of food intake or digestion. A MET-based net AEE figure therefore has
no thermic-effect-of-food component baked into it, unlike a PAL-ratio-
based estimate (see ``metabosim.models.activity.iom_pal``). This is
why ``METBasedActivityModel.includes_average_tef`` is ``False``,
and why it is the strategy
``metabosim.models.tdee.calculator.calculate_tdee_from_components``
uses to safely combine with an independently-computed TEF.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from metabosim.domain.person import Person
from metabosim.models.activity.base import ActivityModel

#: Kilocalories per kilogram of body weight per hour represented by
#: one MET, by convention. See module docstring for citation.
KCAL_PER_KG_PER_HOUR_PER_MET: float = 1.0


class ActivityEntry(BaseModel):
    """A single logged activity: a MET value sustained for a duration.

    Attributes
    ----------
    met:
        The Metabolic Equivalent of Task value for this activity,
        typically sourced from the Compendium of Physical Activities
        (Ainsworth et al., 2011). Must be positive; a MET of exactly
        1.0 represents quiet sitting (zero *net* activity cost).
    duration_hours:
        How long this activity was sustained, in hours. Must be
        positive.
    label:
        Optional human-readable description (e.g. "brisk walking",
        "cycling, moderate effort"), for report readability. Not used
        in any calculation.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    met: float = Field(..., gt=0.0)
    duration_hours: float = Field(..., gt=0.0)
    label: str | None = Field(default=None, max_length=200)

    def gross_energy_kcal(self, weight_kg: float) -> float:
        """Total energy expended during this activity, including the
        resting-equivalent baseline (MET x weight_kg x duration_hours).
        """
        return self.met * weight_kg * self.duration_hours

    def net_energy_kcal(self, weight_kg: float) -> float:
        """Energy expended during this activity *above* what would
        have been expended at rest for the same duration:
        (MET - 1) x weight_kg x duration_hours.

        This is the figure used when composing Activity Energy
        Expenditure into a BMR + AEE + TEF breakdown -- see module
        docstring.
        """
        return (self.met - 1.0) * weight_kg * self.duration_hours


class METBasedActivityModel(ActivityModel):
    """Sums the net energy cost of a logged list of ``ActivityEntry``
    objects to produce total daily Activity Energy Expenditure.

    ``bmr_kcal`` is accepted (for interface conformance with
    ``ActivityModel``) but is not used in this calculation -- AEE is
    derived entirely from the activity log and the subject's body
    weight, independent of BMR. See module docstring for the full
    rationale and citations.
    """

    name = "MET-Based Activity Log (Ainsworth Compendium, 2011)"
    includes_average_tef = False

    def __init__(self, entries: list[ActivityEntry]) -> None:
        """
        Parameters
        ----------
        entries:
            The subject's logged activities for the period being
            evaluated (typically one day). May be empty (representing
            a fully sedentary day with zero net activity cost).
        """
        self.entries = entries

    @property
    def total_duration_hours(self) -> float:
        """Convenience: total logged duration across all entries, in
        hours. Not itself a required part of the ``ActivityModel``
        interface; exposed for report/sanity-check purposes (e.g.
        flagging an implausible >24h/day log)."""
        return sum(entry.duration_hours for entry in self.entries)

    def calculate(self, person: Person, bmr_kcal: float) -> float:
        del bmr_kcal  # unused by this strategy; see class docstring.
        return sum(entry.net_energy_kcal(person.weight_kg) for entry in self.entries)
