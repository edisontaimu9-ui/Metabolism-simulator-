"""Unit tests for metabosim.reports.writers."""

from pathlib import Path

import pytest

from metabosim.reports.data import ReportData
from metabosim.reports.writers import save_html_report, save_markdown_report


@pytest.mark.unit
class TestSaveMarkdownReport:
    def test_writes_report_and_figures(
        self, full_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_markdown_report(full_data, tmp_path / "run.md")
        assert path == tmp_path / "run.md"
        text = path.read_text(encoding="utf-8")
        assert "![" in text and "(run_figures/weight.png)" in text
        figure_dir = tmp_path / "run_figures"
        assert (figure_dir / "weight.png").read_bytes().startswith(b"\x89PNG")
        assert (figure_dir / "glycogen.png").exists()

    def test_creates_parent_directories(
        self, basic_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_markdown_report(basic_data, tmp_path / "a" / "b" / "r.md")
        assert path.exists()

    def test_without_figures_writes_no_figure_dir(
        self, basic_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_markdown_report(
            basic_data, tmp_path / "r.md", include_figures=False
        )
        assert not (tmp_path / "r_figures").exists()
        assert "![" not in path.read_text(encoding="utf-8")

    def test_accepts_string_path(self, basic_data: ReportData, tmp_path: Path) -> None:
        path = save_markdown_report(basic_data, str(tmp_path / "s.md"))
        assert path.exists()

    def test_max_daily_rows_respected(
        self, full_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_markdown_report(
            full_data, tmp_path / "r.md", include_figures=False, max_daily_rows=5
        )
        assert "Showing " in path.read_text(encoding="utf-8")


@pytest.mark.unit
class TestSaveHtmlReport:
    def test_writes_self_contained_file(
        self, full_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_html_report(full_data, tmp_path / "run.html")
        text = path.read_text(encoding="utf-8")
        assert text.startswith("<!DOCTYPE html>")
        assert "data:image/png;base64," in text
        assert list(tmp_path.iterdir()) == [path]

    def test_without_figures(self, basic_data: ReportData, tmp_path: Path) -> None:
        path = save_html_report(basic_data, tmp_path / "r.html", include_figures=False)
        assert "data:image/png" not in path.read_text(encoding="utf-8")

    def test_creates_parent_directories(
        self, basic_data: ReportData, tmp_path: Path
    ) -> None:
        path = save_html_report(
            basic_data, tmp_path / "x" / "r.html", include_figures=False
        )
        assert path.exists()
