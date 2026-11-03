"""Shared fixtures for metabosim.reports unit tests."""

from __future__ import annotations

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.reports.data import ReportData, build_report_data
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator

_MACROS = MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)


@pytest.fixture
def basic_data() -> ReportData:
    """Weight-only run (no body fat, no glycogen), no activity."""
    person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
    sim = Simulator(person, SimulationConfig(days=10), DailyPlan(macros=_MACROS))
    return build_report_data(sim, sim.run())


@pytest.fixture
def full_data() -> ReportData:
    """Full tracking, a named subject, logged activity, 60 days."""
    person = Person(
        name="Test | *User*",
        sex=Sex.FEMALE,
        age_years=40,
        height_cm=165,
        weight_kg=70,
        body_fat_percent=30.0,
    )
    plan = DailyPlan(
        macros=_MACROS,
        activity_entries=[ActivityEntry(met=6.0, duration_hours=1.0, label="Run")],
    )
    config = SimulationConfig(
        days=60,
        adaptive_thermogenesis_model_id="proportional",
    )
    sim = Simulator(person, config, plan, initial_glycogen_g=400.0)
    return build_report_data(sim, sim.run())


@pytest.fixture
def varying_data() -> ReportData:
    """A run whose plan changes day to day."""
    person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
    plans = [
        DailyPlan(
            macros=MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=50)
        ),
        DailyPlan(
            macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
        ),
        DailyPlan(
            macros=MacronutrientGrams(protein_g=120, carbohydrate_g=250, fat_g=60)
        ),
    ]
    sim = Simulator(person, SimulationConfig(days=3), plans)
    return build_report_data(sim, sim.run())
