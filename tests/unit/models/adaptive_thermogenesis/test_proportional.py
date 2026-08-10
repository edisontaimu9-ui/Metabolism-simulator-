"""Unit tests for metabosim.models.adaptive_thermogenesis.proportional.

Reference values hand-computed:
    adjustment = k * clamp(fraction, -limit, +limit) * reference
with defaults k=1.5, limit=0.20.
"""

import pytest

from metabosim.models.adaptive_thermogenesis.proportional import (
    DEFAULT_ADAPTATION_SLOPE,
    DEFAULT_MAX_WEIGHT_CHANGE_FRACTION,
    ProportionalAdaptiveThermogenesisModel,
)


@pytest.mark.unit
class TestProportionalConstants:
    def test_documented_defaults(self) -> None:
        assert DEFAULT_ADAPTATION_SLOPE == pytest.approx(1.5)
        assert DEFAULT_MAX_WEIGHT_CHANGE_FRACTION == pytest.approx(0.20)


@pytest.mark.unit
class TestProportionalConstruction:
    def test_name_is_set(self) -> None:
        assert ProportionalAdaptiveThermogenesisModel.name

    def test_default_parameters(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel()
        assert model.adaptation_slope == pytest.approx(1.5)
        assert model.max_weight_change_fraction == pytest.approx(0.20)

    def test_custom_parameters_accepted(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel(
            adaptation_slope=2.0, max_weight_change_fraction=0.30
        )
        assert model.adaptation_slope == pytest.approx(2.0)
        assert model.max_weight_change_fraction == pytest.approx(0.30)

    def test_non_positive_max_fraction_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            ProportionalAdaptiveThermogenesisModel(max_weight_change_fraction=0.0)
        with pytest.raises(ValueError, match="positive"):
            ProportionalAdaptiveThermogenesisModel(max_weight_change_fraction=-0.1)


@pytest.mark.unit
class TestProportionalCalculation:
    def test_calibration_point_10_percent_loss(self) -> None:
        # -0.10 fraction * 1.5 * 2500 = -375.0 (exactly -15% of reference)
        model = ProportionalAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        assert result == pytest.approx(-375.0)
        assert result == pytest.approx(-0.15 * 2500.0)

    def test_calibration_point_10_percent_gain(self) -> None:
        # Symmetric: +0.10 fraction -> +15% of reference
        model = ProportionalAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 110.0, 2500.0)
        assert result == pytest.approx(375.0)

    def test_5_percent_loss_is_half_of_10_percent(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel()
        result_5pct = model.calculate_adjustment_kcal(100.0, 95.0, 2500.0)
        result_10pct = model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        assert result_5pct == pytest.approx(result_10pct / 2.0)

    def test_no_change_gives_zero_adjustment(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel()
        assert model.calculate_adjustment_kcal(100.0, 100.0, 2500.0) == pytest.approx(
            0.0
        )

    def test_clamping_at_20_percent_loss(self) -> None:
        # fraction=-0.20 (at the clamp boundary exactly): -0.20*1.5*2500=-750
        model = ProportionalAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 80.0, 2500.0)
        assert result == pytest.approx(-750.0)

    def test_clamping_beyond_20_percent_loss_does_not_scale_further(self) -> None:
        # 30% and 60% loss should clamp to the SAME adjustment as 20%
        # loss, since the fraction itself is clamped before scaling.
        model = ProportionalAdaptiveThermogenesisModel()
        result_30pct = model.calculate_adjustment_kcal(100.0, 70.0, 2500.0)
        result_60pct = model.calculate_adjustment_kcal(100.0, 40.0, 2500.0)
        result_20pct = model.calculate_adjustment_kcal(100.0, 80.0, 2500.0)
        assert result_30pct == pytest.approx(result_20pct)
        assert result_60pct == pytest.approx(result_20pct)

    def test_clamping_symmetric_for_gain(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel()
        result_30pct_gain = model.calculate_adjustment_kcal(100.0, 130.0, 2500.0)
        result_20pct_gain = model.calculate_adjustment_kcal(100.0, 120.0, 2500.0)
        assert result_30pct_gain == pytest.approx(result_20pct_gain)

    def test_custom_slope_changes_calibration(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel(adaptation_slope=1.0)
        # -0.10 * 1.0 * 2500 = -250 (not -375, since slope is 1.0 not 1.5)
        result = model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        assert result == pytest.approx(-250.0)

    def test_non_positive_baseline_weight_rejected(self) -> None:
        model = ProportionalAdaptiveThermogenesisModel()
        with pytest.raises(ValueError, match="positive"):
            model.calculate_adjustment_kcal(0.0, 90.0, 2500.0)
        with pytest.raises(ValueError, match="positive"):
            model.calculate_adjustment_kcal(-10.0, 90.0, 2500.0)

    def test_negative_reference_expenditure_flips_sign_naturally(self) -> None:
        # Not a physiologically meaningful input, but the arithmetic
        # itself should behave predictably (no special-casing needed).
        model = ProportionalAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 90.0, -2500.0)
        assert result == pytest.approx(375.0)
