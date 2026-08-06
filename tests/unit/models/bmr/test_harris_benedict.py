"""Unit tests for metabosim.models.bmr.harris_benedict.HarrisBenedictBMR."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.harris_benedict import HarrisBenedictBMR


@pytest.mark.unit
class TestHarrisBenedictBMR:
    def test_male_reference_value(self, male_no_bf: Person) -> None:
        # 88.362 + 13.397*80 + 4.799*180 - 5.677*30
        # = 88.362 + 1071.76 + 863.82 - 170.31 = 1853.632
        model = HarrisBenedictBMR()
        assert model.calculate(male_no_bf) == pytest.approx(1853.632, rel=1e-6)

    def test_female_reference_value(self, female_no_bf: Person) -> None:
        # 447.593 + 9.247*60 + 3.098*165 - 4.330*25
        # = 447.593 + 554.82 + 511.17 - 108.25 = 1405.333
        model = HarrisBenedictBMR()
        assert model.calculate(female_no_bf) == pytest.approx(1405.333, rel=1e-6)

    def test_does_not_require_body_fat(self) -> None:
        assert HarrisBenedictBMR.requires_body_fat is False

    def test_result_is_positive_for_valid_adult(
        self, male_no_bf: Person, female_no_bf: Person
    ) -> None:
        model = HarrisBenedictBMR()
        assert model.calculate(male_no_bf) > 0
        assert model.calculate(female_no_bf) > 0

    def test_name_is_descriptive(self) -> None:
        assert "Harris" in HarrisBenedictBMR.name
