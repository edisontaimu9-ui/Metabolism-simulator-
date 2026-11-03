"""Unit tests for metabosim.reports.data."""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.reports.data import ReportData, build_report_data
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator


def _sim(days: int = 5, name: str | None = None) -> Simulator:
    person = Person(name=name, sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
    plan = DailyPlan(
        macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
    )
    return Simulator(person, SimulationConfig(days=days), plan)


@pytest.mark.unit
class TestBuildReportData:
    def test_default_title(self) -> None:
        sim = _sim()
        assert build_report_data(sim, sim.run()).title == "Metabolism Simulation Report"

    def test_title_includes_subject_name(self) -> None:
        sim = _sim(name="Amina")
        data = build_report_data(sim, sim.run())
        assert data.title == "Metabolism Simulation Report: Amina"

    def test_explicit_title_wins(self) -> None:
        sim = _sim(name="Amina")
        assert build_report_data(sim, sim.run(), title="Custom").title == "Custom"

    def test_summary_matches_states(self) -> None:
        sim = _sim(days=7)
        states = sim.run()
        data = build_report_data(sim, states)
        assert data.summary.days_simulated == 7
        assert data.summary.ending_weight_kg == pytest.approx(states[-1].weight_kg)

    def test_carries_initial_glycogen(self) -> None:
        sim = _sim()
        sim.initial_glycogen_g = 350.0
        assert build_report_data(sim, sim.run()).initial_glycogen_g == 350.0

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            build_report_data(_sim(), [])

    def test_states_from_different_run_rejected(self) -> None:
        sim = _sim(days=5)
        other_states = _sim(days=9).run()
        with pytest.raises(ValueError, match="config.days"):
            build_report_data(sim, other_states)


@pytest.mark.unit
class TestReportData:
    def test_wrong_plan_count_rejected(self, basic_data: ReportData) -> None:
        with pytest.raises(ValueError, match="daily_plans"):
            ReportData(
                person=basic_data.person,
                config=basic_data.config,
                daily_plans=basic_data.daily_plans[:-1],
                states=basic_data.states,
                summary=basic_data.summary,
            )

    def test_uniform_plan_detected(self, basic_data: ReportData) -> None:
        assert basic_data.plan_is_uniform is True

    def test_varying_plan_detected(self, varying_data: ReportData) -> None:
        assert varying_data.plan_is_uniform is False

    def test_is_frozen(self, basic_data: ReportData) -> None:
        with pytest.raises(ValueError):
            basic_data.title = "x"  # type: ignore[misc]
