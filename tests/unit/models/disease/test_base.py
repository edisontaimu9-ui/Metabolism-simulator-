"""Unit tests for metabosim.models.disease.base."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR
from metabosim.models.disease.base import DiseaseModifiedBMRModel, DiseaseModifier


@pytest.fixture
def person() -> Person:
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


class _AddFixedKcal(DiseaseModifier):
    """Test double: adds a fixed kcal amount, for isolating composer
    logic from any specific real modifier's math."""

    def __init__(self, amount: float, name: str = "Fixed Addition") -> None:
        self.amount = amount
        self.name = name

    def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
        return base_bmr_kcal + self.amount


@pytest.mark.unit
class TestDiseaseModifierInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            DiseaseModifier()  # type: ignore[abstract]

    def test_subclass_missing_method_cannot_be_instantiated(self) -> None:
        class IncompleteModifier(DiseaseModifier):
            name = "Incomplete"

        with pytest.raises(TypeError):
            IncompleteModifier()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self, person: Person) -> None:
        modifier = _AddFixedKcal(100.0)
        assert modifier(1000.0, person) == pytest.approx(
            modifier.apply_to_bmr_kcal(1000.0, person)
        )

    def test_repr_includes_name(self) -> None:
        modifier = _AddFixedKcal(50.0, name="My Custom Modifier")
        assert "My Custom Modifier" in repr(modifier)


@pytest.mark.unit
class TestDiseaseModifiedBMRModelConstruction:
    def test_empty_modifiers_list_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            DiseaseModifiedBMRModel(MifflinStJeorBMR(), [])

    def test_name_includes_base_and_modifier_names(self) -> None:
        model = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(), [_AddFixedKcal(50.0, name="Test Modifier")]
        )
        assert "Mifflin-St Jeor" in model.name
        assert "Test Modifier" in model.name

    def test_inherits_requires_body_fat_from_base_model(self) -> None:
        from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR

        model = DiseaseModifiedBMRModel(KatchMcArdleBMR(), [_AddFixedKcal(50.0)])
        assert model.requires_body_fat is True

        model2 = DiseaseModifiedBMRModel(MifflinStJeorBMR(), [_AddFixedKcal(50.0)])
        assert model2.requires_body_fat is False


@pytest.mark.unit
class TestDiseaseModifiedBMRModelCalculation:
    def test_single_modifier_applied(self, person: Person) -> None:
        model = DiseaseModifiedBMRModel(MifflinStJeorBMR(), [_AddFixedKcal(100.0)])
        # base Mifflin-St Jeor for this person is 1780.0
        assert model.calculate(person) == pytest.approx(1880.0)

    def test_multiple_modifiers_applied_in_order(self, person: Person) -> None:
        model = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(),
            [_AddFixedKcal(100.0), _AddFixedKcal(50.0)],
        )
        # 1780 + 100 + 50 = 1930
        assert model.calculate(person) == pytest.approx(1930.0)

    def test_order_matters_for_multiplicative_modifiers(self, person: Person) -> None:
        class _Multiply(DiseaseModifier):
            def __init__(self, factor: float) -> None:
                self.factor = factor
                self.name = f"Multiply x{factor}"

            def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
                return base_bmr_kcal * self.factor

        # (1780 + 100) * 2 = 3760
        model_a = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(), [_AddFixedKcal(100.0), _Multiply(2.0)]
        )
        # (1780 * 2) + 100 = 3660
        model_b = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(), [_Multiply(2.0), _AddFixedKcal(100.0)]
        )
        assert model_a.calculate(person) != model_b.calculate(person)
        assert model_a.calculate(person) == pytest.approx(3760.0)
        assert model_b.calculate(person) == pytest.approx(3660.0)

    def test_is_substitutable_as_a_bmr_model(self, person: Person) -> None:
        # The core Decorator-pattern promise: this composed model must
        # work anywhere a plain BMRModel works, via the same interface.
        from metabosim.models.bmr.base import BMRModel

        model: BMRModel = DiseaseModifiedBMRModel(
            MifflinStJeorBMR(), [_AddFixedKcal(0.0)]
        )
        assert isinstance(model, BMRModel)
        assert model.calculate(person) == pytest.approx(1780.0)
        assert model(person) == pytest.approx(model.calculate(person))
