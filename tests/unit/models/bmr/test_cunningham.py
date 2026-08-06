"""Unit tests for metabosim.models.bmr.cunningham.CunninghamBMR."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.cunningham import CunninghamBMR


@pytest.mark.unit
class TestCunninghamBMR:
    def test_male_reference_value(self, male_with_bf: Person) -> None:
        # lean_mass_kg = 80 * (1 - 0.20) = 64.0
        # RMR = 500 + 22*64 = 500 + 1408 = 1908.0
        model = CunninghamBMR()
        assert model.calculate(male_with_bf) == pytest.approx(1908.0)

    def test_female_reference_value(self, female_with_bf: Person) -> None:
        # lean_mass_kg = 60 * (1 - 0.30) = 42.0
        # RMR = 500 + 22*42 = 500 + 924 = 1424.0
        model = CunninghamBMR()
        assert model.calculate(female_with_bf) == pytest.approx(1424.0)

    def test_requires_body_fat_flag_is_true(self) -> None:
        assert CunninghamBMR.requires_body_fat is True

    def test_raises_value_error_without_body_fat(self, male_no_bf: Person) -> None:
        model = CunninghamBMR()
        with pytest.raises(ValueError, match="requires Person.body_fat_percent"):
            model.calculate(male_no_bf)

    def test_cunningham_exceeds_katch_mcardle_for_same_lean_mass(
        self, male_with_bf: Person
    ) -> None:
        # Documented in both modules' docstrings: Cunningham (1980)
        # produces a higher estimate than Katch-McArdle for identical
        # lean mass. Cross-check that the two implementations actually
        # agree with their own documentation.
        from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR

        cunningham = CunninghamBMR().calculate(male_with_bf)
        katch_mcardle = KatchMcArdleBMR().calculate(male_with_bf)
        assert cunningham > katch_mcardle
