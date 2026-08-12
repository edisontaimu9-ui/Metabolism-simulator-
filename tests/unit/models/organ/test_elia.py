"""Unit tests for metabosim.models.organ.elia.

Reference values hand-computed from cited constants:
brain=1.407kg*240, liver=1.561kg*200, heart=0.3kg*440, kidneys=0.266kg*440,
residual_lean = lean_mass_kg - 3.534, at Ki=12.5 (young) or 12.1 (>50y).
"""

import pytest

from metabosim.models.organ.elia import (
    AGE_ADJUSTMENT_THRESHOLD_YEARS,
    KI_ADIPOSE,
    KI_ADIPOSE_OVER_50,
    KI_BRAIN,
    KI_HEART,
    KI_KIDNEYS,
    KI_LIVER,
    KI_RESIDUAL_LEAN,
    KI_RESIDUAL_LEAN_OVER_50,
    REFERENCE_BRAIN_KG,
    REFERENCE_HEART_KG,
    REFERENCE_KIDNEYS_KG,
    REFERENCE_LIVER_KG,
    calculate_organ_bmr_breakdown_kcal,
)


@pytest.mark.unit
class TestConstants:
    def test_elia_1992_ki_values(self) -> None:
        assert KI_BRAIN == pytest.approx(240.0)
        assert KI_LIVER == pytest.approx(200.0)
        assert KI_HEART == pytest.approx(440.0)
        assert KI_KIDNEYS == pytest.approx(440.0)

    def test_residual_lean_is_average_of_muscle_and_residual(self) -> None:
        # (13 + 12) / 2 = 12.5
        assert KI_RESIDUAL_LEAN == pytest.approx(12.5)

    def test_age_adjusted_values_lower_than_defaults(self) -> None:
        # Wang et al. (2010) found Elia's values overestimate for >50y
        assert KI_ADIPOSE_OVER_50 < KI_ADIPOSE
        assert KI_RESIDUAL_LEAN_OVER_50 < KI_RESIDUAL_LEAN

    def test_age_threshold(self) -> None:
        assert AGE_ADJUSTMENT_THRESHOLD_YEARS == pytest.approx(50.0)

    def test_reference_organ_masses(self) -> None:
        assert REFERENCE_BRAIN_KG == pytest.approx(1.407)
        assert REFERENCE_LIVER_KG == pytest.approx(1.561)
        assert REFERENCE_HEART_KG == pytest.approx(0.300)
        assert REFERENCE_KIDNEYS_KG == pytest.approx(0.266)


@pytest.mark.unit
class TestCalculateOrganBmrBreakdownKcal:
    def test_reference_worked_example(self) -> None:
        # 80kg person, 20% body fat -> fat_mass=16, lean_mass=64
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        assert breakdown.brain_kcal == pytest.approx(1.407 * 240.0)
        assert breakdown.liver_kcal == pytest.approx(1.561 * 200.0)
        assert breakdown.heart_kcal == pytest.approx(0.300 * 440.0)
        assert breakdown.kidneys_kcal == pytest.approx(0.266 * 440.0)
        assert breakdown.adipose_kcal == pytest.approx(16.0 * 4.5)
        expected_residual_lean_kg = 64.0 - (1.407 + 1.561 + 0.300 + 0.266)
        assert breakdown.residual_lean_kg == pytest.approx(expected_residual_lean_kg)
        assert breakdown.residual_lean_kcal == pytest.approx(
            expected_residual_lean_kg * 12.5
        )

    def test_total_is_sum_of_components(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        component_sum = (
            breakdown.brain_kcal
            + breakdown.liver_kcal
            + breakdown.heart_kcal
            + breakdown.kidneys_kcal
            + breakdown.residual_lean_kcal
            + breakdown.adipose_kcal
        )
        assert breakdown.total_kcal == pytest.approx(component_sum)

    def test_reference_total_reasonably_close_to_mifflin_st_jeor(self) -> None:
        # Cross-validation sanity check: two independently-derived
        # methods (this bottom-up organ model vs. the top-down
        # Mifflin-St Jeor regression for an 80kg/180cm/30y male,
        # known from Phase 4 to be 1780.0 kcal) should agree to
        # within a modest margin, not be wildly different.
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        mifflin_st_jeor_kcal = 1780.0
        relative_diff = abs(breakdown.total_kcal - mifflin_st_jeor_kcal) / (
            mifflin_st_jeor_kcal
        )
        assert relative_diff < 0.10  # within 10%

    def test_more_fat_mass_increases_total_only_modestly(self) -> None:
        # Adipose tissue has a very low specific metabolic rate (4.5
        # kcal/kg/day) -- adding fat mass should increase total BMR,
        # but only by a small amount per kg, much less than adding
        # the same mass as lean tissue would.
        low_fat = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=10.0, lean_mass_kg=64.0
        )
        high_fat = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=30.0, lean_mass_kg=64.0
        )
        # 20 kg more fat -> 20*4.5 = 90 kcal more
        assert high_fat.total_kcal - low_fat.total_kcal == pytest.approx(90.0)

    def test_more_lean_mass_increases_total_substantially(self) -> None:
        low_lean = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=60.0
        )
        high_lean = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=70.0
        )
        # 10 kg more lean mass, all residual -> 10*12.5 = 125 kcal more
        assert high_lean.total_kcal - low_lean.total_kcal == pytest.approx(125.0)

    def test_age_adjustment_activates_above_threshold(self) -> None:
        young = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=40
        )
        old = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=60
        )
        assert old.total_kcal < young.total_kcal

    def test_age_adjustment_not_used_at_exactly_threshold(self) -> None:
        # Strictly greater than the threshold, per the documented rule.
        at_threshold = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=50
        )
        default = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=None
        )
        assert at_threshold.total_kcal == pytest.approx(default.total_kcal)

    def test_none_age_years_uses_default_ki_values(self) -> None:
        with_none = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=None
        )
        with_young = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0, age_years=25
        )
        assert with_none.total_kcal == pytest.approx(with_young.total_kcal)

    def test_negative_fat_mass_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            calculate_organ_bmr_breakdown_kcal(fat_mass_kg=-1.0, lean_mass_kg=64.0)

    def test_lean_mass_below_fixed_organ_total_rejected(self) -> None:
        with pytest.raises(ValueError, match="implausible"):
            calculate_organ_bmr_breakdown_kcal(fat_mass_kg=5.0, lean_mass_kg=2.0)

    def test_lean_mass_exactly_at_fixed_organ_total_accepted(self) -> None:
        # Boundary: residual_lean_kg == 0 is valid (though extreme).
        fixed_total = 1.407 + 1.561 + 0.300 + 0.266
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=5.0, lean_mass_kg=fixed_total
        )
        assert breakdown.residual_lean_kg == pytest.approx(0.0, abs=1e-9)
        assert breakdown.residual_lean_kcal == pytest.approx(0.0, abs=1e-9)

    def test_reported_organ_masses_match_reference_constants(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        assert breakdown.brain_kg == pytest.approx(REFERENCE_BRAIN_KG)
        assert breakdown.liver_kg == pytest.approx(REFERENCE_LIVER_KG)
        assert breakdown.heart_kg == pytest.approx(REFERENCE_HEART_KG)
        assert breakdown.kidneys_kg == pytest.approx(REFERENCE_KIDNEYS_KG)
        assert breakdown.adipose_kg == pytest.approx(16.0)

    def test_breakdown_is_frozen(self) -> None:
        from pydantic import ValidationError

        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        with pytest.raises(ValidationError):
            breakdown.total_kcal = 9999.0  # type: ignore[misc]
