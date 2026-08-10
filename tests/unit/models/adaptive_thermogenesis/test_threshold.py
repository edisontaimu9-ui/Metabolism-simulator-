"""Unit tests for metabosim.models.adaptive_thermogenesis.threshold."""

import pytest

from metabosim.models.adaptive_thermogenesis.threshold import (
    DEFAULT_ADAPTATION_FRACTION,
    DEFAULT_THRESHOLD_FRACTION,
    ThresholdAdaptiveThermogenesisModel,
)


@pytest.mark.unit
class TestThresholdConstants:
    def test_documented_defaults(self) -> None:
        assert DEFAULT_THRESHOLD_FRACTION == pytest.approx(0.10)
        assert DEFAULT_ADAPTATION_FRACTION == pytest.approx(0.15)


@pytest.mark.unit
class TestThresholdConstruction:
    def test_name_is_set(self) -> None:
        assert ThresholdAdaptiveThermogenesisModel.name

    def test_default_parameters(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel()
        assert model.threshold_fraction == pytest.approx(0.10)
        assert model.adaptation_fraction == pytest.approx(0.15)

    def test_custom_parameters_accepted(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel(
            threshold_fraction=0.05, adaptation_fraction=0.10
        )
        assert model.threshold_fraction == pytest.approx(0.05)
        assert model.adaptation_fraction == pytest.approx(0.10)

    def test_non_positive_threshold_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            ThresholdAdaptiveThermogenesisModel(threshold_fraction=0.0)
        with pytest.raises(ValueError, match="positive"):
            ThresholdAdaptiveThermogenesisModel(threshold_fraction=-0.1)

    def test_negative_adaptation_fraction_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            ThresholdAdaptiveThermogenesisModel(adaptation_fraction=-0.1)

    def test_zero_adaptation_fraction_accepted(self) -> None:
        # Degenerate but valid: a threshold that, once crossed,
        # applies zero adjustment.
        model = ThresholdAdaptiveThermogenesisModel(adaptation_fraction=0.0)
        assert model.adaptation_fraction == 0.0


@pytest.mark.unit
class TestThresholdCalculation:
    def test_below_threshold_gives_zero(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 95.0, 2500.0)  # 5% loss
        assert result == pytest.approx(0.0)

    def test_at_threshold_activates_full_adjustment(self) -> None:
        # Exactly 10% loss -- the boundary is inclusive.
        model = ThresholdAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        assert result == pytest.approx(-375.0)  # -0.15 * 2500

    def test_beyond_threshold_stays_flat(self) -> None:
        # 20% and 50% loss should give the SAME fixed adjustment as
        # exactly 10% loss -- no further scaling beyond the threshold.
        model = ThresholdAdaptiveThermogenesisModel()
        result_10pct = model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        result_20pct = model.calculate_adjustment_kcal(100.0, 80.0, 2500.0)
        result_50pct = model.calculate_adjustment_kcal(100.0, 50.0, 2500.0)
        assert result_20pct == pytest.approx(result_10pct)
        assert result_50pct == pytest.approx(result_10pct)

    def test_symmetric_for_gain(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 110.0, 2500.0)  # 10% gain
        assert result == pytest.approx(375.0)

    def test_just_below_threshold_gives_zero_not_partial(self) -> None:
        # 9.9% loss should still be exactly zero -- this is the
        # defining "no partial credit" behavior distinguishing this
        # model from the proportional one.
        model = ThresholdAdaptiveThermogenesisModel()
        result = model.calculate_adjustment_kcal(100.0, 90.1, 2500.0)
        assert result == pytest.approx(0.0)

    def test_custom_threshold_and_magnitude(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel(
            threshold_fraction=0.05, adaptation_fraction=0.08
        )
        below = model.calculate_adjustment_kcal(100.0, 96.0, 2500.0)  # 4% loss
        at = model.calculate_adjustment_kcal(100.0, 95.0, 2500.0)  # 5% loss
        assert below == pytest.approx(0.0)
        assert at == pytest.approx(-0.08 * 2500.0)

    def test_non_positive_baseline_weight_rejected(self) -> None:
        model = ThresholdAdaptiveThermogenesisModel()
        with pytest.raises(ValueError, match="positive"):
            model.calculate_adjustment_kcal(0.0, 90.0, 2500.0)
