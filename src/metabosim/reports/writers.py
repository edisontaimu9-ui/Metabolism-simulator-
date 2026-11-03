"""
metabosim.reports.writers
============================

The public, file-writing entry points for report generation.

  - ``save_markdown_report`` writes ``<path>`` plus its figures as PNG
    files in a sibling ``<stem>_figures/`` directory.
  - ``save_html_report`` writes one self-contained ``<path>``.

Both take a ``ReportData`` (see ``metabosim.reports.data``) and return
the path written.
"""

from __future__ import annotations

from pathlib import Path

from metabosim.reports.data import ReportData
from metabosim.reports.document import (
    DEFAULT_MAX_DAILY_ROWS,
    build_document,
)
from metabosim.reports.figures import render_figures
from metabosim.reports.render import render_html, render_markdown


def save_markdown_report(
    data: ReportData,
    path: str | Path,
    include_figures: bool = True,
    max_daily_rows: int = DEFAULT_MAX_DAILY_ROWS,
) -> Path:
    """Write a Markdown report (and its figure files) and return ``path``.

    Figures go in ``<path stem>_figures/`` next to the report and are
    linked by relative path, so the folder can be moved as a unit.
    Parent directories are created if missing.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figures = render_figures(data) if include_figures else []
    figure_dir_name = f"{target.stem}_figures"
    document = build_document(data, figures, max_daily_rows)
    if figures:
        figure_dir = target.parent / figure_dir_name
        figure_dir.mkdir(parents=True, exist_ok=True)
        for figure in figures:
            (figure_dir / f"{figure.key}.png").write_bytes(figure.png)
    target.write_text(render_markdown(document, figure_dir_name), encoding="utf-8")
    return target


def save_html_report(
    data: ReportData,
    path: str | Path,
    include_figures: bool = True,
    max_daily_rows: int = DEFAULT_MAX_DAILY_ROWS,
) -> Path:
    """Write a self-contained HTML report and return ``path``.

    Parent directories are created if missing.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figures = render_figures(data) if include_figures else []
    document = build_document(data, figures, max_daily_rows)
    target.write_text(render_html(document), encoding="utf-8")
    return target
