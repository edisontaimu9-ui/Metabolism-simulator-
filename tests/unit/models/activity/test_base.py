"""Unit tests for metabosim.models.activity.base.ActivityModel."""

import pytest

from metabosim.domain.person import Person
from metabosim.models.activity.base import ActivityModel


@pytest.mark.unit
class TestActivityModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            ActivityModel()  # type: ignore[abstract]

    def test_subclass_missing_calculate_cannot_be_instantiated(self) -> None:
        class IncompleteActivityModel(ActivityModel):
            name = "Incomplete"
            includes_average_tef = False

        with pytest.raises(TypeError):
            IncompleteActivityModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self, sedentary_male_80kg: Person) -> None:
        class FixedAEE(ActivityModel):
            name = "Fixed 300 kcal"
            includes_average_tef = False

            def calculate(self, person: Person, bmr_kcal: float) -> float:
                return 300.0

        model = FixedAEE()
        assert model(sedentary_male_80kg, 1600.0) == pytest.approx(
            model.calculate(sedentary_male_80kg, 1600.0)
        )

    def test_repr_includes_name(self) -> None:
        class NamedActivityModel(ActivityModel):
            name = "My Custom Activity Model"
            includes_average_tef = True

            def calculate(self, person: Person, bmr_kcal: float) -> float:
                return 0.0

        assert "My Custom Activity Model" in repr(NamedActivityModel())

    def test_includes_average_tef_must_be_declared_by_subclass(self) -> None:
        # Accessing includes_average_tef on a subclass that forgot to
        # set it should raise AttributeError (loud failure) rather
        # than silently defaulting to a guessed value -- this is a
        # deliberate design choice documented in the base class.
        class ForgetfulActivityModel(ActivityModel):
            name = "Forgot to set includes_average_tef"

            def calculate(self, person: Person, bmr_kcal: float) -> float:
                return 0.0

        model = ForgetfulActivityModel()
        with pytest.raises(AttributeError):
            _ = model.includes_average_tef
