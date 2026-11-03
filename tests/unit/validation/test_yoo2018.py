"""Unit tests for metabosim.validation.yoo2018 (fast paths only; the
full ten-year check lives in tests/validation)."""

import pytest

from metabosim.validation import yoo2018


@pytest.mark.unit
class TestYoo2018:
    def test_short_run_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 730"):
            yoo2018.run_yoo_2018_check(days=100)

    def test_plan_scaled_to_requested_intake(self) -> None:
        plan = yoo2018._plan_for_intake(2000.0)
        assert plan.macros.energy_kcal == pytest.approx(2000.0)
        assert len(plan.activity_entries) == 1

    def test_returns_two_named_results(self) -> None:
        results = yoo2018.run_yoo_2018_check(days=800)
        assert [r.name for r in results] == [
            "yoo_2018_steady_state_weight",
            "yoo_2018_trajectory_settled",
        ]

    def test_citation_mentions_source(self) -> None:
        assert "Yoo S" in yoo2018.CITATION
