"""Unit tests for metabosim.models.energy_balance.base.EnergyBalanceModel."""

import pytest

from metabosim.models.energy_balance.base import EnergyBalanceModel


@pytest.mark.unit
class TestEnergyBalanceModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            EnergyBalanceModel()  # type: ignore[abstract]

    def test_subclass_missing_methods_cannot_be_instantiated(self) -> None:
        class IncompleteModel(EnergyBalanceModel):
            name = "Incomplete"
            includes_weight_dependent_feedback = False

        with pytest.raises(TypeError):
            IncompleteModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self) -> None:
        class FixedRateModel(EnergyBalanceModel):
            name = "Fixed rate"
            includes_weight_dependent_feedback = False

            def mass_change_rate_kg_per_day(
                self, daily_energy_balance_kcal: float, excess_weight_kg: float = 0.0
            ) -> float:
                return daily_energy_balance_kcal / 7700.0

            def project_weight_change_kg(
                self, daily_energy_balance_kcal: float, days: float
            ) -> float:
                return (
                    self.mass_change_rate_kg_per_day(daily_energy_balance_kcal) * days
                )

        model = FixedRateModel()
        assert model(-500.0) == pytest.approx(model.mass_change_rate_kg_per_day(-500.0))

    def test_repr_includes_name(self) -> None:
        class NamedModel(EnergyBalanceModel):
            name = "My Custom Energy Balance Model"
            includes_weight_dependent_feedback = True

            def mass_change_rate_kg_per_day(
                self, daily_energy_balance_kcal: float, excess_weight_kg: float = 0.0
            ) -> float:
                return 0.0

            def project_weight_change_kg(
                self, daily_energy_balance_kcal: float, days: float
            ) -> float:
                return 0.0

        assert "My Custom Energy Balance Model" in repr(NamedModel())

    def test_includes_weight_dependent_feedback_must_be_declared(self) -> None:
        class ForgetfulModel(EnergyBalanceModel):
            name = "Forgot the flag"

            def mass_change_rate_kg_per_day(
                self, daily_energy_balance_kcal: float, excess_weight_kg: float = 0.0
            ) -> float:
                return 0.0

            def project_weight_change_kg(
                self, daily_energy_balance_kcal: float, days: float
            ) -> float:
                return 0.0

        model = ForgetfulModel()
        with pytest.raises(AttributeError):
            _ = model.includes_weight_dependent_feedback
