"""Unit tests for metabosim.models.energy_balance.static_rule.

Reference values hand-computed: rate = balance / 7716.18 kcal/kg,
where 7716.18 = 3500 kcal/lb / 0.45359237 kg/lb.
"""

import pytest

from metabosim.models.energy_balance.static_rule import (
    ENERGY_DENSITY_KCAL_PER_KG,
    WISHNOFSKY_KCAL_PER_LB,
    StaticEnergyBalanceModel,
)


@pytest.mark.unit
class TestStaticRuleConstants:
    def test_wishnofsky_constant(self) -> None:
        assert WISHNOFSKY_KCAL_PER_LB == pytest.approx(3500.0)

    def test_energy_density_kcal_per_kg(self) -> None:
        # 3500 / 0.45359237 ~= 7716.18
        assert ENERGY_DENSITY_KCAL_PER_KG == pytest.approx(7716.18, abs=0.01)


@pytest.mark.unit
class TestStaticEnergyBalanceModel:
    def test_name_and_feedback_flag(self) -> None:
        model = StaticEnergyBalanceModel()
        assert model.name
        assert model.includes_weight_dependent_feedback is False

    def test_deficit_rate_reference_value(self) -> None:
        # -500 / 7716.18 ~= -0.0648 kg/day
        model = StaticEnergyBalanceModel()
        rate = model.mass_change_rate_kg_per_day(-500.0)
        assert rate == pytest.approx(-0.06479, abs=1e-4)

    def test_surplus_rate_is_positive(self) -> None:
        model = StaticEnergyBalanceModel()
        assert model.mass_change_rate_kg_per_day(500.0) > 0.0

    def test_zero_balance_gives_zero_rate(self) -> None:
        model = StaticEnergyBalanceModel()
        assert model.mass_change_rate_kg_per_day(0.0) == pytest.approx(0.0)

    def test_excess_weight_kg_is_ignored(self) -> None:
        # This model has no feedback term -- the rate must be
        # identical regardless of accumulated weight change.
        model = StaticEnergyBalanceModel()
        rate_a = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=0.0)
        rate_b = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=-50.0)
        assert rate_a == rate_b

    def test_one_year_projection_reference_value(self) -> None:
        # -500 kcal/day * 365 days / 7716.18 ~= -23.65 kg
        model = StaticEnergyBalanceModel()
        result = model.project_weight_change_kg(-500.0, 365)
        assert result == pytest.approx(-23.6516, abs=1e-3)

    def test_ten_year_projection_is_ten_times_one_year(self) -> None:
        # This is exactly the "unbounded, linear forever" problem the
        # model is documented as having -- verified directly.
        model = StaticEnergyBalanceModel()
        one_year = model.project_weight_change_kg(-500.0, 365)
        ten_years = model.project_weight_change_kg(-500.0, 3650)
        assert ten_years == pytest.approx(one_year * 10)

    def test_projection_never_plateaus(self) -> None:
        # Directly demonstrates the documented flaw: the magnitude of
        # projected change keeps growing without bound as days -> inf,
        # unlike the dynamic model's bounded steady state.
        model = StaticEnergyBalanceModel()
        change_100y = abs(model.project_weight_change_kg(-500.0, 365 * 100))
        change_1000y = abs(model.project_weight_change_kg(-500.0, 365 * 1000))
        assert change_1000y == pytest.approx(change_100y * 10)

    def test_negative_days_rejected(self) -> None:
        model = StaticEnergyBalanceModel()
        with pytest.raises(ValueError, match="non-negative"):
            model.project_weight_change_kg(-500.0, -10)

    def test_zero_days_gives_zero_change(self) -> None:
        model = StaticEnergyBalanceModel()
        assert model.project_weight_change_kg(-500.0, 0) == pytest.approx(0.0)
