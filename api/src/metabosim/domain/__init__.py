"""
metabosim.domain
=================

Pure data layer of the simulation engine.

Contains Pydantic-based domain models (e.g. ``Person``, ``DietPlan``,
``SimulationState``) and enumerations (``Sex``, ``ActivityLevel``,
``UnitSystem``). This package has NO dependencies on any other
``metabosim`` subpackage and performs no calculations of its own --
it exists purely to define validated, well-typed data structures that
every other layer consumes.

Rationale: keeping domain models dependency-free ensures they can be
imported by every model strategy, the simulation engine, and the
reporting layer without risk of circular imports.

Public API
----------
This package re-exports its stable, commonly-used names at the top
level so downstream code can write::

    from metabosim.domain import Person, Sex, ActivityLevel

rather than reaching into individual submodules. Submodules
(``metabosim.domain.constants``, ``metabosim.domain.units``) remain
directly importable for callers that specifically need conversion
helpers or raw constants.
"""

from metabosim.domain.diet import DietPlan, MacronutrientGrams
from metabosim.domain.enums import ActivityLevel, Sex, UnitSystem
from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState

__all__ = [
    "ActivityLevel",
    "DietPlan",
    "MacronutrientGrams",
    "Person",
    "Sex",
    "SimulationState",
    "UnitSystem",
]
