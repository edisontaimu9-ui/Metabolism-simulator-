# Phase 16: Simulation Reports

**Status:** Complete (Markdown and HTML; PDF deliberately deferred)

## What was built

**`metabosim.reports`**, turning a completed run into a readable report:

- **`data.py`**: `ReportData` (frozen Pydantic model) and
  `build_report_data(simulator, states, title=None)`. Bundles the subject,
  config, per-day plans, state history, and headline summary. Plans,
  config, and initial glycogen are read from the `Simulator` itself, so a
  caller cannot pair a state history with the wrong inputs; the validator
  also rejects a state history whose length does not match `config.days`.
- **`document.py`**: a small format-neutral document model (`Section`,
  `Paragraph`, `BulletList`, `Table`, `FigureBlock`) and `build_document`.
  Sections: Subject, Models used, Diet and activity, Key results, Figures,
  Daily results, Interpretation and limitations, References.
- **`render.py`**: `render_markdown` and `render_html`, pure string
  functions. All text is escaped, so a subject name or activity label
  cannot inject Markdown or HTML.
- **`figures.py`**: `render_figures` draws the Phase 15 plots to PNG bytes
  on `matplotlib.figure.Figure` objects (no pyplot, no display, no leaked
  figures). Body composition and glycogen figures appear only when that
  tracking was active.
- **`references.py`**: per-model-ID citations, so a report cites exactly
  the models the run used.
- **`writers.py`**: `save_markdown_report` (report plus a sibling
  `<stem>_figures/` folder, linked by relative path) and `save_html_report`
  (one self-contained file, figures embedded as base64).

## Design decisions

1. **One document model, two renderers.** Markdown and HTML are rendered
   from the same `Document`, so they cannot disagree, and content logic is
   tested without parsing either format.
2. **References are per run, not the whole bibliography.** A run using
   Mifflin-St Jeor does not cite Harris-Benedict. The body composition
   citations appear only if body composition was tracked, glycogen only if
   glycogen was tracked.
3. **Citations live in the package, with a drift test.** `docs/` is not
   shipped in an installed wheel, so short-form citations are stored in
   `references.py`. A test checks that each one still appears in
   `docs/model_references.md`, and registry-completeness tests fail if a
   new built-in model is added without citations. (Those tests only count
   models defined inside the `metabosim` package, because other test
   modules register throwaway dummy models in the global registries.)
4. **Honest framing is part of the report.** Every report states that
   results are model-based estimates, not individual predictions or
   clinical advice. It notes when adaptive thermogenesis was not modeled,
   and when glycogen tracking means early weight changes may be water.
5. **Long runs are sampled in the daily table**, capped at 31 rows by
   default (`max_daily_rows`), always keeping the first and final state,
   with a visible note saying so.
6. **Table values are rounded for display only.** Underlying states are
   untouched.

## Not done in this phase

- **PDF output.** Deferred on purpose: it would add a heavy optional
  dependency (for example weasyprint) or a second layout path. The HTML
  report prints to PDF from any browser in the meantime. If added later it
  should be a third renderer over the same `Document`.
- **No CLI command yet.** `pyproject.toml` still points the `metabosim`
  script at `metabosim.cli.main:app`, which does not exist. That belongs
  with Phase 18.

## Fixes made alongside

- Removed `*/reports/*` from the coverage `omit` list in `pyproject.toml`
  (same stale-exclusion issue found with visualization in Phase 15).
- Updated the stale README status line, which still said Phase 2.

## No new scientific citations

Every number in a report was computed by an earlier phase. The citations in
`references.py` are short-form copies of entries already in
`docs/model_references.md`, which is unchanged.

## Testing

- 82 new unit tests in `tests/unit/reports/`, 100% coverage of
  `metabosim.reports`.
- 654 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and doctests clean.
- Sample Markdown and HTML reports were generated and inspected by eye
  (tables, escaping, figure links, embedded images), not only asserted.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/reports --cov=metabosim.reports --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Usage

```python
from metabosim.domain import MacronutrientGrams, Person, Sex
from metabosim.simulation import DailyPlan, SimulationConfig, Simulator
from metabosim.reports import (
    build_report_data, save_html_report, save_markdown_report,
)

person = Person(name="Demo", sex=Sex.FEMALE, age_years=40, height_cm=165,
                weight_kg=70, body_fat_percent=30)
plan = DailyPlan(macros=MacronutrientGrams(protein_g=120, carbohydrate_g=180, fat_g=50))
sim = Simulator(person, SimulationConfig(days=90), plan, initial_glycogen_g=400)
data = build_report_data(sim, sim.run())
save_markdown_report(data, "reports_out/demo.md")
save_html_report(data, "reports_out/demo.html")
```
