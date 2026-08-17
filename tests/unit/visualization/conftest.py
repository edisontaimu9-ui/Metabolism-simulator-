"""Shared fixtures and setup for metabosim.visualization unit tests.

Forces Matplotlib's non-interactive "Agg" backend before any test in
this directory imports ``matplotlib.pyplot`` (directly or via the
package under test), so the suite runs correctly in headless/CI
environments with no display available.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator


@pytest.fixture(autouse=True)
def _close_all_figures_after_test():
    """Prevent unbounded figure accumulation across the test session
    (Matplotlib keeps every created Figure alive until explicitly
    closed, which would otherwise leak memory across hundreds of
    tests)."""
    yield
    plt.close("all")


@pytest.fixture
def weight_only_states() -> list[SimulationState]:
    """A short simulation with no body composition or glycogen
    tracking (Phase 9-style)."""
    person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
    plan = DailyPlan(
        macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
    )
    config = SimulationConfig(days=10)
    return Simulator(person, config, plan).run()


@pytest.fixture
def full_tracking_states() -> list[SimulationState]:
    """A short simulation with body composition and glycogen tracking
    both active."""
    person = Person(
        sex=Sex.MALE,
        age_years=30,
        height_cm=180,
        weight_kg=80,
        body_fat_percent=20.0,
    )
    plan = DailyPlan(
        macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
    )
    config = SimulationConfig(days=10)
    return Simulator(person, config, plan, initial_glycogen_g=300.0).run()


@pytest.fixture
def person_with_bf() -> Person:
    return Person(
        sex=Sex.MALE,
        age_years=30,
        height_cm=180,
        weight_kg=80,
        body_fat_percent=20.0,
    )


@pytest.fixture
def person_without_bf() -> Person:
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
