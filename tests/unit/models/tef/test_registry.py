"""Unit tests for metabosim.models.tef.registry."""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.base import TEFModel
from metabosim.models.tef.fixed_percentage import FixedPercentageTEF
from metabosim.models.tef.macronutrient_specific import MacronutrientSpecificTEF
from metabosim.models.tef.registry import get_model, list_models, register_model


@pytest.mark.unit
class TestListModels:
    def test_contains_both_built_in_models(self) -> None:
        expected = {"macronutrient_specific", "fixed_percentage"}
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_macronutrient_specific(self) -> None:
        model = get_model("macronutrient_specific")
        assert isinstance(model, MacronutrientSpecificTEF)

    def test_get_fixed_percentage(self) -> None:
        model = get_model("fixed_percentage")
        assert isinstance(model, FixedPercentageTEF)

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("fixed_percentage")
        model_b = get_model("fixed_percentage")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="fixed_percentage"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyTEF(TEFModel):
            name = "Dummy"

            def calculate(self, macros: MacronutrientGrams) -> float:
                return macros.energy_kcal * 0.05

        register_model("dummy_five_percent", DummyTEF)
        assert "dummy_five_percent" in list_models()
        model = get_model("dummy_five_percent")
        assert isinstance(model, DummyTEF)
