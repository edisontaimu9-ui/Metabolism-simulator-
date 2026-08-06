"""Unit tests for metabosim.models.tdee.base.TDEEModel."""

import pytest

from metabosim.models.tdee.base import TDEEModel


@pytest.mark.unit
class TestTDEEModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            TDEEModel()  # type: ignore[abstract]

    def test_subclass_missing_calculate_cannot_be_instantiated(self) -> None:
        class IncompleteTDEEModel(TDEEModel):
            name = "Incomplete"

        with pytest.raises(TypeError):
            IncompleteTDEEModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self, sedentary_male) -> None:  # type: ignore[no-untyped-def]
        class FixedMultiplierTDEE(TDEEModel):
            name = "Fixed x1.5"

            def calculate(self, person: object, bmr_kcal: float) -> float:
                return bmr_kcal * 1.5

        model = FixedMultiplierTDEE()
        # __call__ should delegate to calculate()
        assert model(sedentary_male, 1000.0) == pytest.approx(1500.0)

    def test_repr_includes_name(self) -> None:
        class NamedTDEE(TDEEModel):
            name = "My Custom Model"

            def calculate(self, person: object, bmr_kcal: float) -> float:
                return bmr_kcal

        assert "My Custom Model" in repr(NamedTDEE())
