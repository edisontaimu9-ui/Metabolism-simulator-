"""Unit tests for metabosim.models.disease.body_temperature.

Reference values hand-computed: adjustment = 0.13 * (temp_c - 37.0).
"""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.disease.body_temperature import (
    KI_PER_CELSIUS,
    NORMAL_BODY_TEMPERATURE_C,
    BodyTemperatureModifier,
)


@pytest.fixture
def person() -> Person:
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


@pytest.mark.unit
class TestConstants:
    def test_documented_values(self) -> None:
        assert KI_PER_CELSIUS == pytest.approx(0.13)
        assert NORMAL_BODY_TEMPERATURE_C == pytest.approx(37.0)


@pytest.mark.unit
class TestBodyTemperatureModifierConstruction:
    def test_normal_temperature_accepted(self) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=37.0)
        assert modifier.body_temperature_c == pytest.approx(37.0)

    def test_out_of_range_temperature_rejected(self) -> None:
        with pytest.raises(ValueError, match="physiologically survivable"):
            BodyTemperatureModifier(body_temperature_c=19.9)
        with pytest.raises(ValueError, match="physiologically survivable"):
            BodyTemperatureModifier(body_temperature_c=45.1)

    def test_boundary_temperatures_accepted(self) -> None:
        BodyTemperatureModifier(body_temperature_c=20.0)
        BodyTemperatureModifier(body_temperature_c=45.0)

    def test_custom_ki_accepted(self) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=39.0, ki_per_celsius=0.10)
        assert modifier.ki_per_celsius == pytest.approx(0.10)

    def test_name_reflects_fever(self) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=39.0)
        assert "fever" in modifier.name

    def test_name_reflects_hypothermia(self) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=34.0)
        assert "hypothermia" in modifier.name

    def test_name_reflects_normal(self) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=37.0)
        assert "normal" in modifier.name


@pytest.mark.unit
class TestBodyTemperatureModifierCalculation:
    def test_normal_temperature_gives_no_adjustment(self, person: Person) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=37.0)
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(1780.0)

    def test_fever_reference_value(self, person: Person) -> None:
        # 39C = +2C above normal -> 1780 * (1 + 0.13*2) = 1780*1.26 = 2242.8
        modifier = BodyTemperatureModifier(body_temperature_c=39.0)
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(2242.8)

    def test_hypothermia_reference_value(self, person: Person) -> None:
        # 35C = -2C below normal -> 1780 * (1 - 0.13*2) = 1780*0.74 = 1317.2
        modifier = BodyTemperatureModifier(body_temperature_c=35.0)
        assert modifier.apply_to_bmr_kcal(1780.0, person) == pytest.approx(1317.2)

    def test_higher_fever_produces_larger_increase(self, person: Person) -> None:
        low_fever = BodyTemperatureModifier(body_temperature_c=38.0)
        high_fever = BodyTemperatureModifier(body_temperature_c=40.0)
        low_result = low_fever.apply_to_bmr_kcal(1780.0, person)
        high_result = high_fever.apply_to_bmr_kcal(1780.0, person)
        assert high_result > low_result

    def test_symmetric_magnitude_above_and_below_normal(self, person: Person) -> None:
        fever = BodyTemperatureModifier(body_temperature_c=39.0)
        hypothermia = BodyTemperatureModifier(body_temperature_c=35.0)
        fever_delta = fever.apply_to_bmr_kcal(1780.0, person) - 1780.0
        hypothermia_delta = 1780.0 - hypothermia.apply_to_bmr_kcal(1780.0, person)
        assert fever_delta == pytest.approx(hypothermia_delta)

    def test_custom_ki_changes_magnitude(self, person: Person) -> None:
        default_ki = BodyTemperatureModifier(body_temperature_c=39.0)
        custom_ki = BodyTemperatureModifier(
            body_temperature_c=39.0, ki_per_celsius=0.10
        )
        default_result = default_ki.apply_to_bmr_kcal(1780.0, person)
        custom_result = custom_ki.apply_to_bmr_kcal(1780.0, person)
        assert custom_result < default_result

    def test_non_positive_base_bmr_rejected(self, person: Person) -> None:
        modifier = BodyTemperatureModifier(body_temperature_c=39.0)
        with pytest.raises(ValueError, match="positive"):
            modifier.apply_to_bmr_kcal(0.0, person)
        with pytest.raises(ValueError, match="positive"):
            modifier.apply_to_bmr_kcal(-50.0, person)
