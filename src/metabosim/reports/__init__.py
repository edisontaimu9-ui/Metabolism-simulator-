"""
metabosim.reports
===================

Structured report generation (Markdown and self-contained HTML)
summarizing a completed simulation run: subject, models used, diet and
activity, key results, figures from ``metabosim.visualization``, a
daily results table, limitations, and the citations for exactly the
models the run used.

  - ``data``       -- ``ReportData`` / ``build_report_data``: bundles a
    ``Simulator`` and its output with a headline summary.
  - ``document``   -- ``build_document``: a format-neutral document
    model, so Markdown and HTML always say the same thing.
  - ``render``     -- ``render_markdown`` / ``render_html``: pure
    string renderers (all text escaped).
  - ``figures``    -- ``render_figures``: PNG bytes from the Phase 15
    plots, drawn without pyplot or a display.
  - ``references`` -- per-model citations for each run.
  - ``writers``    -- ``save_markdown_report`` / ``save_html_report``.

PDF output is not implemented in this phase; see
``docs/phase_notes/phase_16.md``.

Example
-------
>>> from metabosim.domain import MacronutrientGrams, Person, Sex
>>> from metabosim.simulation import DailyPlan, SimulationConfig, Simulator
>>> from metabosim.reports import build_report_data, save_html_report
>>> person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
>>> plan = DailyPlan(
...     macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
... )
>>> sim = Simulator(person, SimulationConfig(days=14), plan)
>>> data = build_report_data(sim, sim.run())
>>> data.summary.days_simulated
14
"""

from metabosim.reports.data import ReportData, build_report_data
from metabosim.reports.document import Document, build_document
from metabosim.reports.figures import render_figures
from metabosim.reports.render import render_html, render_markdown
from metabosim.reports.writers import save_html_report, save_markdown_report

__all__ = [
    "Document",
    "ReportData",
    "build_document",
    "build_report_data",
    "render_figures",
    "render_html",
    "render_markdown",
    "save_html_report",
    "save_markdown_report",
]
