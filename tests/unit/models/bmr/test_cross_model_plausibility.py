"""Cross-cutting comparison and plausibility tests across all BMR
models, complementing the per-equation reference-value tests.

These tests check properties that should hold across *any* correct
BMR implementation, rather than one specific equation's numeric
output -- e.g. "BMR should increase with weight, holding everything
else fixed" is a property every equation in this package satisfies by
construction.
"""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.bmr.cunningham import CunninghamBMR
from metabosim.models.bmr.elia_organ_based import EliaOrganBasedBMR
from metabosim.models.bmr.harris_benedict import HarrisBenedictBMR
from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR
from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR

_WEIGHT_INDEPENDENT_MODELS = [MifflinStJeorBMR, HarrisBenedictBMR]
_LEAN_MASS_MODELS = [KatchMcArdleBMR, CunninghamBMR, EliaOrganBasedBMR]
_ALL_MODELS = _WEIGHT_INDEPENDENT_MODELS + _LEAN_MASS_MODELS


@pytest.mark.unit
class TestCrossModelPlausibility:
    @pytest.mark.parametrize("model_cls", _ALL_MODELS)
    def test_bmr_is_positive_for_typical_adult(self, model_cls: type) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=35,
            height_cm=175,
            weight_kg=75,
            body_fat_percent=18.0,
        )
        model = model_cls()
        assert model.calculate(person) > 0

    @pytest.mark.parametrize("model_cls", _WEIGHT_INDEPENDENT_MODELS)
    def test_bmr_increases_with_weight(self, model_cls: type) -> None:
        lighter = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=70)
        heavier = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=90)
        model = model_cls()
        assert model.calculate(heavier) > model.calculate(lighter)

    @pytest.mark.parametrize("model_cls", _WEIGHT_INDEPENDENT_MODELS)
    def test_bmr_decreases_with_age(self, model_cls: type) -> None:
        younger = Person(sex=Sex.MALE, age_years=25, height_cm=180, weight_kg=80)
        older = Person(sex=Sex.MALE, age_years=60, height_cm=180, weight_kg=80)
        model = model_cls()
        assert model.calculate(younger) > model.calculate(older)

    @pytest.mark.parametrize("model_cls", _LEAN_MASS_MODELS)
    def test_bmr_increases_with_lean_mass(self, model_cls: type) -> None:
        leaner = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=30.0,  # lean mass = 56 kg
        )
        more_muscular = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=10.0,  # lean mass = 72 kg
        )
        model = model_cls()
        assert model.calculate(more_muscular) > model.calculate(leaner)

    @pytest.mark.parametrize("model_cls", _LEAN_MASS_MODELS)
    def test_lean_mass_models_are_sex_independent(self, model_cls: type) -> None:
        # Same weight, height, age, and body fat % for both sexes ->
        # identical lean mass -> identical BMR, since Katch-McArdle and
        # Cunningham are driven purely by lean mass.
        male = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=175,
            weight_kg=70,
            body_fat_percent=20.0,
        )
        female = Person(
            sex=Sex.FEMALE,
            age_years=30,
            height_cm=175,
            weight_kg=70,
            body_fat_percent=20.0,
        )
        model = model_cls()
        assert model.calculate(male) == pytest.approx(model.calculate(female))

    def test_all_models_agree_within_a_plausible_range(self) -> None:
        # For a typical adult, no two BMR equations in clinical use
        # should disagree wildly. This is a coarse sanity check, not a
        # precision claim -- literature-based validation against real
        # published datasets is Phase 17's job, not this test's.
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        results = [model_cls().calculate(person) for model_cls in _ALL_MODELS]
        assert max(results) - min(results) < 300.0
