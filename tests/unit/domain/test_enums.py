"""Unit tests for metabosim.domain.enums."""

import pytest

from metabosim.domain.enums import ActivityLevel, Sex, UnitSystem


@pytest.mark.unit
class TestSex:
    def test_values(self) -> None:
        assert Sex.MALE == "male"
        assert Sex.FEMALE == "female"

    def test_is_str_subclass(self) -> None:
        assert isinstance(Sex.MALE, str)

    def test_json_round_trip(self) -> None:
        import json

        assert json.loads(json.dumps(Sex.MALE.value)) == "male"


@pytest.mark.unit
class TestActivityLevel:
    def test_all_expected_tiers_present(self) -> None:
        expected = {"sedentary", "light", "moderate", "active", "very_active"}
        actual = {level.value for level in ActivityLevel}
        assert actual == expected

    def test_is_str_subclass(self) -> None:
        assert isinstance(ActivityLevel.MODERATE, str)


@pytest.mark.unit
class TestUnitSystem:
    def test_values(self) -> None:
        assert UnitSystem.METRIC == "metric"
        assert UnitSystem.IMPERIAL == "imperial"
