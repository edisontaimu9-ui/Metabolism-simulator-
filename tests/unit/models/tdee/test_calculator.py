"""Unit tests for metabosim.models.tdee.calculator.calculate_tdee.

These are integration-style tests within the unit tier: they exercise
the composition of two registries (bmr + tdee) together, but remain
fast and dependency-free, so they stay under tests/unit rather than
tests/integration.
"""

import pytest

from metabosim.domain.enums import ActivityLevel, Sex
from metabosim.domain.person import Person
from metabosim.models.tdee.calculator import (
    DEFAULT_BMR_MODEL_ID,
    DEFAULT_TDEE_MODEL_ID,
    TDEEResult,
    calculate_tdee,
)


@pytest.mark.unit
class TestCalculateTDEEDefaults:
    def test_default_model_ids_are_registered(self) -> None:
        from metabosim.models.bmr.registry import list_models as list_bmr_models
        from metabosim.models.tdee.registry import list_models as list_tdee_models

        assert DEFAULT_BMR_MODEL_ID in list_bmr_models()
        assert DEFAULT_TDEE_MODEL_ID in list_tdee_models()

    def test_default_wiring_reference_value(self, moderate_male: Person) -> None:
        # Mifflin-St Jeor BMR (1780.0) x moderate multiplier (1.55)
        # = 2759.0
        result = calculate_tdee(moderate_male)
        assert result.bmr_kcal == pytest.approx(1780.0)
        assert result.tdee_kcal == pytest.approx(2759.0)

    def test_result_is_frozen(self, moderate_male: Person) -> None:
        from pydantic import ValidationError

        result = calculate_tdee(moderate_male)
        with pytest.raises(ValidationError):
            result.tdee_kcal = 9999.0  # type: ignore[misc]

    def test_result_reports_model_names(self, moderate_male: Person) -> None:
        result = calculate_tdee(moderate_male)
        assert "Mifflin-St Jeor" in result.bmr_model_name
        assert "PAL Multiplier" in result.tdee_model_name


@pytest.mark.unit
class TestCalculateTDEEExplicitModelSelection:
    def test_explicit_bmr_model_selection(self) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
            activity_level=ActivityLevel.SEDENTARY,
        )
        result_default = calculate_tdee(person, bmr_model_id="mifflin_st_jeor")
        result_katch = calculate_tdee(person, bmr_model_id="katch_mcardle")
        # Different equations should (generally) produce different BMR
        # figures for the same person -- confirms the model_id is
        # actually being respected, not silently ignored.
        assert result_default.bmr_kcal != result_katch.bmr_kcal
        assert result_default.bmr_model_id == "mifflin_st_jeor"
        assert result_katch.bmr_model_id == "katch_mcardle"

    def test_unknown_bmr_model_id_raises(self, moderate_male: Person) -> None:
        with pytest.raises(KeyError):
            calculate_tdee(moderate_male, bmr_model_id="not_a_real_model")

    def test_unknown_tdee_model_id_raises(self, moderate_male: Person) -> None:
        with pytest.raises(KeyError):
            calculate_tdee(moderate_male, tdee_model_id="not_a_real_model")

    def test_lean_mass_model_without_body_fat_raises_clear_error(
        self, moderate_male: Person
    ) -> None:
        # moderate_male fixture has no body_fat_percent set.
        with pytest.raises(ValueError, match="body_fat_percent"):
            calculate_tdee(moderate_male, bmr_model_id="katch_mcardle")


@pytest.mark.unit
class TestTDEEResultShape:
    def test_all_fields_present(self, moderate_male: Person) -> None:
        result = calculate_tdee(moderate_male)
        assert isinstance(result, TDEEResult)
        assert result.bmr_kcal > 0
        assert result.tdee_kcal >= result.bmr_kcal
        assert result.bmr_model_id
        assert result.bmr_model_name
        assert result.tdee_model_id
        assert result.tdee_model_name
