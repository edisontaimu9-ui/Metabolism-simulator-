"""Unit tests for metabosim.domain.diet (MacronutrientGrams, DietPlan)."""

import pytest
from pydantic import ValidationError

from metabosim.domain.diet import DietPlan, MacronutrientGrams


@pytest.mark.unit
class TestMacronutrientGrams:
    def test_energy_kcal_known_value(self) -> None:
        # 100g protein, 200g carb, 50g fat, 20g fiber, 10g alcohol
        # = 100*4 + 200*4 + 50*9 + 20*2 + 10*7
        # = 400 + 800 + 450 + 40 + 70 = 1760
        macros = MacronutrientGrams(
            protein_g=100,
            carbohydrate_g=200,
            fat_g=50,
            fiber_g=20,
            alcohol_g=10,
        )
        assert macros.energy_kcal == pytest.approx(1760.0)

    def test_energy_kcal_no_fiber_or_alcohol(self) -> None:
        # 50g protein, 100g carb, 30g fat = 200 + 400 + 270 = 870
        macros = MacronutrientGrams(protein_g=50, carbohydrate_g=100, fat_g=30)
        assert macros.energy_kcal == pytest.approx(870.0)

    def test_zero_classmethod(self) -> None:
        macros = MacronutrientGrams.zero()
        assert macros.energy_kcal == 0.0

    def test_negative_values_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MacronutrientGrams(protein_g=-1, carbohydrate_g=100, fat_g=30)

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            MacronutrientGrams(
                protein_g=50,
                carbohydrate_g=100,
                fat_g=30,
                sugar_g=20,  # not a defined field
            )


@pytest.mark.unit
class TestDietPlan:
    def test_energy_kcal_delegates_to_macros(self) -> None:
        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=250, fat_g=70)
        plan = DietPlan(macros=macros, label="Baseline")
        assert plan.energy_kcal == pytest.approx(macros.energy_kcal)

    def test_meal_frequency_bounds(self) -> None:
        macros = MacronutrientGrams.zero()
        with pytest.raises(ValidationError):
            DietPlan(macros=macros, meal_frequency=0)
        with pytest.raises(ValidationError):
            DietPlan(macros=macros, meal_frequency=13)

    def test_valid_meal_frequency_accepted(self) -> None:
        macros = MacronutrientGrams.zero()
        plan = DietPlan(macros=macros, meal_frequency=3)
        assert plan.meal_frequency == 3

    def test_round_trip_json(self) -> None:
        # See the equivalent note in test_person.py: DietPlan.energy_kcal
        # and MacronutrientGrams.energy_kcal are computed fields, so a
        # full model_dump_json() cannot be fed straight back into
        # model_validate_json() under extra="forbid". Round-trip via
        # the declared input fields only, as a real deserializing
        # caller would.
        macros = MacronutrientGrams(protein_g=120, carbohydrate_g=300, fat_g=80)
        plan = DietPlan(macros=macros, label="Bulk", notes="Test plan")

        macro_input_fields = set(MacronutrientGrams.model_fields.keys())
        plan_input_fields = set(DietPlan.model_fields.keys())
        raw = plan.model_dump(mode="json", include=plan_input_fields)
        raw["macros"] = {
            k: v for k, v in raw["macros"].items() if k in macro_input_fields
        }
        restored = DietPlan.model_validate(raw)
        assert restored.macros.protein_g == 120
        assert restored.label == "Bulk"
