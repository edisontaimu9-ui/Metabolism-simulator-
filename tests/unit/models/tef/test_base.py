"""Unit tests for metabosim.models.tef.base.TEFModel."""

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.base import TEFModel


@pytest.mark.unit
class TestTEFModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            TEFModel()  # type: ignore[abstract]

    def test_subclass_missing_calculate_cannot_be_instantiated(self) -> None:
        class IncompleteTEFModel(TEFModel):
            name = "Incomplete"

        with pytest.raises(TypeError):
            IncompleteTEFModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(
        self, mixed_diet: MacronutrientGrams
    ) -> None:
        class FixedFractionTEF(TEFModel):
            name = "Fixed 10%"

            def calculate(self, macros: MacronutrientGrams) -> float:
                return macros.energy_kcal * 0.10

        model = FixedFractionTEF()
        assert model(mixed_diet) == pytest.approx(model.calculate(mixed_diet))

    def test_repr_includes_name(self) -> None:
        class NamedTEF(TEFModel):
            name = "My Custom TEF Model"

            def calculate(self, macros: MacronutrientGrams) -> float:
                return 0.0

        assert "My Custom TEF Model" in repr(NamedTEF())
