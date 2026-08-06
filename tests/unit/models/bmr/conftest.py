"""Shared fixtures for metabosim.models.bmr unit tests."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person


@pytest.fixture
def male_no_bf() -> Person:
    """30-year-old male, 180cm, 80kg, body fat percentage unknown."""
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


@pytest.fixture
def female_no_bf() -> Person:
    """25-year-old female, 165cm, 60kg, body fat percentage unknown."""
    return Person(sex=Sex.FEMALE, age_years=25, height_cm=165, weight_kg=60)


@pytest.fixture
def male_with_bf() -> Person:
    """30-year-old male, 180cm, 80kg, 20% body fat -> 64kg lean mass."""
    return Person(
        sex=Sex.MALE,
        age_years=30,
        height_cm=180,
        weight_kg=80,
        body_fat_percent=20.0,
    )


@pytest.fixture
def female_with_bf() -> Person:
    """25-year-old female, 165cm, 60kg, 30% body fat -> 42kg lean mass."""
    return Person(
        sex=Sex.FEMALE,
        age_years=25,
        height_cm=165,
        weight_kg=60,
        body_fat_percent=30.0,
    )
