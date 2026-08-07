"""Unit tests for metabosim.models.activity.registry."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.activity.base import ActivityModel
from metabosim.models.activity.iom_pal import IOMPALActivityModel
from metabosim.models.activity.met_based import ActivityEntry, METBasedActivityModel
from metabosim.models.activity.registry import get_model, list_models, register_model


@pytest.mark.unit
class TestListModels:
    def test_contains_both_built_in_models(self) -> None:
        expected = {"met_based", "iom_pal"}
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_iom_pal_no_kwargs_needed(self) -> None:
        model = get_model("iom_pal")
        assert isinstance(model, IOMPALActivityModel)

    def test_get_met_based_requires_entries_kwarg(self) -> None:
        entries = [ActivityEntry(met=5.0, duration_hours=1.0)]
        model = get_model("met_based", entries=entries)
        assert isinstance(model, METBasedActivityModel)
        assert model.entries == entries

    def test_get_met_based_without_entries_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            get_model("met_based")

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("iom_pal")
        model_b = get_model("iom_pal")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="iom_pal"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyActivityModel(ActivityModel):
            name = "Dummy"
            includes_average_tef = False

            def calculate(self, person: Person, bmr_kcal: float) -> float:
                return 42.0

        register_model("dummy_fixed", DummyActivityModel)
        assert "dummy_fixed" in list_models()
        model = get_model("dummy_fixed")
        assert isinstance(model, DummyActivityModel)
