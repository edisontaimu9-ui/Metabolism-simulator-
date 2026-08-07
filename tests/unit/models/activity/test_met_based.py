"""Unit tests for metabosim.models.activity.met_based.

Reference values are hand-computed:
  gross_kcal = MET * weight_kg * duration_hours
  net_kcal   = (MET - 1) * weight_kg * duration_hours
"""

import pytest
from pydantic import ValidationError

from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry, METBasedActivityModel


@pytest.mark.unit
class TestActivityEntry:
    def test_gross_energy_kcal_known_value(self) -> None:
        # 6 MET, 80kg, 1 hour -> 6*80*1 = 480
        entry = ActivityEntry(met=6.0, duration_hours=1.0)
        assert entry.gross_energy_kcal(80.0) == pytest.approx(480.0)

    def test_net_energy_kcal_known_value(self) -> None:
        # (6-1)*80*1 = 400
        entry = ActivityEntry(met=6.0, duration_hours=1.0)
        assert entry.net_energy_kcal(80.0) == pytest.approx(400.0)

    def test_resting_met_gives_zero_net_energy(self) -> None:
        # MET of exactly 1.0 (quiet sitting) has zero net cost above
        # rest, by definition.
        entry = ActivityEntry(met=1.0, duration_hours=5.0)
        assert entry.net_energy_kcal(70.0) == pytest.approx(0.0)

    def test_non_positive_met_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ActivityEntry(met=0.0, duration_hours=1.0)
        with pytest.raises(ValidationError):
            ActivityEntry(met=-2.0, duration_hours=1.0)

    def test_non_positive_duration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ActivityEntry(met=3.0, duration_hours=0.0)

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            ActivityEntry(met=3.0, duration_hours=1.0, unexpected_field=1)


@pytest.mark.unit
class TestMETBasedActivityModel:
    def test_name_and_tef_flag_are_set(self) -> None:
        model = METBasedActivityModel(entries=[])
        assert model.name
        assert model.includes_average_tef is False

    def test_empty_log_gives_zero_aee(self, sedentary_male_80kg: Person) -> None:
        model = METBasedActivityModel(entries=[])
        assert model.calculate(sedentary_male_80kg, 1600.0) == pytest.approx(0.0)

    def test_single_entry_reference_value(self, sedentary_male_80kg: Person) -> None:
        entries = [ActivityEntry(met=6.0, duration_hours=1.0, label="jogging")]
        model = METBasedActivityModel(entries=entries)
        # (6-1)*80*1 = 400
        assert model.calculate(sedentary_male_80kg, 1600.0) == pytest.approx(400.0)

    def test_multiple_entries_sum_correctly(self, sedentary_male_80kg: Person) -> None:
        entries = [
            ActivityEntry(met=6.0, duration_hours=1.0, label="jogging"),
            ActivityEntry(met=1.5, duration_hours=8.0, label="light desk work"),
        ]
        model = METBasedActivityModel(entries=entries)
        # (6-1)*80*1 + (1.5-1)*80*8 = 400 + 320 = 720
        assert model.calculate(sedentary_male_80kg, 1600.0) == pytest.approx(720.0)

    def test_bmr_kcal_argument_is_ignored(self, sedentary_male_80kg: Person) -> None:
        # MET-based AEE must not depend on the supplied bmr_kcal value
        # at all -- verifying this is the whole point of the "safe to
        # combine with TEF" property.
        entries = [ActivityEntry(met=4.0, duration_hours=2.0)]
        model = METBasedActivityModel(entries=entries)
        result_a = model.calculate(sedentary_male_80kg, bmr_kcal=1000.0)
        result_b = model.calculate(sedentary_male_80kg, bmr_kcal=5000.0)
        assert result_a == result_b

    def test_total_duration_hours_property(self) -> None:
        entries = [
            ActivityEntry(met=6.0, duration_hours=1.0),
            ActivityEntry(met=1.5, duration_hours=8.0),
        ]
        model = METBasedActivityModel(entries=entries)
        assert model.total_duration_hours == pytest.approx(9.0)

    def test_uses_person_weight_not_fixed_value(self) -> None:
        from metabosim.domain.enums import Sex

        entries = [ActivityEntry(met=6.0, duration_hours=1.0)]
        model = METBasedActivityModel(entries=entries)

        light_person = Person(sex=Sex.FEMALE, age_years=25, height_cm=160, weight_kg=50)
        heavy_person = Person(sex=Sex.MALE, age_years=25, height_cm=190, weight_kg=110)

        aee_light = model.calculate(light_person, bmr_kcal=1400.0)
        aee_heavy = model.calculate(heavy_person, bmr_kcal=2000.0)
        assert aee_heavy > aee_light
