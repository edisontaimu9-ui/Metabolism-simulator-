"""Shared fixtures for metabosim.models.activity unit tests."""

import pytest

from metabosim.domain.enums import ActivityLevel, Sex
from metabosim.domain.person import Person


@pytest.fixture
def sedentary_male_80kg() -> Person:
    """30-year-old male, 180cm, 80kg, sedentary."""
    return Person(
        sex=Sex.MALE,
        age_years=30,
        height_cm=180,
        weight_kg=80,
        activity_level=ActivityLevel.SEDENTARY,
    )


@pytest.fixture
def moderate_male_80kg() -> Person:
    """30-year-old male, 180cm, 80kg, moderately active."""
    return Person(
        sex=Sex.MALE,
        age_years=30,
        height_cm=180,
        weight_kg=80,
        activity_level=ActivityLevel.MODERATE,
    )


@pytest.fixture
def light_female_60kg() -> Person:
    """25-year-old female, 165cm, 60kg, lightly active."""
    return Person(
        sex=Sex.FEMALE,
        age_years=25,
        height_cm=165,
        weight_kg=60,
        activity_level=ActivityLevel.LIGHT,
    )
