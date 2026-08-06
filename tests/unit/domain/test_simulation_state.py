"""Unit tests for metabosim.domain.simulation_state.SimulationState."""

from datetime import date

import pytest
from pydantic import ValidationError

from metabosim.domain.simulation_state import SimulationState


@pytest.mark.unit
class TestSimulationStateConstruction:
    def test_minimal_valid_state(self) -> None:
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            energy_intake_kcal=2500.0,
            energy_expenditure_kcal=2400.0,
        )
        assert state.day_index == 0
        assert state.weight_kg == 80.0

    def test_with_full_composition(self) -> None:
        state = SimulationState(
            day_index=10,
            date=date(2026, 1, 11),
            weight_kg=80.0,
            fat_mass_kg=20.0,
            lean_mass_kg=60.0,
            glycogen_g=400.0,
            total_body_water_kg=45.0,
            energy_intake_kcal=2200.0,
            energy_expenditure_kcal=2500.0,
            bmr_kcal=1700.0,
            tdee_kcal=2500.0,
            adaptive_thermogenesis_kcal=-50.0,
        )
        assert state.fat_mass_kg == 20.0
        assert state.lean_mass_kg == 60.0


@pytest.mark.unit
class TestSimulationStateValidation:
    def test_negative_day_index_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SimulationState(
                day_index=-1,
                weight_kg=80.0,
                energy_intake_kcal=2000.0,
                energy_expenditure_kcal=2000.0,
            )

    def test_zero_or_negative_weight_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SimulationState(
                day_index=0,
                weight_kg=0.0,
                energy_intake_kcal=2000.0,
                energy_expenditure_kcal=2000.0,
            )

    def test_negative_intake_or_expenditure_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SimulationState(
                day_index=0,
                weight_kg=80.0,
                energy_intake_kcal=-100.0,
                energy_expenditure_kcal=2000.0,
            )

    def test_composition_mismatch_rejected(self) -> None:
        # fat_mass_kg + lean_mass_kg (100) far from weight_kg (80)
        with pytest.raises(ValidationError):
            SimulationState(
                day_index=0,
                weight_kg=80.0,
                fat_mass_kg=40.0,
                lean_mass_kg=60.0,
                energy_intake_kcal=2000.0,
                energy_expenditure_kcal=2000.0,
            )

    def test_composition_within_tolerance_accepted(self) -> None:
        # 20 + 60.03 = 80.03, within the 0.05 kg tolerance of weight_kg=80
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            fat_mass_kg=20.0,
            lean_mass_kg=60.03,
            energy_intake_kcal=2000.0,
            energy_expenditure_kcal=2000.0,
        )
        assert state.weight_kg == 80.0

    def test_only_one_composition_field_set_is_allowed(self) -> None:
        # Partial composition info (e.g. only fat mass known) should not
        # trigger the cross-field consistency check.
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            fat_mass_kg=20.0,
            energy_intake_kcal=2000.0,
            energy_expenditure_kcal=2000.0,
        )
        assert state.lean_mass_kg is None


@pytest.mark.unit
class TestSimulationStateComputedFields:
    def test_energy_balance_surplus(self) -> None:
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            energy_intake_kcal=2800.0,
            energy_expenditure_kcal=2500.0,
        )
        assert state.energy_balance_kcal == pytest.approx(300.0)

    def test_energy_balance_deficit(self) -> None:
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            energy_intake_kcal=1800.0,
            energy_expenditure_kcal=2500.0,
        )
        assert state.energy_balance_kcal == pytest.approx(-700.0)

    def test_energy_balance_maintenance(self) -> None:
        state = SimulationState(
            day_index=0,
            weight_kg=80.0,
            energy_intake_kcal=2500.0,
            energy_expenditure_kcal=2500.0,
        )
        assert state.energy_balance_kcal == pytest.approx(0.0)
