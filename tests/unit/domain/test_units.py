"""Unit tests for metabosim.domain.units."""

import pytest

from metabosim.domain.units import (
    cm_to_ft_in,
    cm_to_in,
    ft_in_to_cm,
    in_to_cm,
    kcal_to_kj,
    kg_to_lb,
    kj_to_kcal,
    lb_to_kg,
)


@pytest.mark.unit
class TestMassConversion:
    def test_kg_to_lb_known_value(self) -> None:
        # 1 kg == 2.2046226... lb
        assert kg_to_lb(1.0) == pytest.approx(2.20462, rel=1e-4)

    def test_lb_to_kg_known_value(self) -> None:
        # 1 lb == 0.45359237 kg exactly
        assert lb_to_kg(1.0) == pytest.approx(0.45359237, rel=1e-9)

    def test_round_trip(self) -> None:
        original = 83.7
        assert lb_to_kg(kg_to_lb(original)) == pytest.approx(original, rel=1e-9)


@pytest.mark.unit
class TestLengthConversion:
    def test_cm_to_in_known_value(self) -> None:
        # 2.54 cm == 1 in exactly
        assert cm_to_in(2.54) == pytest.approx(1.0, rel=1e-9)

    def test_in_to_cm_known_value(self) -> None:
        assert in_to_cm(1.0) == pytest.approx(2.54, rel=1e-9)

    def test_cm_to_ft_in(self) -> None:
        # 180 cm ~= 5 ft 10.87 in
        feet, inches = cm_to_ft_in(180.0)
        assert feet == 5
        assert inches == pytest.approx(10.866, rel=1e-3)

    def test_ft_in_to_cm_round_trip(self) -> None:
        feet, inches = cm_to_ft_in(175.0)
        assert ft_in_to_cm(feet, inches) == pytest.approx(175.0, rel=1e-9)


@pytest.mark.unit
class TestEnergyConversion:
    def test_kcal_to_kj_known_value(self) -> None:
        # 1 kcal == 4.184 kJ exactly (thermochemical calorie definition)
        assert kcal_to_kj(1.0) == pytest.approx(4.184, rel=1e-9)

    def test_kj_to_kcal_known_value(self) -> None:
        assert kj_to_kcal(4.184) == pytest.approx(1.0, rel=1e-9)

    def test_round_trip(self) -> None:
        original = 2000.0
        assert kj_to_kcal(kcal_to_kj(original)) == pytest.approx(original, rel=1e-9)
