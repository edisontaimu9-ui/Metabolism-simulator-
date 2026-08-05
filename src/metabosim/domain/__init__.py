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
"""
