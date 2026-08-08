"""Unit tests for metabosim.models.energy_balance.tissue_energy_density.

Reference values hand-computed: default blended density
= 0.25*1020 + 0.75*9500 = 255 + 7125 = 7380 kcal/kg.
"""

import pytest

from metabosim.models.energy_balance.tissue_energy_density import (
    DEFAULT_FFM_FRACTION,
    FAT_ENERGY_DENSITY_KCAL_PER_KG,
    FFM_ENERGY_DENSITY_KCAL_PER_KG,
    TissueEnergyDensityModel,
)


@pytest.mark.unit
class TestTissueEnergyDensityConstants:
    def test_documented_values(self) -> None:
        assert FFM_ENERGY_DENSITY_KCAL_PER_KG == pytest.approx(1020.0)
        assert FAT_ENERGY_DENSITY_KCAL_PER_KG == pytest.approx(9500.0)
        assert DEFAULT_FFM_FRACTION == pytest.approx(0.25)


@pytest.mark.unit
class TestTissueEnergyDensityModel:
    def test_name_and_feedback_flag(self) -> None:
        model = TissueEnergyDensityModel()
        assert model.name
        assert model.includes_weight_dependent_feedback is False

    def test_default_blended_density(self) -> None:
        model = TissueEnergyDensityModel()
        assert model.energy_density_kcal_per_kg == pytest.approx(7380.0)

    def test_pure_fat_density_when_ffm_fraction_zero(self) -> None:
        model = TissueEnergyDensityModel(ffm_fraction=0.0)
        assert model.energy_density_kcal_per_kg == pytest.approx(9500.0)

    def test_pure_ffm_density_when_ffm_fraction_one(self) -> None:
        model = TissueEnergyDensityModel(ffm_fraction=1.0)
        assert model.energy_density_kcal_per_kg == pytest.approx(1020.0)

    def test_ffm_fraction_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            TissueEnergyDensityModel(ffm_fraction=-0.1)
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            TissueEnergyDensityModel(ffm_fraction=1.1)

    def test_deficit_rate_reference_value(self) -> None:
        # -500 / 7380 ~= -0.06775 kg/day
        model = TissueEnergyDensityModel()
        rate = model.mass_change_rate_kg_per_day(-500.0)
        assert rate == pytest.approx(-0.06775, abs=1e-4)

    def test_excess_weight_kg_is_ignored(self) -> None:
        # By design: weight-dependent feedback is expected to come
        # from the caller's own BMR recompute (Phase 9), not this
        # primitive.
        model = TissueEnergyDensityModel()
        rate_a = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=0.0)
        rate_b = model.mass_change_rate_kg_per_day(-500.0, excess_weight_kg=-30.0)
        assert rate_a == rate_b

    def test_higher_ffm_fraction_gives_lower_density_and_faster_rate(self) -> None:
        # Fat-free mass has much lower energy density than fat, so a
        # higher assumed FFM fraction should produce a *larger
        # magnitude* rate of change for the same caloric deficit.
        low_ffm_model = TissueEnergyDensityModel(ffm_fraction=0.1)
        high_ffm_model = TissueEnergyDensityModel(ffm_fraction=0.5)
        low_ffm_rate = abs(low_ffm_model.mass_change_rate_kg_per_day(-500.0))
        high_ffm_rate = abs(high_ffm_model.mass_change_rate_kg_per_day(-500.0))
        assert high_ffm_rate > low_ffm_rate

    def test_one_year_projection_reference_value(self) -> None:
        # -500 * 365 / 7380 ~= -24.73 kg
        model = TissueEnergyDensityModel()
        result = model.project_weight_change_kg(-500.0, 365)
        assert result == pytest.approx(-24.7290, abs=1e-3)

    def test_negative_days_rejected(self) -> None:
        model = TissueEnergyDensityModel()
        with pytest.raises(ValueError, match="non-negative"):
            model.project_weight_change_kg(-500.0, -1)
