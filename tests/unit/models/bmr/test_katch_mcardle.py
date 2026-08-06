"""Unit tests for metabosim.models.bmr.katch_mcardle.KatchMcArdleBMR."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR


@pytest.mark.unit
class TestKatchMcArdleBMR:
    def test_male_reference_value(self, male_with_bf: Person) -> None:
        # lean_mass_kg = 80 * (1 - 0.20) = 64.0
        # RMR = 370 + 21.6*64 = 370 + 1382.4 = 1752.4
        model = KatchMcArdleBMR()
        assert model.calculate(male_with_bf) == pytest.approx(1752.4)

    def test_female_reference_value(self, female_with_bf: Person) -> None:
        # lean_mass_kg = 60 * (1 - 0.30) = 42.0
        # RMR = 370 + 21.6*42 = 370 + 907.2 = 1277.2
        model = KatchMcArdleBMR()
        assert model.calculate(female_with_bf) == pytest.approx(1277.2)

    def test_requires_body_fat_flag_is_true(self) -> None:
        assert KatchMcArdleBMR.requires_body_fat is True

    def test_raises_value_error_without_body_fat(self, male_no_bf: Person) -> None:
        assert male_no_bf.body_fat_percent is None
        model = KatchMcArdleBMR()
        with pytest.raises(ValueError, match="requires Person.body_fat_percent"):
            model.calculate(male_no_bf)

    def test_result_is_positive(self, male_with_bf: Person) -> None:
        model = KatchMcArdleBMR()
        assert model.calculate(male_with_bf) > 0
