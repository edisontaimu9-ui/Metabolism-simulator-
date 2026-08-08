"""Unit tests for metabosim.models.energy_balance.registry."""

import pytest

from metabosim.models.energy_balance.base import EnergyBalanceModel
from metabosim.models.energy_balance.dynamic_quasi_exponential import (
    DynamicQuasiExponentialModel,
)
from metabosim.models.energy_balance.registry import (
    get_model,
    list_models,
    register_model,
)
from metabosim.models.energy_balance.static_rule import StaticEnergyBalanceModel
from metabosim.models.energy_balance.tissue_energy_density import (
    TissueEnergyDensityModel,
)


@pytest.mark.unit
class TestListModels:
    def test_contains_all_built_in_models(self) -> None:
        expected = {
            "static_rule",
            "tissue_energy_density",
            "dynamic_quasi_exponential",
        }
        assert expected.issubset(set(list_models()))

    def test_returns_sorted_list(self) -> None:
        models = list_models()
        assert models == sorted(models)


@pytest.mark.unit
class TestGetModel:
    def test_get_static_rule(self) -> None:
        assert isinstance(get_model("static_rule"), StaticEnergyBalanceModel)

    def test_get_tissue_energy_density(self) -> None:
        assert isinstance(get_model("tissue_energy_density"), TissueEnergyDensityModel)

    def test_get_dynamic_quasi_exponential(self) -> None:
        assert isinstance(
            get_model("dynamic_quasi_exponential"), DynamicQuasiExponentialModel
        )

    def test_get_model_returns_fresh_instance_each_call(self) -> None:
        model_a = get_model("static_rule")
        model_b = get_model("static_rule")
        assert model_a is not model_b

    def test_unknown_model_id_raises_key_error_with_helpful_message(self) -> None:
        with pytest.raises(KeyError, match="static_rule"):
            get_model("does_not_exist")


@pytest.mark.unit
class TestRegisterModel:
    def test_register_custom_model_and_retrieve_it(self) -> None:
        class DummyEnergyBalanceModel(EnergyBalanceModel):
            name = "Dummy"
            includes_weight_dependent_feedback = False

            def mass_change_rate_kg_per_day(
                self, daily_energy_balance_kcal: float, excess_weight_kg: float = 0.0
            ) -> float:
                return daily_energy_balance_kcal / 5000.0

            def project_weight_change_kg(
                self, daily_energy_balance_kcal: float, days: float
            ) -> float:
                return (
                    self.mass_change_rate_kg_per_day(daily_energy_balance_kcal) * days
                )

        register_model("dummy_5000", DummyEnergyBalanceModel)
        assert "dummy_5000" in list_models()
        model = get_model("dummy_5000")
        assert isinstance(model, DummyEnergyBalanceModel)
