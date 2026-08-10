"""Unit tests for metabosim.models.adaptive_thermogenesis.base.

Covers AdaptiveThermogenesisModel, the abstract strategy interface.
"""

import pytest

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel


@pytest.mark.unit
class TestAdaptiveThermogenesisModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            AdaptiveThermogenesisModel()  # type: ignore[abstract]

    def test_subclass_missing_method_cannot_be_instantiated(self) -> None:
        class IncompleteModel(AdaptiveThermogenesisModel):
            name = "Incomplete"

        with pytest.raises(TypeError):
            IncompleteModel()  # type: ignore[abstract]

    def test_concrete_subclass_is_callable(self) -> None:
        class FixedAdjustmentModel(AdaptiveThermogenesisModel):
            name = "Fixed -100 kcal"

            def calculate_adjustment_kcal(
                self,
                baseline_weight_kg: float,
                current_weight_kg: float,
                reference_expenditure_kcal: float,
            ) -> float:
                return -100.0

        model = FixedAdjustmentModel()
        assert model(100.0, 90.0, 2500.0) == pytest.approx(
            model.calculate_adjustment_kcal(100.0, 90.0, 2500.0)
        )

    def test_repr_includes_name(self) -> None:
        class NamedModel(AdaptiveThermogenesisModel):
            name = "My Custom Adaptation Model"

            def calculate_adjustment_kcal(
                self,
                baseline_weight_kg: float,
                current_weight_kg: float,
                reference_expenditure_kcal: float,
            ) -> float:
                return 0.0

        assert "My Custom Adaptation Model" in repr(NamedModel())
