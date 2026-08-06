"""Unit tests for metabosim.models.tef.fixed_percentage."""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.fixed_percentage import (
    FIXED_TEF_FRACTION,
    FixedPercentageTEF,
)


@pytest.mark.unit
class TestFixedPercentageTEF:
    def test_name_is_set(self) -> None:
        assert FixedPercentageTEF.name

    def test_documented_fraction_value(self) -> None:
        assert FIXED_TEF_FRACTION == pytest.approx(0.10)

    def test_reference_value_mixed_diet(self, mixed_diet: MacronutrientGrams) -> None:
        # total energy 2580.0 * 0.10 = 258.0
        model = FixedPercentageTEF()
        assert model.calculate(mixed_diet) == pytest.approx(258.0)

    def test_zero_intake_gives_zero_tef(self, zero_intake: MacronutrientGrams) -> None:
        model = FixedPercentageTEF()
        assert model.calculate(zero_intake) == pytest.approx(0.0)

    def test_ignores_macronutrient_composition(self) -> None:
        # By design, two diets with identical total energy but very
        # different composition must produce identical TEF under this
        # model -- this is exactly its documented limitation vs.
        # MacronutrientSpecificTEF, verified explicitly here.
        model = FixedPercentageTEF()
        high_protein = MacronutrientGrams(
            protein_g=100, carbohydrate_g=0, fat_g=0
        )  # 400 kcal
        high_fat = MacronutrientGrams(
            protein_g=0, carbohydrate_g=0, fat_g=400 / 9
        )  # ~400 kcal
        assert model.calculate(high_protein) == pytest.approx(model.calculate(high_fat))
