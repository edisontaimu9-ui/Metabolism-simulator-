"""Unit tests for metabosim.reports.document."""

import pytest

from metabosim.reports.data import ReportData
from metabosim.reports.document import (
    BulletList,
    Document,
    FigureBlock,
    Paragraph,
    Section,
    Table,
    _daily_rows_indices,
    build_document,
)


def _section(doc: Document, heading: str) -> Section:
    return next(s for s in doc.sections if s.heading == heading)


def _table(section: Section) -> Table:
    return next(b for b in section.blocks if isinstance(b, Table))


def _cells(table: Table) -> dict[str, str]:
    return {row[0]: row[1] for row in table.rows}


@pytest.mark.unit
class TestStructure:
    def test_section_order_without_figures(self, basic_data: ReportData) -> None:
        doc = build_document(basic_data)
        assert [s.heading for s in doc.sections] == [
            "Subject",
            "Models used",
            "Diet and activity",
            "Key results",
            "Daily results",
            "Interpretation and limitations",
            "References",
        ]

    def test_figures_section_inserted_before_daily(
        self, basic_data: ReportData
    ) -> None:
        fig = FigureBlock(key="weight", caption="c", png=b"x")
        doc = build_document(basic_data, [fig])
        headings = [s.heading for s in doc.sections]
        assert headings.index("Figures") == headings.index("Daily results") - 1
        assert _section(doc, "Figures").blocks == (fig,)

    def test_title_from_data(self, basic_data: ReportData) -> None:
        assert build_document(basic_data).title == basic_data.title

    def test_max_daily_rows_validated(self, basic_data: ReportData) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            build_document(basic_data, max_daily_rows=1)


@pytest.mark.unit
class TestSubject:
    def test_name_shown_when_set(self, full_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(full_data), "Subject")))
        assert cells["Name"] == "Test | *User*"

    def test_name_omitted_when_unset(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Subject")))
        assert "Name" not in cells

    def test_body_fat_not_provided(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Subject")))
        assert cells["Body fat"] == "Not provided"

    def test_body_fat_shown(self, full_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(full_data), "Subject")))
        assert cells["Body fat"] == "30.0 %"

    def test_start_date_shown_when_set(self, basic_data: ReportData) -> None:
        from datetime import date

        config = basic_data.config.model_copy(update={"start_date": date(2026, 1, 5)})
        data = basic_data.model_copy(update={"config": config})
        cells = _cells(_table(_section(build_document(data), "Subject")))
        assert cells["Start date"] == "2026-01-05"


@pytest.mark.unit
class TestModels:
    def test_model_names_and_ids_shown(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Models used")))
        assert "(mifflin_st_jeor)" in cells["BMR"]
        assert "(none)" in cells["Adaptive thermogenesis"]

    def test_body_composition_inactive_message(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Models used")))
        assert cells["Body composition"].startswith("Not active")
        assert cells["Glycogen"] == "Not tracked"

    def test_body_composition_and_glycogen_active(self, full_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(full_data), "Models used")))
        assert "(forbes)" in cells["Body composition"]
        assert cells["Glycogen"] == "Tracked (starting store 400 g)"


@pytest.mark.unit
class TestPlan:
    def test_uniform_plan_table(self, basic_data: ReportData) -> None:
        section = _section(build_document(basic_data), "Diet and activity")
        cells = _cells(_table(section))
        assert cells["Energy intake"] == "2430 kcal"
        assert cells["Protein"] == "150 g"
        assert any(
            isinstance(b, Paragraph) and "No physical activity" in b.text
            for b in section.blocks
        )

    def test_activity_entries_listed(self, full_data: ReportData) -> None:
        section = _section(build_document(full_data), "Diet and activity")
        tables = [b for b in section.blocks if isinstance(b, Table)]
        assert tables[1].rows == (("Run", "6.0", "1.00"),)

    def test_unlabeled_activity(self, basic_data: ReportData) -> None:
        from metabosim.models.activity.met_based import ActivityEntry
        from metabosim.simulation.config import DailyPlan

        plan = DailyPlan(
            macros=basic_data.daily_plans[0].macros,
            activity_entries=[ActivityEntry(met=3.0, duration_hours=0.5)],
        )
        data = basic_data.model_copy(
            update={"daily_plans": [plan] * basic_data.config.days}
        )
        section = _section(build_document(data), "Diet and activity")
        tables = [b for b in section.blocks if isinstance(b, Table)]
        assert tables[1].rows[0][0] == "Unlabeled"

    def test_varying_plan_summarised(self, varying_data: ReportData) -> None:
        section = _section(build_document(varying_data), "Diet and activity")
        assert len(section.blocks) == 1
        text = section.blocks[0]
        assert isinstance(text, Paragraph)
        assert "varied from day to day" in text.text
        assert "1650 to 2430 kcal" in text.text


@pytest.mark.unit
class TestResults:
    def test_core_rows(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Key results")))
        assert cells["Days simulated"] == "10"
        assert cells["Starting weight"] == "80.00 kg"
        assert cells["Total weight change"].startswith("+")
        assert "Fat mass" not in cells
        assert "Glycogen" not in cells

    def test_tracked_rows(self, full_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(full_data), "Key results")))
        assert "Fat mass" in cells
        assert "Lean mass" in cells
        assert "Glycogen" in cells

    def test_bmr_and_tdee_rows(self, basic_data: ReportData) -> None:
        cells = _cells(_table(_section(build_document(basic_data), "Key results")))
        assert "BMR (first day to final state)" in cells
        assert "TDEE (first day to final state)" in cells

    def test_bmr_tdee_rows_omitted_when_missing(self, basic_data: ReportData) -> None:
        states = [
            s.model_copy(update={"bmr_kcal": None, "tdee_kcal": None})
            for s in basic_data.states
        ]
        data = basic_data.model_copy(update={"states": states})
        cells = _cells(_table(_section(build_document(data), "Key results")))
        assert "BMR (first day to final state)" not in cells
        assert "TDEE (first day to final state)" not in cells


@pytest.mark.unit
class TestDailyRows:
    def test_all_rows_when_they_fit(self) -> None:
        assert _daily_rows_indices(11, 31) == list(range(11))

    def test_sampling_keeps_first_and_last(self) -> None:
        indices = _daily_rows_indices(366, 31)
        assert indices[0] == 0
        assert indices[-1] == 365
        assert len(indices) <= 31 + 1

    def test_sampling_appends_last_when_step_skips_it(self) -> None:
        indices = _daily_rows_indices(12, 5)
        assert indices[-1] == 11

    def test_sampling_exact_fit_does_not_duplicate_last(self) -> None:
        indices = _daily_rows_indices(7, 4)
        assert indices == [0, 2, 4, 6]

    def test_table_has_row_per_state_when_small(self, basic_data: ReportData) -> None:
        table = _table(_section(build_document(basic_data), "Daily results"))
        assert len(table.rows) == len(basic_data.states)
        assert table.headers == (
            "Day",
            "Weight (kg)",
            "Intake (kcal)",
            "Expenditure (kcal)",
            "Balance (kcal)",
        )

    def test_sampling_note_shown(self, full_data: ReportData) -> None:
        section = _section(
            build_document(full_data, max_daily_rows=10), "Daily results"
        )
        notes = [b.text for b in section.blocks if isinstance(b, Paragraph)]
        assert any(t.startswith("Showing ") for t in notes)
        table = _table(section)
        assert table.rows[0][0] == "0"
        assert table.rows[-1][0] == "60"

    def test_tracked_columns(self, full_data: ReportData) -> None:
        table = _table(_section(build_document(full_data), "Daily results"))
        assert table.headers[-3:] == ("Fat (kg)", "Lean (kg)", "Glycogen (g)")
        assert all(len(row) == len(table.headers) for row in table.rows)


@pytest.mark.unit
class TestLimitationsAndReferences:
    def _bullets(self, data: ReportData, heading: str) -> tuple[str, ...]:
        section = _section(build_document(data), heading)
        block = section.blocks[0]
        assert isinstance(block, BulletList)
        return block.items

    def test_no_adaptation_note(self, basic_data: ReportData) -> None:
        items = self._bullets(basic_data, "Interpretation and limitations")
        assert any("No metabolic adaptation" in i for i in items)
        assert not any("glycogen" in i.lower() for i in items)

    def test_adaptation_and_glycogen_notes(self, full_data: ReportData) -> None:
        items = self._bullets(full_data, "Interpretation and limitations")
        assert any("contested" in i for i in items)
        assert any("glycogen" in i.lower() for i in items)

    def test_not_clinical_advice_stated(self, basic_data: ReportData) -> None:
        items = self._bullets(basic_data, "Interpretation and limitations")
        assert any("not clinical advice" in i for i in items)

    def test_references_match_run(self, full_data: ReportData) -> None:
        items = self._bullets(full_data, "References")
        assert any("Fothergill" in i for i in items)
        assert any("Forbes" in i for i in items)
        assert any("Chow" in i for i in items)
