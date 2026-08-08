"""Unit tests for metabosim.models.body_composition.forbes.

Reference values hand-computed from dFFM/dBW = C/(C+FM), with
C=10.4 (female) or C=13.8 (male).
"""

import pytest

from metabosim.domain.enums import Sex
from metabosim.models.body_composition.forbes import (
    FORBES_CONSTANT_FEMALE_KG,
    FORBES_CONSTANT_MALE_KG,
    ForbesPartitionModel,
)


@pytest.mark.unit
class TestForbesConstants:
    def test_documented_values(self) -> None:
        assert FORBES_CONSTANT_FEMALE_KG == pytest.approx(10.4)
        assert FORBES_CONSTANT_MALE_KG == pytest.approx(13.8)


@pytest.mark.unit
class TestForbesPartitionModelConstruction:
    def test_name_is_set(self) -> None:
        assert ForbesPartitionModel.name

    def test_default_constants(self) -> None:
        model = ForbesPartitionModel()
        assert model.forbes_constant_female_kg == pytest.approx(10.4)
        assert model.forbes_constant_male_kg == pytest.approx(13.8)

    def test_custom_constants_accepted(self) -> None:
        model = ForbesPartitionModel(
            forbes_constant_female_kg=12.0, forbes_constant_male_kg=15.0
        )
        assert model.forbes_constant_female_kg == pytest.approx(12.0)
        assert model.forbes_constant_male_kg == pytest.approx(15.0)

    def test_non_positive_female_constant_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            ForbesPartitionModel(forbes_constant_female_kg=0.0)
        with pytest.raises(ValueError, match="positive"):
            ForbesPartitionModel(forbes_constant_female_kg=-1.0)

    def test_non_positive_male_constant_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            ForbesPartitionModel(forbes_constant_male_kg=0.0)
        with pytest.raises(ValueError, match="positive"):
            ForbesPartitionModel(forbes_constant_male_kg=-1.0)


@pytest.mark.unit
class TestFfmFractionOfChange:
    def test_exactly_half_at_fat_mass_equal_to_constant(self) -> None:
        # The defining physical property of the Forbes constant: at
        # FM == C, fat and fat-free mass change in exactly equal
        # amounts.
        model = ForbesPartitionModel()
        assert model.ffm_fraction_of_change(10.4, Sex.FEMALE) == pytest.approx(0.5)
        assert model.ffm_fraction_of_change(13.8, Sex.MALE) == pytest.approx(0.5)

    def test_low_fat_mass_gives_high_ffm_fraction(self) -> None:
        # 10.4/(10.4+1) ~= 0.9123
        model = ForbesPartitionModel()
        result = model.ffm_fraction_of_change(1.0, Sex.FEMALE)
        assert result == pytest.approx(0.9123, abs=1e-3)

    def test_high_fat_mass_gives_low_ffm_fraction(self) -> None:
        # 10.4/(10.4+50) ~= 0.1722
        model = ForbesPartitionModel()
        result = model.ffm_fraction_of_change(50.0, Sex.FEMALE)
        assert result == pytest.approx(0.1722, abs=1e-3)

    def test_zero_fat_mass_gives_fraction_of_exactly_one(self) -> None:
        model = ForbesPartitionModel()
        assert model.ffm_fraction_of_change(0.0, Sex.FEMALE) == pytest.approx(1.0)

    def test_fraction_always_in_unit_interval(self) -> None:
        model = ForbesPartitionModel()
        for fm in [0.0, 0.5, 5.0, 10.4, 20.0, 50.0, 200.0]:
            for sex in (Sex.MALE, Sex.FEMALE):
                fraction = model.ffm_fraction_of_change(fm, sex)
                assert 0.0 <= fraction <= 1.0

    def test_fraction_decreases_monotonically_with_fat_mass(self) -> None:
        model = ForbesPartitionModel()
        fat_masses = [1.0, 5.0, 10.4, 20.0, 50.0, 100.0]
        fractions = [model.ffm_fraction_of_change(fm, Sex.FEMALE) for fm in fat_masses]
        assert fractions == sorted(fractions, reverse=True)

    def test_negative_fat_mass_rejected(self) -> None:
        model = ForbesPartitionModel()
        with pytest.raises(ValueError, match="non-negative"):
            model.ffm_fraction_of_change(-1.0, Sex.FEMALE)

    def test_male_and_female_differ_at_same_fat_mass(self) -> None:
        # Different constants (10.4 vs 13.8) must produce different
        # fractions at the same fat mass -- confirms sex is actually
        # consulted, not silently ignored.
        model = ForbesPartitionModel()
        female_fraction = model.ffm_fraction_of_change(15.0, Sex.FEMALE)
        male_fraction = model.ffm_fraction_of_change(15.0, Sex.MALE)
        assert female_fraction != male_fraction


@pytest.mark.unit
class TestPartitionMassChangeKgIntegration:
    def test_partition_consistent_with_ffm_fraction(self) -> None:
        model = ForbesPartitionModel()
        fraction = model.ffm_fraction_of_change(20.0, Sex.FEMALE)
        delta_fat, delta_lean = model.partition_mass_change_kg(-1.0, 20.0, Sex.FEMALE)
        assert delta_lean == pytest.approx(fraction * -1.0)
        assert delta_fat + delta_lean == pytest.approx(-1.0)

    def test_weight_gain_at_low_fat_mass_is_mostly_lean(self) -> None:
        model = ForbesPartitionModel()
        delta_fat, delta_lean = model.partition_mass_change_kg(1.0, 2.0, Sex.FEMALE)
        assert delta_lean > delta_fat

    def test_weight_gain_at_high_fat_mass_is_mostly_fat(self) -> None:
        model = ForbesPartitionModel()
        delta_fat, delta_lean = model.partition_mass_change_kg(1.0, 60.0, Sex.FEMALE)
        assert delta_fat > delta_lean
