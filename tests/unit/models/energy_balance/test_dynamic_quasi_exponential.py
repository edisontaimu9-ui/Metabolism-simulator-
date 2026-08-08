"""Unit tests for metabosim.models.energy_balance.dynamic_quasi_exponential.

Reference values hand-computed from the closed-form solution:
    W(t) = (E/gamma) * (1 - exp(-gamma*t/rho))
with defaults rho=7380, gamma=20.0.
"""

import math

import pytest

from metabosim.models.energy_balance.dynamic_quasi_exponential import (
    DEFAULT_ENERGY_DENSITY_KCAL_PER_KG,
    DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY,
    DynamicQuasiExponentialModel,
)


@pytest.mark.unit
class TestDynamicModelConstants:
    def test_default_energy_density_matches_tissue_model_blend(self) -> None:
        # 0.25*1020 + 0.75*9500 = 7380
        assert DEFAULT_ENERGY_DENSITY_KCAL_PER_KG == pytest.approx(7380.0)

    def test_default_expenditure_slope(self) -> None:
        assert DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY == pytest.approx(20.0)


@pytest.mark.unit
class TestDynamicQuasiExponentialModelConstruction:
    def test_name_and_feedback_flag(self) -> None:
        model = DynamicQuasiExponentialModel()
        assert model.name
        assert model.includes_weight_dependent_feedback is True

    def test_default_parameters(self) -> None:
        model = DynamicQuasiExponentialModel()
        assert model.rho == pytest.approx(7380.0)
        assert model.gamma == pytest.approx(20.0)

    def test_custom_parameters_accepted(self) -> None:
        model = DynamicQuasiExponentialModel(
            tissue_energy_density_kcal_per_kg=8000.0,
            expenditure_slope_kcal_per_kg_per_day=25.0,
        )
        assert model.rho == pytest.approx(8000.0)
        assert model.gamma == pytest.approx(25.0)

    def test_non_positive_rho_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            DynamicQuasiExponentialModel(tissue_energy_density_kcal_per_kg=0.0)
        with pytest.raises(ValueError, match="positive"):
            DynamicQuasiExponentialModel(tissue_energy_density_kcal_per_kg=-100.0)

    def test_non_positive_gamma_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            DynamicQuasiExponentialModel(expenditure_slope_kcal_per_kg_per_day=0.0)
        with pytest.raises(ValueError, match="positive"):
            DynamicQuasiExponentialModel(expenditure_slope_kcal_per_kg_per_day=-5.0)


@pytest.mark.unit
class TestSteadyStateAndTimeConstant:
    def test_time_constant_reference_value(self) -> None:
        # tau = rho/gamma = 7380/20 = 369.0 days
        model = DynamicQuasiExponentialModel()
        assert model.time_constant_days == pytest.approx(369.0)

    def test_steady_state_reference_value(self) -> None:
        # E/gamma = -500/20 = -25.0 kg
        model = DynamicQuasiExponentialModel()
        assert model.steady_state_weight_change_kg(-500.0) == pytest.approx(-25.0)

    def test_steady_state_scales_linearly_with_balance(self) -> None:
        model = DynamicQuasiExponentialModel()
        assert model.steady_state_weight_change_kg(-1000.0) == pytest.approx(
            2 * model.steady_state_weight_change_kg(-500.0)
        )


@pytest.mark.unit
class TestMassChangeRate:
    def test_rate_at_zero_excess_weight(self) -> None:
        # dW/dt = (-500 - 0)/7380
        model = DynamicQuasiExponentialModel()
        rate = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=0.0)
        assert rate == pytest.approx(-500.0 / 7380.0)

    def test_rate_shrinks_as_excess_weight_approaches_steady_state(self) -> None:
        # As excess_weight_kg approaches the steady state (-25 kg), the
        # rate should approach zero -- this IS the negative feedback
        # loop the model exists to represent.
        model = DynamicQuasiExponentialModel()
        rate_at_start = abs(
            model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=0.0)
        )
        rate_near_steady_state = abs(
            model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=-24.9)
        )
        assert rate_near_steady_state < rate_at_start

    def test_rate_is_exactly_zero_at_steady_state(self) -> None:
        model = DynamicQuasiExponentialModel()
        steady_state = model.steady_state_weight_change_kg(-500.0)
        rate = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=steady_state)
        assert rate == pytest.approx(0.0, abs=1e-9)


@pytest.mark.unit
class TestProjectWeightChangeKg:
    def test_one_year_reference_value(self) -> None:
        model = DynamicQuasiExponentialModel()
        result = model.project_weight_change_kg(-500.0, 365)
        assert result == pytest.approx(-15.7028, abs=1e-3)

    def test_three_year_reference_value(self) -> None:
        model = DynamicQuasiExponentialModel()
        result = model.project_weight_change_kg(-500.0, 365 * 3)
        assert result == pytest.approx(-23.7142, abs=1e-3)

    def test_approaches_steady_state_at_large_t(self) -> None:
        model = DynamicQuasiExponentialModel()
        result = model.project_weight_change_kg(-500.0, 365 * 100)
        steady_state = model.steady_state_weight_change_kg(-500.0)
        assert result == pytest.approx(steady_state, abs=1e-6)

    def test_bounded_unlike_static_rule(self) -> None:
        # This is the entire point of the model: unlike the static
        # rule, projected change does NOT keep growing without bound.
        model = DynamicQuasiExponentialModel()
        change_10y = model.project_weight_change_kg(-500.0, 365 * 10)
        change_1000y = model.project_weight_change_kg(-500.0, 365 * 1000)
        # Both should be very close to the same steady state, NOT a
        # 100x difference (contrast with the static rule's test of the
        # same ratio, which IS ~10x).
        assert change_1000y == pytest.approx(change_10y, abs=0.01)

    def test_negative_days_rejected(self) -> None:
        model = DynamicQuasiExponentialModel()
        with pytest.raises(ValueError, match="non-negative"):
            model.project_weight_change_kg(-500.0, -1)

    def test_zero_days_gives_zero_change(self) -> None:
        model = DynamicQuasiExponentialModel()
        assert model.project_weight_change_kg(-500.0, 0) == pytest.approx(0.0)

    def test_rate_integral_matches_closed_form_numerically(self) -> None:
        # Sanity-check that mass_change_rate_kg_per_day, if numerically
        # integrated with small steps, reproduces the closed-form
        # project_weight_change_kg result -- confirms the two methods
        # are mutually consistent, not just independently plausible.
        model = DynamicQuasiExponentialModel()
        daily_balance = -500.0
        dt = 0.1
        w = 0.0
        steps = int(365 / dt)
        for _ in range(steps):
            w += model.mass_change_rate_kg_per_day(daily_balance, w) * dt
        closed_form = model.project_weight_change_kg(daily_balance, 365)
        assert w == pytest.approx(closed_form, rel=1e-3)

    def test_positive_surplus_produces_weight_gain(self) -> None:
        model = DynamicQuasiExponentialModel()
        result = model.project_weight_change_kg(500.0, 365)
        assert result > 0.0


@pytest.mark.unit
class TestConsistencyWithMathModule:
    def test_closed_form_matches_manual_exponential_calculation(self) -> None:
        model = DynamicQuasiExponentialModel()
        e, t = -500.0, 200.0
        expected = (e / model.gamma) * (1 - math.exp(-model.gamma * t / model.rho))
        assert model.project_weight_change_kg(e, t) == pytest.approx(expected)
