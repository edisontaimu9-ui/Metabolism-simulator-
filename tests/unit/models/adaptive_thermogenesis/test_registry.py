"""Unit tests for metabosim.models.adaptive_thermogenesis.registry."""

import pytest

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.none import NoAdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.proportional import (
    ProportionalAdaptiveThermogenesisModel,
)
from metabosim.models.adaptive_thermogenesis.registry import (
    get_model,
    list_models,
    register_model,
)
from metabosim.models.adaptive_thermogenesis.threshold import (
    ThresholdAdaptiveThermogenesisModel,
)


@pytest.mark.unit
class TestListModels:
    def test_contains_all_built_in_models(self) -> None:
        expected = {"none", "threshold", "proportional"}
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_none(self) -> None:
        assert isinstance(get_model("none"), NoAdaptiveThermogenesisModel)

    def test_get_threshold(self) -> None:
        assert isinstance(get_model("threshold"), ThresholdAdaptiveThermogenesisModel)

    def test_get_proportional(self) -> None:
        assert isinstance(
            get_model("proportional"), ProportionalAdaptiveThermogenesisModel
        )

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("none")
        model_b = get_model("none")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="none"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyAdaptationModel(AdaptiveThermogenesisModel):
            name = "Dummy"

            def calculate_adjustment_kcal(
                self,
                baseline_weight_kg: float,
                current_weight_kg: float,
                reference_expenditure_kcal: float,
            ) -> float:
                return -50.0

        register_model("dummy_fixed_negative", DummyAdaptationModel)
        assert "dummy_fixed_negative" in list_models()
        model = get_model("dummy_fixed_negative")
        assert isinstance(model, DummyAdaptationModel)
