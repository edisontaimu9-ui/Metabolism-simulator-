"""Unit tests for metabosim.models.disease.thyroid.

Reference values hand-computed from THYROID_BMR_ADJUSTMENT_FRACTION.
"""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.disease.thyroid import (
    THYROID_BMR_ADJUSTMENT_FRACTION,
    ThyroidModifier,
    ThyroidStatus,
)


@pytest.fixture
def person() -> Person:
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


@pytest.mark.unit
class TestThyroidStatus:
    def test_all_seven_tiers_present(self) -> None:
        expected = {
            "euthyroid",
            "mild_hypothyroid",
            "moderate_hypothyroid",
            "severe_hypothyroid",
            "mild_hyperthyroid",
            "moderate_hyperthyroid",
            "severe_hyperthyroid",
        }
        actual = {status.value for status in ThyroidStatus}
        assert actual == expected


@pytest.mark.unit
class TestThyroidBmrAdjustmentFraction:
    def test_euthyroid_is_zero(self) -> None:
        assert THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.EUTHYROID] == 0.0

    def test_hypothyroid_tiers_are_negative_and_increasing_in_magnitude(self) -> None:
        mild = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.MILD_HYPOTHYROID]
        moderate = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.MODERATE_HYPOTHYROID]
        severe = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.SEVERE_HYPOTHYROID]
        assert severe < moderate < mild < 0.0

    def test_hyperthyroid_tiers_are_positive_and_increasing(self) -> None:
        mild = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.MILD_HYPERTHYROID]
        moderate = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.MODERATE_HYPERTHYROID]
        severe = THYROID_BMR_ADJUSTMENT_FRACTION[ThyroidStatus.SEVERE_HYPERTHYROID]
        assert 0.0 < mild < moderate < severe

    def test_documented_values(self) -> None:
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.MILD_HYPOTHYROID
        ] == pytest.approx(-0.10)
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.MODERATE_HYPOTHYROID
        ] == pytest.approx(-0.20)
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.SEVERE_HYPOTHYROID
        ] == pytest.approx(-0.35)
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.MILD_HYPERTHYROID
        ] == pytest.approx(0.15)
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.MODERATE_HYPERTHYROID
        ] == pytest.approx(0.30)
        assert THYROID_BMR_ADJUSTMENT_FRACTION[
            ThyroidStatus.SEVERE_HYPERTHYROID
        ] == pytest.approx(0.50)


@pytest.mark.unit
class TestThyroidModifier:
    def test_default_status_is_euthyroid(self, person: Person) -> None:
        modifier = ThyroidModifier()
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(1780.0)

    def test_moderate_hypothyroid_reference_value(self, person: Person) -> None:
        modifier = ThyroidModifier(status=ThyroidStatus.MODERATE_HYPOTHYROID)
        # 1780 * (1 - 0.20) = 1424.0
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(1424.0)

    def test_severe_hyperthyroid_reference_value(self, person: Person) -> None:
        modifier = ThyroidModifier(status=ThyroidStatus.SEVERE_HYPERTHYROID)
        # 1780 * (1 + 0.50) = 2670.0
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(2670.0)

    def test_name_reflects_status(self) -> None:
        modifier = ThyroidModifier(status=ThyroidStatus.SEVERE_HYPOTHYROID)
        assert "severe_hypothyroid" in modifier.name

    def test_non_positive_base_bmr_rejected(self, person: Person) -> None:
        modifier = ThyroidModifier(status=ThyroidStatus.MILD_HYPOTHYROID)
        with pytest.raises(ValueError, match="positive"):
            modifier.apply_to_bmr_kcal(0.0, person)
        with pytest.raises(ValueError, match="positive"):
            modifier.apply_to_bmr_kcal(-100.0, person)

    def test_all_tiers_produce_distinct_adjustments(self, person: Person) -> None:
        results = {
            status: ThyroidModifier(status=status).apply_to_bmr_kcal(1780.0, person)
            for status in ThyroidStatus
        }
        assert len(set(results.values())) == len(ThyroidStatus)
