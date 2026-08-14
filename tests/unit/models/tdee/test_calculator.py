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


@pytest.mark.unit
class TestCalculateTDEEFromComponents:
    """Tests for calculate_tdee_from_components, the Phase 7 function
    that composes BMR + Activity + TEF independently, resolving the
    double-counting caveat flagged in Phases 5 and 6.
    """

    def test_reference_value_with_met_based_activity(
        self, moderate_male: Person
    ) -> None:
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.activity import ActivityEntry
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(
            protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30
        )
        entries = [ActivityEntry(met=6.0, duration_hours=1.0, label="jogging")]

        result = calculate_tdee_from_components(
            moderate_male,
            macros,
            activity_model_kwargs={"entries": entries},
        )

        # BMR: 1780.0 (Mifflin-St Jeor)
        # Activity: (6-1)*80*1 = 400.0
        # TEF: 150*4*0.25 + (300*4+30*2)*0.075 + 80*9*0.02 = 258.9
        # TDEE: 1780 + 400 + 258.9 = 2438.9
        assert result.bmr_kcal == pytest.approx(1780.0)
        assert result.activity_kcal == pytest.approx(400.0)
        assert result.tef_kcal == pytest.approx(258.9)
        assert result.tdee_kcal == pytest.approx(2438.9)

    def test_components_sum_to_tdee(self, moderate_male: Person) -> None:
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.activity import ActivityEntry
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        entries = [ActivityEntry(met=4.0, duration_hours=1.5)]

        result = calculate_tdee_from_components(
            moderate_male, macros, activity_model_kwargs={"entries": entries}
        )
        assert result.tdee_kcal == pytest.approx(
            result.bmr_kcal + result.activity_kcal + result.tef_kcal
        )

    def test_empty_activity_log_still_works(self, moderate_male: Person) -> None:
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        result = calculate_tdee_from_components(
            moderate_male, macros, activity_model_kwargs={"entries": []}
        )
        assert result.activity_kcal == pytest.approx(0.0)
        assert result.tdee_kcal == pytest.approx(result.bmr_kcal + result.tef_kcal)

    def test_iom_pal_activity_model_rejected_with_clear_error(
        self, moderate_male: Person
    ) -> None:
        # This is the core safety guarantee of this function: using an
        # activity model that already bundles an average TEF must
        # raise, not silently double-count.
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        with pytest.raises(ValueError, match="double-count"):
            calculate_tdee_from_components(
                moderate_male, macros, activity_model_id="iom_pal"
            )

    def test_unknown_tef_model_id_raises(self, moderate_male: Person) -> None:
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        with pytest.raises(KeyError):
            calculate_tdee_from_components(
                moderate_male,
                macros,
                activity_model_kwargs={"entries": []},
                tef_model_id="not_a_real_model",
            )

    def test_result_is_frozen(self, moderate_male: Person) -> None:
        from pydantic import ValidationError

        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.tdee.calculator import calculate_tdee_from_components

        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        result = calculate_tdee_from_components(
            moderate_male, macros, activity_model_kwargs={"entries": []}
        )
        with pytest.raises(ValidationError):
            result.tdee_kcal = 9999.0  # type: ignore[misc]

    def test_default_activity_model_is_met_based(self, moderate_male: Person) -> None:
        from metabosim.models.tdee.calculator import DEFAULT_ACTIVITY_MODEL_ID

        assert DEFAULT_ACTIVITY_MODEL_ID == "met_based"


@pytest.mark.unit
class TestCalculateTDEEAcceptsPrebuiltBMRModel:
    """Tests for Phase 14's extension: bmr_model_id may be a pre-built
    BMRModel instance (e.g. a DiseaseModifiedBMRModel), not only a
    registry string ID.
    """

    def test_calculate_tdee_accepts_prebuilt_model(self, moderate_male: Person) -> None:
        from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR
        from metabosim.models.disease import (
            DiseaseModifiedBMRModel,
            ThyroidModifier,
            ThyroidStatus,
        )
        from metabosim.models.tdee.calculator import CUSTOM_BMR_MODEL_ID, calculate_tdee

        disease_model = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(),
            [ThyroidModifier(status=ThyroidStatus.MODERATE_HYPOTHYROID)],
        )
        result = calculate_tdee(moderate_male, bmr_model_id=disease_model)
        # 1780 * 0.8 = 1424.0
        assert result.bmr_kcal == pytest.approx(1424.0)
        assert result.bmr_model_id == CUSTOM_BMR_MODEL_ID
        assert "Thyroid Dysfunction" in result.bmr_model_name

    def test_calculate_tdee_from_components_accepts_prebuilt_model(
        self, moderate_male: Person
    ) -> None:
        from metabosim.domain.diet import MacronutrientGrams
        from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR
        from metabosim.models.disease import (
            DiseaseModifiedBMRModel,
            ThyroidModifier,
            ThyroidStatus,
        )
        from metabosim.models.tdee.calculator import (
            CUSTOM_BMR_MODEL_ID,
            calculate_tdee_from_components,
        )

        disease_model = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(),
            [ThyroidModifier(status=ThyroidStatus.MODERATE_HYPOTHYROID)],
        )
        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        result = calculate_tdee_from_components(
            moderate_male,
            macros,
            bmr_model_id=disease_model,
            activity_model_kwargs={"entries": []},
        )
        assert result.bmr_kcal == pytest.approx(1424.0)
        assert result.bmr_model_id == CUSTOM_BMR_MODEL_ID

    def test_string_bmr_model_id_still_reports_its_own_id(
        self, moderate_male: Person
    ) -> None:
        # Backward-compatibility check: passing a string must continue
        # to report that exact string, not "custom".
        from metabosim.models.tdee.calculator import calculate_tdee

        result = calculate_tdee(moderate_male, bmr_model_id="harris_benedict")
        assert result.bmr_model_id == "harris_benedict"

    def test_stacked_disease_modifiers_via_prebuilt_model(
        self, moderate_male: Person
    ) -> None:
        from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR
        from metabosim.models.disease import (
            BodyTemperatureModifier,
            DiseaseModifiedBMRModel,
            ThyroidModifier,
            ThyroidStatus,
        )
        from metabosim.models.tdee.calculator import calculate_tdee

        disease_model = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(),
            [
                ThyroidModifier(status=ThyroidStatus.MODERATE_HYPOTHYROID),
                BodyTemperatureModifier(body_temperature_c=39.0),
            ],
        )
        result = calculate_tdee(moderate_male, bmr_model_id=disease_model)
        # 1780 * 0.8 * 1.26 = 1794.24
        assert result.bmr_kcal == pytest.approx(1794.24)
