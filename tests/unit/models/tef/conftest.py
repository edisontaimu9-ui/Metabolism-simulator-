"""Shared fixtures for metabosim.models.tef unit tests."""

import pytest

from metabosim.domain.diet import MacronutrientGrams


@pytest.fixture
def mixed_diet() -> MacronutrientGrams:
    """150g protein, 300g carb, 80g fat, 30g fiber, no alcohol.

    Total energy = 150*4 + 300*4 + 80*9 + 30*2 = 600+1200+720+60 = 2580
    """
    return MacronutrientGrams(
        protein_g=150,
        carbohydrate_g=300,
        fat_g=80,
        fiber_g=30,
    )


@pytest.fixture
def diet_with_alcohol() -> MacronutrientGrams:
    """100g protein, 200g carb, 60g fat, 0g fiber, 40g alcohol."""
    return MacronutrientGrams(
        protein_g=100,
        carbohydrate_g=200,
        fat_g=60,
        alcohol_g=40,
    )


@pytest.fixture
def zero_intake() -> MacronutrientGrams:
    return MacronutrientGrams.zero()
