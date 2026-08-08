"""Shared fixtures for metabosim.simulation unit tests."""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.simulation.config import DailyPlan


@pytest.fixture
def moderate_male_80kg() -> Person:
    """30-year-old male, 180cm, 80kg. activity_level is irrelevant to
    the simulator (see metabosim.simulation.config docstring) but set
    for realism.
    """
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


@pytest.fixture
def jogging_plan() -> DailyPlan:
    """150g protein / 300g carb / 80g fat / 30g fiber, plus 1 hour of
    jogging at 6.0 MET. Total intake energy = 2580.0 kcal.
    """
    macros = MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30)
    entries = [ActivityEntry(met=6.0, duration_hours=1.0, label="jogging")]
    return DailyPlan(macros=macros, activity_entries=entries)


@pytest.fixture
def sedentary_maintenance_plan() -> DailyPlan:
    """A lower-calorie plan with no logged activity, intended to
    represent a caloric deficit scenario in engine-level tests."""
    macros = MacronutrientGrams(protein_g=100, carbohydrate_g=150, fat_g=40)
    return DailyPlan(macros=macros, activity_entries=[])
