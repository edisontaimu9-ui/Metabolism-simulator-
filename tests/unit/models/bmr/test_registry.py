"""Unit tests for metabosim.models.bmr.registry."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel
from metabosim.models.bmr.cunningham import CunninghamBMR
from metabosim.models.bmr.registry import get_model, list_models, register_model


@pytest.mark.unit
class TestListModels:
    def test_contains_all_four_built_in_models(self) -> None:
        expected = {
            "mifflin_st_jeor",
            "harris_benedict",
            "katch_mcardle",
            "cunningham",
        }
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_model_by_id_returns_correct_type(self) -> None:
        model = get_model("mifflin_st_jeor")
        from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR

        assert isinstance(model, MifflinStJeorBMR)

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("cunningham")
        model_b = get_model("cunningham")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="Unknown BMR model id"):
            get_model("not_a_real_model")

    def test_get_model_result_is_usable(self, male_no_bf: Person) -> None:
        model = get_model("mifflin_st_jeor")
        assert model.calculate(male_no_bf) > 0


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_becomes_retrievable(self) -> None:
        class _ExperimentalBMR(BMRModel):
            name = "Experimental"
            requires_body_fat = False

            def calculate(self, person: Person) -> float:
                return 9999.0

        register_model("experimental_test_only", _ExperimentalBMR)
        try:
            assert "experimental_test_only" in list_models()
            model = get_model("experimental_test_only")
            assert isinstance(model, _ExperimentalBMR)
        finally:
            # Registry is module-level, process-global state -- clean
            # up so this test does not leak into other tests/sessions.
            from metabosim.models.bmr.registry import _REGISTRY

            _REGISTRY.pop("experimental_test_only", None)

    def test_register_overwrites_existing_id(self) -> None:
        original = get_model("cunningham")
        assert isinstance(original, CunninghamBMR)

        class _ReplacementBMR(BMRModel):
            name = "Replacement"
            requires_body_fat = False

            def calculate(self, person: Person) -> float:
                return 1.0

        register_model("cunningham", _ReplacementBMR)
        try:
            replaced = get_model("cunningham")
            assert isinstance(replaced, _ReplacementBMR)
        finally:
            # Restore the real registration so this test does not
            # leak state into other tests (registry is module-level,
            # process-global state).
            register_model("cunningham", CunninghamBMR)
