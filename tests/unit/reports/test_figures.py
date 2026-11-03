"""Unit tests for metabosim.reports.figures."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from metabosim.reports.data import ReportData
from metabosim.reports.figures import render_figures

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.mark.unit
class TestRenderFigures:
    def test_basic_run_figure_keys(self, basic_data: ReportData) -> None:
        keys = [f.key for f in render_figures(basic_data)]
        assert keys == ["weight", "energy", "balance", "bmr-comparison"]

    def test_full_tracking_figure_keys(self, full_data: ReportData) -> None:
        keys = [f.key for f in render_figures(full_data)]
        assert keys == [
            "weight",
            "energy",
            "balance",
            "composition",
            "glycogen",
            "bmr-comparison",
        ]

    def test_outputs_are_valid_png(self, full_data: ReportData) -> None:
        for figure in render_figures(full_data):
            assert figure.png.startswith(_PNG_MAGIC)
            assert len(figure.png) > 1000
            assert figure.caption

    def test_does_not_leak_pyplot_figures(self, basic_data: ReportData) -> None:
        plt.close("all")
        render_figures(basic_data)
        assert plt.get_fignums() == []
