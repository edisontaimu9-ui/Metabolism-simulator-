"""Unit tests for metabosim.models.tdee.registry."""

import pytest

from metabosim.models.tdee.base import TDEEModel
from metabosim.models.tdee.pal_multiplier import PALMultiplierTDEE
from metabosim.models.tdee.registry import get_model, list_models, register_model


@pytest.mark.unit
class TestListModels:
    def test_contains_built_in_model(self) -> None:
        assert "pal_multiplier" in list_models()

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_model_by_id_returns_correct_type(self) -> None:
        model = get_model("pal_multiplier")
        assert isinstance(model, PALMultiplierTDEE)

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("pal_multiplier")
        model_b = get_model("pal_multiplier")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="pal_multiplier"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyTDEE(TDEEModel):
            name = "Dummy"

            def calculate(self, person: object, bmr_kcal: float) -> float:
                return bmr_kcal * 2.0

        register_model("dummy_double", DummyTDEE)
        assert "dummy_double" in list_models()
        model = get_model("dummy_double")
        assert isinstance(model, DummyTDEE)
