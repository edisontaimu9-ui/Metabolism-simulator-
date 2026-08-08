"""Unit tests for metabosim.models.body_composition.registry."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.models.body_composition.base import BodyCompositionModel
from metabosim.models.body_composition.forbes import ForbesPartitionModel
from metabosim.models.body_composition.registry import (
    get_model,
    list_models,
    register_model,
)


@pytest.mark.unit
class TestListModels:
    def test_contains_built_in_model(self) -> None:
        assert "forbes" in list_models()

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_forbes(self) -> None:
        assert isinstance(get_model("forbes"), ForbesPartitionModel)

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("forbes")
        model_b = get_model("forbes")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="forbes"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyBodyCompositionModel(BodyCompositionModel):
            name = "Dummy"

            def ffm_fraction_of_change(
                self, current_fat_mass_kg: float, sex: Sex
            ) -> float:
                return 0.5

        register_model("dummy_half", DummyBodyCompositionModel)
        assert "dummy_half" in list_models()
        model = get_model("dummy_half")
        assert isinstance(model, DummyBodyCompositionModel)
