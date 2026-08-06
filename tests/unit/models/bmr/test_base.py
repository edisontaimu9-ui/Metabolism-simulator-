"""Unit tests for metabosim.models.bmr.base.BMRModel."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.bmr.base import BMRModel


class _DummyBMR(BMRModel):
    """Minimal concrete subclass for exercising the base contract."""

    name = "Dummy"
    requires_body_fat = False

    def calculate(self, person: Person) -> float:
        return 1234.5


@pytest.mark.unit
class TestBMRModelContract:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            BMRModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self) -> None:
        model = _DummyBMR()
        person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
        assert model(person) == model.calculate(person) == 1234.5

    def test_repr_includes_name(self) -> None:
        model = _DummyBMR()
        assert "Dummy" in repr(model)
