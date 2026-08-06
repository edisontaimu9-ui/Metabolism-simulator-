"""Unit tests for metabosim.models.bmr.mifflin_st_jeor.MifflinStJeorBMR."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR


@pytest.mark.unit
class TestMifflinStJeorBMR:
    def test_male_reference_value(self, male_no_bf: Person) -> None:
        # 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
        model = MifflinStJeorBMR()
        assert model.calculate(male_no_bf) == pytest.approx(1780.0)

    def test_female_reference_value(self, female_no_bf: Person) -> None:
        # 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        model = MifflinStJeorBMR()
        assert model.calculate(female_no_bf) == pytest.approx(1345.25)

    def test_does_not_require_body_fat(self) -> None:
        assert MifflinStJeorBMR.requires_body_fat is False

    def test_works_without_body_fat_percent(self, male_no_bf: Person) -> None:
        assert male_no_bf.body_fat_percent is None
        model = MifflinStJeorBMR()
        # Should not raise even though body_fat_percent is unset.
        assert model.calculate(male_no_bf) > 0

    def test_result_is_positive_for_valid_adult(
        self, male_no_bf: Person, female_no_bf: Person
    ) -> None:
        model = MifflinStJeorBMR()
        assert model.calculate(male_no_bf) > 0
        assert model.calculate(female_no_bf) > 0

    def test_name_is_descriptive(self) -> None:
        assert "Mifflin" in MifflinStJeorBMR.name
