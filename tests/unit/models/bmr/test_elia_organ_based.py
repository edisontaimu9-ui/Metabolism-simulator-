"""Unit tests for metabosim.models.bmr.elia_organ_based.EliaOrganBasedBMR."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.elia_organ_based import EliaOrganBasedBMR
from metabosim.models.organ.elia import calculate_organ_bmr_breakdown_kcal


@pytest.mark.unit
class TestEliaOrganBasedBMR:
    def test_name_and_requires_body_fat_flag(self) -> None:
        assert EliaOrganBasedBMR.name
        assert EliaOrganBasedBMR.requires_body_fat is True

    def test_reference_value_matches_organ_breakdown_total(
        self, male_with_bf: Person
    ) -> None:
        model = EliaOrganBasedBMR()
        result = model.calculate(male_with_bf)
        expected = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=male_with_bf.fat_mass_kg,
            lean_mass_kg=male_with_bf.lean_mass_kg,
            age_years=male_with_bf.age_years,
        ).total_kcal
        assert result == pytest.approx(expected)

    def test_missing_body_fat_percent_raises_clear_error(
        self, male_no_bf: Person
    ) -> None:
        model = EliaOrganBasedBMR()
        with pytest.raises(ValueError, match="body_fat_percent"):
            model.calculate(male_no_bf)

    def test_female_with_bf_also_works(self, female_with_bf: Person) -> None:
        model = EliaOrganBasedBMR()
        result = model.calculate(female_with_bf)
        assert result > 0.0

    def test_result_is_positive(self, male_with_bf: Person) -> None:
        model = EliaOrganBasedBMR()
        assert model.calculate(male_with_bf) > 0.0

    def test_callable_alias_matches_calculate(self, male_with_bf: Person) -> None:
        model = EliaOrganBasedBMR()
        assert model(male_with_bf) == model.calculate(male_with_bf)
