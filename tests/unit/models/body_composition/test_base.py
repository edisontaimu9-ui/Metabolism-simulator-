"""Unit tests for metabosim.models.body_composition.base.BodyCompositionModel."""

import pytest

from metabosim.domain.enums import Sex
from metabosim.models.body_composition.base import BodyCompositionModel


@pytest.mark.unit
class TestBodyCompositionModelInterface:
    def test_cannot_instantiate_abstract_base_directly(self) -> None:
        with pytest.raises(TypeError):
            BodyCompositionModel()  # type: ignore[abstract]

    def test_subclass_missing_ffm_fraction_cannot_be_instantiated(self) -> None:
        class IncompleteModel(BodyCompositionModel):
            name = "Incomplete"

        with pytest.raises(TypeError):
            IncompleteModel()  # type: ignore[abstract]

    def test_repr_includes_name(self) -> None:
        class NamedModel(BodyCompositionModel):
            name = "My Custom Body Composition Model"

            def ffm_fraction_of_change(
                self, current_fat_mass_kg: float, sex: Sex
            ) -> float:
                return 0.5

        assert "My Custom Body Composition Model" in repr(NamedModel())


@pytest.mark.unit
class TestPartitionMassChangeTemplateMethod:
    """partition_mass_change_kg is implemented once on the base class
    in terms of ffm_fraction_of_change -- these tests use a trivial
    fixed-fraction subclass to verify that template method's
    arithmetic directly, independent of any specific concrete model
    like ForbesPartitionModel.
    """

    class _FixedFractionModel(BodyCompositionModel):
        name = "Fixed fraction (test double)"

        def __init__(self, fraction: float) -> None:
            self.fraction = fraction

        def ffm_fraction_of_change(self, current_fat_mass_kg: float, sex: Sex) -> float:
            return self.fraction

    def test_partition_sums_to_total_change(self) -> None:
        model = self._FixedFractionModel(0.3)
        delta_fat, delta_lean = model.partition_mass_change_kg(-1.0, 20.0, Sex.FEMALE)
        assert delta_fat + delta_lean == pytest.approx(-1.0)

    def test_partition_respects_fraction(self) -> None:
        model = self._FixedFractionModel(0.25)
        delta_fat, delta_lean = model.partition_mass_change_kg(2.0, 20.0, Sex.MALE)
        assert delta_lean == pytest.approx(0.5)
        assert delta_fat == pytest.approx(1.5)

    def test_zero_fraction_puts_all_change_in_fat(self) -> None:
        model = self._FixedFractionModel(0.0)
        delta_fat, delta_lean = model.partition_mass_change_kg(1.0, 20.0, Sex.FEMALE)
        assert delta_fat == pytest.approx(1.0)
        assert delta_lean == pytest.approx(0.0)

    def test_one_fraction_puts_all_change_in_lean(self) -> None:
        model = self._FixedFractionModel(1.0)
        delta_fat, delta_lean = model.partition_mass_change_kg(1.0, 20.0, Sex.FEMALE)
        assert delta_fat == pytest.approx(0.0)
        assert delta_lean == pytest.approx(1.0)

    def test_negative_change_partitions_correctly(self) -> None:
        model = self._FixedFractionModel(0.4)
        delta_fat, delta_lean = model.partition_mass_change_kg(-2.0, 20.0, Sex.MALE)
        assert delta_lean == pytest.approx(-0.8)
        assert delta_fat == pytest.approx(-1.2)
