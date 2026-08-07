"""Unit tests for metabosim.models.activity.iom_pal.

Reference values are hand-computed: AEE = BMR * (PAL - 1), using this
project's interpolated 5-tier table (1.2/1.4/1.6/1.8/2.2).
"""

import pytest

from metabosim.domain.enums import ActivityLevel, Sex
from metabosim.domain.person import Person
from metabosim.models.activity.iom_pal import IOMPALActivityModel, get_pal_value


@pytest.mark.unit
class TestGetPalValue:
    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            (ActivityLevel.SEDENTARY, 1.20),
            (ActivityLevel.LIGHT, 1.40),
            (ActivityLevel.MODERATE, 1.60),
            (ActivityLevel.ACTIVE, 1.80),
            (ActivityLevel.VERY_ACTIVE, 2.20),
        ],
    )
    def test_known_pal_values(self, level: ActivityLevel, expected: float) -> None:
        assert get_pal_value(level) == pytest.approx(expected)


@pytest.mark.unit
class TestIOMPALActivityModel:
    def test_name_and_tef_flag_are_set(self) -> None:
        model = IOMPALActivityModel()
        assert model.name
        assert model.includes_average_tef is True

    def test_sedentary_reference_value(self, sedentary_male_80kg: Person) -> None:
        # 1780.0 * (1.2 - 1) = 356.0
        model = IOMPALActivityModel()
        assert model.calculate(sedentary_male_80kg, 1780.0) == pytest.approx(356.0)

    def test_moderate_reference_value(self, moderate_male_80kg: Person) -> None:
        # 1780.0 * (1.6 - 1) = 1068.0
        model = IOMPALActivityModel()
        assert model.calculate(moderate_male_80kg, 1780.0) == pytest.approx(1068.0)

    def test_light_reference_value(self, light_female_60kg: Person) -> None:
        # 1345.25 * (1.4 - 1) = 538.1
        model = IOMPALActivityModel()
        result = model.calculate(light_female_60kg, 1345.25)
        assert result == pytest.approx(538.1)

    def test_zero_bmr_rejected(self, sedentary_male_80kg: Person) -> None:
        model = IOMPALActivityModel()
        with pytest.raises(ValueError, match="positive"):
            model.calculate(sedentary_male_80kg, 0.0)

    def test_negative_bmr_rejected(self, sedentary_male_80kg: Person) -> None:
        model = IOMPALActivityModel()
        with pytest.raises(ValueError, match="positive"):
            model.calculate(sedentary_male_80kg, -100.0)

    def test_aee_increases_monotonically_with_activity(self) -> None:
        model = IOMPALActivityModel()
        ordered_levels = [
            ActivityLevel.SEDENTARY,
            ActivityLevel.LIGHT,
            ActivityLevel.MODERATE,
            ActivityLevel.ACTIVE,
            ActivityLevel.VERY_ACTIVE,
        ]
        aee_values = []
        for level in ordered_levels:
            person = Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                activity_level=level,
            )
            aee_values.append(model.calculate(person, 1780.0))

        assert aee_values == sorted(aee_values)
        assert len(set(aee_values)) == len(aee_values)

    def test_aee_always_non_negative(self) -> None:
        model = IOMPALActivityModel()
        for level in ActivityLevel:
            person = Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                activity_level=level,
            )
            assert model.calculate(person, 1500.0) >= 0.0
