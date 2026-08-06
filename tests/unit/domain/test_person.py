"""Unit tests for metabosim.domain.person.Person."""

import pytest
from pydantic import ValidationError

from metabosim.domain.enums import ActivityLevel, Sex, UnitSystem
from metabosim.domain.person import Person


@pytest.fixture
def base_male() -> Person:
    """A standard 30-year-old male, 180cm, 80kg, no body fat % known."""
    return Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)


@pytest.fixture
def base_female_with_bf() -> Person:
    """A 28-year-old female with a known body fat percentage."""
    return Person(
        sex=Sex.FEMALE,
        age_years=28,
        height_cm=165,
        weight_kg=60,
        body_fat_percent=25.0,
    )


@pytest.mark.unit
class TestPersonConstruction:
    def test_minimal_valid_person(self, base_male: Person) -> None:
        assert base_male.sex == Sex.MALE
        assert base_male.age_years == 30
        assert base_male.height_cm == 180
        assert base_male.weight_kg == 80

    def test_defaults(self, base_male: Person) -> None:
        assert base_male.activity_level == ActivityLevel.SEDENTARY
        assert base_male.unit_system == UnitSystem.METRIC
        assert base_male.body_fat_percent is None
        assert base_male.name is None

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                made_up_field=123,
            )


@pytest.mark.unit
class TestPersonValidationBounds:
    @pytest.mark.parametrize("age", [-1, 131])
    def test_age_out_of_bounds_rejected(self, age: float) -> None:
        with pytest.raises(ValidationError):
            Person(sex=Sex.MALE, age_years=age, height_cm=180, weight_kg=80)

    @pytest.mark.parametrize("height", [10, 300])
    def test_height_out_of_bounds_rejected(self, height: float) -> None:
        with pytest.raises(ValidationError):
            Person(sex=Sex.MALE, age_years=30, height_cm=height, weight_kg=80)

    @pytest.mark.parametrize("weight", [0.0, 700])
    def test_weight_out_of_bounds_rejected(self, weight: float) -> None:
        with pytest.raises(ValidationError):
            Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=weight)

    @pytest.mark.parametrize("bf", [-5, 90])
    def test_body_fat_percent_out_of_bounds_rejected(self, bf: float) -> None:
        with pytest.raises(ValidationError):
            Person(
                sex=Sex.MALE,
                age_years=30,
                height_cm=180,
                weight_kg=80,
                body_fat_percent=bf,
            )

    def test_boundary_values_accepted(self) -> None:
        # Should not raise at the exact documented bounds.
        Person(sex=Sex.MALE, age_years=0, height_cm=25, weight_kg=0.3)
        Person(sex=Sex.MALE, age_years=130, height_cm=275, weight_kg=650)


@pytest.mark.unit
class TestPersonComputedFields:
    def test_bmi_known_value(self) -> None:
        # 70 kg at 175 cm -> BMI = 70 / 1.75^2 = 22.857...
        person = Person(sex=Sex.MALE, age_years=40, height_cm=175, weight_kg=70)
        assert person.bmi == pytest.approx(22.857, rel=1e-3)

    def test_fat_mass_and_lean_mass_none_when_bf_unknown(
        self, base_male: Person
    ) -> None:
        assert base_male.fat_mass_kg is None
        assert base_male.lean_mass_kg is None

    def test_fat_mass_and_lean_mass_computed_when_bf_known(
        self, base_female_with_bf: Person
    ) -> None:
        # 60 kg at 25% body fat -> 15 kg fat mass, 45 kg lean mass
        assert base_female_with_bf.fat_mass_kg == pytest.approx(15.0)
        assert base_female_with_bf.lean_mass_kg == pytest.approx(45.0)

    def test_fat_and_lean_mass_sum_to_weight(self, base_female_with_bf: Person) -> None:
        total = base_female_with_bf.fat_mass_kg + base_female_with_bf.lean_mass_kg
        assert total == pytest.approx(base_female_with_bf.weight_kg)


@pytest.mark.unit
class TestPersonSerialization:
    def test_model_dump_includes_computed_fields(
        self, base_female_with_bf: Person
    ) -> None:
        dumped = base_female_with_bf.model_dump()
        assert dumped["fat_mass_kg"] == pytest.approx(15.0)
        assert "bmi" in dumped

    def test_round_trip_json(self, base_male: Person) -> None:
        # NOTE: Person.model_dump_json() includes computed fields
        # (bmi, fat_mass_kg, lean_mass_kg), which are derived
        # read-only properties, not settable constructor inputs. With
        # extra="forbid" (deliberately strict, to catch input typos),
        # feeding the full dump back into model_validate_json would
        # correctly raise -- computed fields are not valid inputs.
        # The round-trip must therefore go through the *input* fields
        # only, which is what a real caller (CLI/API deserializing a
        # request) would do.
        input_fields = set(Person.model_fields.keys())
        raw = base_male.model_dump(mode="json", include=input_fields)
        restored = Person.model_validate(raw)
        assert restored.weight_kg == base_male.weight_kg
        assert restored.sex == base_male.sex
        assert restored.bmi == pytest.approx(base_male.bmi)
