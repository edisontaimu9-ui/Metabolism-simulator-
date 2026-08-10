"""Unit tests for metabosim.models.adaptive_thermogenesis.none."""

import pytest

from metabosim.models.adaptive_thermogenesis.none import NoAdaptiveThermogenesisModel


@pytest.mark.unit
class TestNoAdaptiveThermogenesisModel:
    def test_name_is_set(self) -> None:
        assert NoAdaptiveThermogenesisModel.name

    def test_always_returns_zero(self) -> None:
        model = NoAdaptiveThermogenesisModel()
        assert model.calculate_adjustment_kcal(100.0, 90.0, 2500.0) == 0.0
        assert model.calculate_adjustment_kcal(100.0, 110.0, 2500.0) == 0.0
        assert model.calculate_adjustment_kcal(100.0, 100.0, 2500.0) == 0.0
        assert model.calculate_adjustment_kcal(80.0, 40.0, 1000.0) == 0.0
