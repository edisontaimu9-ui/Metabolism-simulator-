"""Unit tests for metabosim.models.macronutrient.glycogen.

Reference values hand-computed and cross-checked against the module's
own docstring examples.
"""

import pytest

from metabosim.models.macronutrient.glycogen import (
    DEFAULT_OXIDATION_TIME_CONSTANT_DAYS,
    GLYCOGEN_WATER_RATIO,
    REFERENCE_MAX_GLYCOGEN_G,
    REFERENCE_WEIGHT_KG,
    glycogen_and_water_kg,
    max_glycogen_g,
    step_glycogen_g,
    step_reference_carbohydrate_intake_g,
)


@pytest.mark.unit
class TestConstants:
    def test_documented_values(self) -> None:
        assert GLYCOGEN_WATER_RATIO == pytest.approx(2.7)
        assert REFERENCE_WEIGHT_KG == pytest.approx(70.0)
        assert REFERENCE_MAX_GLYCOGEN_G == pytest.approx(500.0)
        assert DEFAULT_OXIDATION_TIME_CONSTANT_DAYS == pytest.approx(3.0)


@pytest.mark.unit
class TestMaxGlycogenG:
    def test_reference_weight_gives_reference_capacity(self) -> None:
        assert max_glycogen_g(70.0) == pytest.approx(500.0)

    def test_scales_linearly_with_weight(self) -> None:
        # 100kg -> 500 * (100/70) = 714.2857...
        assert max_glycogen_g(100.0) == pytest.approx(714.2857, abs=1e-3)

    def test_half_reference_weight_gives_half_capacity(self) -> None:
        assert max_glycogen_g(35.0) == pytest.approx(250.0)

    def test_non_positive_weight_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            max_glycogen_g(0.0)
        with pytest.raises(ValueError, match="positive"):
            max_glycogen_g(-10.0)


@pytest.mark.unit
class TestGlycogenAndWaterKg:
    def test_reference_value(self) -> None:
        # 500 * (1 + 2.7) / 1000 = 1.85
        assert glycogen_and_water_kg(500.0) == pytest.approx(1.85)

    def test_zero_glycogen_gives_zero(self) -> None:
        assert glycogen_and_water_kg(0.0) == pytest.approx(0.0)

    def test_scales_linearly(self) -> None:
        assert glycogen_and_water_kg(1000.0) == pytest.approx(
            2 * glycogen_and_water_kg(500.0)
        )

    def test_negative_glycogen_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            glycogen_and_water_kg(-1.0)


@pytest.mark.unit
class TestStepGlycogenG:
    def test_surplus_carbohydrate_increases_glycogen(self) -> None:
        # intake 300, reference 200 -> +100g balance
        result = step_glycogen_g(
            current_glycogen_g=250.0,
            carbohydrate_intake_g=300.0,
            reference_carbohydrate_intake_g=200.0,
            weight_kg=70.0,
        )
        assert result == pytest.approx(350.0)

    def test_deficit_carbohydrate_decreases_glycogen(self) -> None:
        # intake 20, reference 300 -> -280g balance
        result = step_glycogen_g(
            current_glycogen_g=300.0,
            carbohydrate_intake_g=20.0,
            reference_carbohydrate_intake_g=300.0,
            weight_kg=70.0,
        )
        assert result == pytest.approx(20.0)

    def test_matched_intake_and_reference_gives_no_change(self) -> None:
        result = step_glycogen_g(
            current_glycogen_g=250.0,
            carbohydrate_intake_g=250.0,
            reference_carbohydrate_intake_g=250.0,
            weight_kg=70.0,
        )
        assert result == pytest.approx(250.0)

    def test_clamped_at_zero_floor(self) -> None:
        result = step_glycogen_g(
            current_glycogen_g=20.0,
            carbohydrate_intake_g=0.0,
            reference_carbohydrate_intake_g=300.0,
            weight_kg=70.0,
        )
        assert result == pytest.approx(0.0)

    def test_clamped_at_capacity_ceiling(self) -> None:
        result = step_glycogen_g(
            current_glycogen_g=480.0,
            carbohydrate_intake_g=500.0,
            reference_carbohydrate_intake_g=100.0,
            weight_kg=70.0,
        )
        # unclamped would be 480 + 400 = 880, way beyond 500g capacity
        assert result == pytest.approx(500.0)

    def test_capacity_scales_with_weight_argument(self) -> None:
        result = step_glycogen_g(
            current_glycogen_g=480.0,
            carbohydrate_intake_g=500.0,
            reference_carbohydrate_intake_g=100.0,
            weight_kg=100.0,
        )
        assert result == pytest.approx(max_glycogen_g(100.0))

    def test_negative_current_glycogen_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            step_glycogen_g(
                current_glycogen_g=-1.0,
                carbohydrate_intake_g=100.0,
                reference_carbohydrate_intake_g=100.0,
                weight_kg=70.0,
            )


@pytest.mark.unit
class TestStepReferenceCarbohydrateIntakeG:
    def test_reference_moves_toward_todays_intake(self) -> None:
        # alpha = 1/3; 200 + (1/3)*(300-200) = 233.33...
        result = step_reference_carbohydrate_intake_g(
            current_reference_g=200.0, todays_intake_g=300.0
        )
        assert result == pytest.approx(233.333, abs=1e-3)

    def test_reference_unchanged_when_intake_matches(self) -> None:
        result = step_reference_carbohydrate_intake_g(
            current_reference_g=250.0, todays_intake_g=250.0
        )
        assert result == pytest.approx(250.0)

    def test_repeated_constant_intake_converges_to_that_intake(self) -> None:
        reference = 300.0
        for _ in range(50):
            reference = step_reference_carbohydrate_intake_g(reference, 20.0)
        assert reference == pytest.approx(20.0, abs=1e-6)

    def test_custom_time_constant_changes_adaptation_speed(self) -> None:
        fast = step_reference_carbohydrate_intake_g(
            200.0, 300.0, time_constant_days=1.0
        )
        slow = step_reference_carbohydrate_intake_g(
            200.0, 300.0, time_constant_days=10.0
        )
        # A shorter time constant should move further toward the new
        # intake in a single day.
        assert abs(fast - 300.0) < abs(slow - 300.0)

    def test_non_positive_time_constant_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            step_reference_carbohydrate_intake_g(200.0, 300.0, time_constant_days=0.0)
        with pytest.raises(ValueError, match="positive"):
            step_reference_carbohydrate_intake_g(200.0, 300.0, time_constant_days=-1.0)


@pytest.mark.unit
class TestRealisticScenario:
    """End-to-end sanity checks reproducing the well-known low-carb
    'water weight' phenomenon, matching the module docstring's claims.
    """

    def test_low_carb_switch_depletes_glycogen_within_a_few_days(self) -> None:
        reference = 300.0
        glycogen = 300.0
        weight = 80.0
        for _ in range(5):
            glycogen = step_glycogen_g(glycogen, 20.0, reference, weight)
            reference = step_reference_carbohydrate_intake_g(reference, 20.0)
        assert glycogen < 10.0  # essentially depleted

    def test_glycogen_transient_resolves_once_intake_stabilizes(self) -> None:
        # After many days at a stable NEW intake level, the reference
        # should have caught up, and further glycogen changes should
        # be negligible -- i.e. the transient has fully resolved.
        reference = 300.0
        glycogen = 300.0
        weight = 80.0
        for _ in range(60):
            glycogen = step_glycogen_g(glycogen, 20.0, reference, weight)
            reference = step_reference_carbohydrate_intake_g(reference, 20.0)
        glycogen_before = glycogen
        glycogen = step_glycogen_g(glycogen, 20.0, reference, weight)
        assert glycogen == pytest.approx(glycogen_before, abs=0.5)

    def test_refeed_replenishes_glycogen_up_to_capacity(self) -> None:
        reference = 20.0
        glycogen = 0.0
        weight = 80.0
        for _ in range(10):
            glycogen = step_glycogen_g(glycogen, 300.0, reference, weight)
            reference = step_reference_carbohydrate_intake_g(reference, 300.0)
        assert glycogen == pytest.approx(max_glycogen_g(weight))
