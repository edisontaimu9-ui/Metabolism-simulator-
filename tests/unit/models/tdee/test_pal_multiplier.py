"""Unit tests for metabosim.models.tdee.pal_multiplier.

Reference values are hand-computed: TDEE = BMR x multiplier, where the
multiplier table is 1.2 / 1.375 / 1.55 / 1.725 / 1.9 for
sedentary/light/moderate/active/very_active respectively (see module
docstring for citation).
"""

import pytest

from metabosim.domain.enums import ActivityLevel, Sex
from metabosim.domain.person import Person
from metabosim.models.tdee.pal_multiplier import (
    PALMultiplierTDEE,
    get_activity_multiplier,
)


@pytest.mark.unit
class TestGetActivityMultiplier:
    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            (ActivityLevel.SEDENTARY, 1.200),
            (ActivityLevel.LIGHT, 1.375),
            (ActivityLevel.MODERATE, 1.550),
            (ActivityLevel.ACTIVE, 1.725),
            (ActivityLevel.VERY_ACTIVE, 1.900),
        ],
    )
    def test_known_multiplier_values(
        self, level: ActivityLevel, expected: float
    ) -> None:
        assert get_activity_multiplier(level) == pytest.approx(expected)


@pytest.mark.unit
class TestPALMultiplierTDEE:
    def test_name_is_set(self) -> None:
        assert PALMultiplierTDEE.name

    def test_sedentary_reference_value(self, sedentary_male: Person) -> None:
        # BMR 1780.0 (Mifflin-St Jeor, see bmr tests) x 1.2 = 2136.0
        model = PALMultiplierTDEE()
        assert model.calculate(sedentary_male, 1780.0) == pytest.approx(2136.0)

    def test_moderate_reference_value(self, moderate_male: Person) -> None:
        # 1780.0 x 1.55 = 2759.0
        model = PALMultiplierTDEE()
        assert model.calculate(moderate_male, 1780.0) == pytest.approx(2759.0)

    def test_very_active_reference_value(self, very_active_female: Person) -> None:
        # Arbitrary BMR of 1345.25 (see bmr tests) x 1.9 = 2555.975
        model = PALMultiplierTDEE()
        result = model.calculate(very_active_female, 1345.25)
        assert result == pytest.approx(2555.975)

    def test_zero_bmr_rejected(self, sedentary_male: Person) -> None:
        model = PALMultiplierTDEE()
        with pytest.raises(ValueError, match="positive"):
            model.calculate(sedentary_male, 0.0)

    def test_negative_bmr_rejected(self, sedentary_male: Person) -> None:
        model = PALMultiplierTDEE()
        with pytest.raises(ValueError, match="positive"):
            model.calculate(sedentary_male, -500.0)

    def test_callable_alias_matches_calculate(self, moderate_male: Person) -> None:
        model = PALMultiplierTDEE()
        assert model(moderate_male, 1780.0) == model.calculate(moderate_male, 1780.0)

    def test_tdee_always_at_least_bmr(self) -> None:
        # Sanity property: TDEE must never be less than BMR, since
        # every published multiplier in the table is >= 1.0.
        model = PALMultiplierTDEE()
        for level in ActivityLevel:
            person = Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                activity_level=level,
            )
            assert model.calculate(person, 1500.0) >= 1500.0

    def test_tdee_increases_monotonically_with_activity(self) -> None:
        model = PALMultiplierTDEE()
        ordered_levels = [
            ActivityLevel.SEDENTARY,
            ActivityLevel.LIGHT,
            ActivityLevel.MODERATE,
            ActivityLevel.ACTIVE,
            ActivityLevel.VERY_ACTIVE,
        ]
        tdee_values = []
        for level in ordered_levels:
            person = Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                activity_level=level,
            )
            tdee_values.append(model.calculate(person, 1780.0))

        assert tdee_values == sorted(tdee_values)
        # And strictly increasing (no ties in the published table).
        assert len(set(tdee_values)) == len(tdee_values)
