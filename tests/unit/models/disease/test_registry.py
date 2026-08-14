"""Unit tests for metabosim.models.disease.registry."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.disease.base import DiseaseModifier
from metabosim.models.disease.body_temperature import BodyTemperatureModifier
from metabosim.models.disease.registry import get_model, list_models, register_model
from metabosim.models.disease.thyroid import ThyroidModifier, ThyroidStatus


@pytest.mark.unit
class TestListModels:
    def test_contains_both_built_in_models(self) -> None:
        expected = {"thyroid", "body_temperature"}
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_thyroid_with_status_kwarg(self) -> None:
        modifier = get_model("thyroid", status=ThyroidStatus.MILD_HYPERTHYROID)
        assert isinstance(modifier, ThyroidModifier)
        assert modifier.status == ThyroidStatus.MILD_HYPERTHYROID

    def test_get_thyroid_without_kwargs_uses_default(self) -> None:
        modifier = get_model("thyroid")
        assert isinstance(modifier, ThyroidModifier)
        assert modifier.status == ThyroidStatus.EUTHYROID

    def test_get_body_temperature_requires_kwarg(self) -> None:
        modifier = get_model("body_temperature", body_temperature_c=39.0)
        assert isinstance(modifier, BodyTemperatureModifier)
        assert modifier.body_temperature_c == pytest.approx(39.0)

    def test_get_body_temperature_without_required_kwarg_raises_type_error(
        self,
    ) -> None:
        with pytest.raises(TypeError):
            get_model("body_temperature")

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("body_temperature", body_temperature_c=39.0)
        model_b = get_model("body_temperature", body_temperature_c=39.0)
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="thyroid"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyDiseaseModifier(DiseaseModifier):
            name = "Dummy"

            def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
                return base_bmr_kcal * 1.05

        register_model("dummy_five_percent", DummyDiseaseModifier)
        assert "dummy_five_percent" in list_models()
        modifier = get_model("dummy_five_percent")
        assert isinstance(modifier, DummyDiseaseModifier)
        person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
        assert modifier.apply_to_bmr_kcal(1000.0, person) == pytest.approx(1050.0)
