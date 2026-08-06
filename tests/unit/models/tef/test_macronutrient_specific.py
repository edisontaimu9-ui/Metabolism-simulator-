"""Unit tests for metabosim.models.tef.macronutrient_specific.

Reference values are hand-computed using the module's documented
formula:
    TEF = protein_energy*0.25 + (carb_energy+fiber_energy)*0.075
          + fat_energy*0.02 + alcohol_energy*0.20
"""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.macronutrient_specific import (
    THERMIC_FRACTION_ALCOHOL,
    THERMIC_FRACTION_CARBOHYDRATE,
    THERMIC_FRACTION_FAT,
    THERMIC_FRACTION_PROTEIN,
    MacronutrientSpecificTEF,
)


@pytest.mark.unit
class TestMacronutrientSpecificTEF:
    def test_name_is_set(self) -> None:
        assert MacronutrientSpecificTEF.name

    def test_documented_fraction_values(self) -> None:
        # These are the literature midpoints -- pin them explicitly so
        # an accidental edit to the module constants is caught here,
        # not just in an end-to-end reference-value test.
        assert THERMIC_FRACTION_PROTEIN == pytest.approx(0.25)
        assert THERMIC_FRACTION_CARBOHYDRATE == pytest.approx(0.075)
        assert THERMIC_FRACTION_FAT == pytest.approx(0.02)
        assert THERMIC_FRACTION_ALCOHOL == pytest.approx(0.20)

    def test_reference_value_mixed_diet(self, mixed_diet: MacronutrientGrams) -> None:
        # protein: 150*4=600 -> 600*0.25=150
        # carb+fiber: 300*4 + 30*2 = 1200+60=1260 -> 1260*0.075=94.5
        # fat: 80*9=720 -> 720*0.02=14.4
        # total = 150 + 94.5 + 14.4 = 258.9
        model = MacronutrientSpecificTEF()
        assert model.calculate(mixed_diet) == pytest.approx(258.9)

    def test_reference_value_with_alcohol(
        self, diet_with_alcohol: MacronutrientGrams
    ) -> None:
        # protein: 100*4=400 -> 400*0.25=100
        # carb: 200*4=800 -> 800*0.075=60
        # fat: 60*9=540 -> 540*0.02=10.8
        # alcohol: 40*7=280 -> 280*0.20=56
        # total = 100+60+10.8+56 = 226.8
        model = MacronutrientSpecificTEF()
        assert model.calculate(diet_with_alcohol) == pytest.approx(226.8)

    def test_zero_intake_gives_zero_tef(self, zero_intake: MacronutrientGrams) -> None:
        model = MacronutrientSpecificTEF()
        assert model.calculate(zero_intake) == pytest.approx(0.0)

    def test_tef_is_less_than_total_energy(
        self, mixed_diet: MacronutrientGrams
    ) -> None:
        model = MacronutrientSpecificTEF()
        tef = model.calculate(mixed_diet)
        assert 0.0 <= tef < mixed_diet.energy_kcal

    def test_protein_has_highest_thermic_cost_per_kcal(self) -> None:
        # Matched-calorie comparison: 400 kcal purely from protein vs
        # purely from fat should show protein produces more TEF,
        # consistent with Jequier & Tappy's reported ranges.
        model = MacronutrientSpecificTEF()
        protein_only = MacronutrientGrams(
            protein_g=100, carbohydrate_g=0, fat_g=0
        )  # 400 kcal
        fat_only = MacronutrientGrams(
            protein_g=0, carbohydrate_g=0, fat_g=400 / 9
        )  # ~400 kcal
        assert model.calculate(protein_only) > model.calculate(fat_only)
