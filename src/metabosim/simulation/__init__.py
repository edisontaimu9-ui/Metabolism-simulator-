"""
metabosim.simulation
=====================

Orchestration layer. Owns the time-stepping simulation engine that
composes model strategies from ``metabosim.models`` into a coherent
day-by-day (or arbitrary-timestep) simulation of a subject's energy
metabolism and body composition.

Key responsibilities (implemented in later phases):
  - ``engine.py``   The ``Simulator`` class: runs a configured simulation
                     across a time horizon and records state history.
  - ``stepper.py``  Single-timestep state transition logic (pure function
                     of current state + models -> next state).
  - ``config.py``   ``SimulationConfig`` -- declarative configuration for
                     which model strategies to use, timestep size, horizon.

This package depends on ``metabosim.domain`` and ``metabosim.models``,
but nothing downstream (analysis/visualization/reports) depends on it
in reverse -- data flows strictly forward in time and up the stack.
"""
