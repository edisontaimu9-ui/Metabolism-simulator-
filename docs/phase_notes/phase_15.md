# Phase 15 — Visualization Engine

**Status:** Complete

## What was built

**`metabosim.analysis`** (minimal support infrastructure, see scope
note below):

- **`series.py`** — pure extraction functions turning a
  `list[SimulationState]` into plain numeric lists (weight, fat/lean
  mass, glycogen, energy intake/expenditure/balance), plus
  `moving_average()` for smoothing short-term noise.
- **`summary.py`** — `summarize()` / `SimulationSummary`: headline
  statistics (total change, average daily rate, average daily energy
  balance, which tracking features were active) for a completed run.

**`metabosim.visualization`** — Matplotlib plotting, consuming
`metabosim.analysis` and `metabosim.models.*` outputs directly:

- **`trajectory.py`** — `plot_weight_trajectory`,
  `plot_body_composition_trajectory`, `plot_glycogen_trajectory`.
- **`energy.py`** — `plot_energy_intake_vs_expenditure`,
  `plot_energy_balance` (bar chart with zero-reference line and
  optional moving-average overlay).
- **`comparison.py`** — `plot_organ_bmr_breakdown` (Phase 13),
  `plot_bmr_model_comparison` (every registered BMR equation for one
  subject, side by side — silently skipping equations that need
  `body_fat_percent` when it isn't set, since this is a showcase view
  where partial results beat an outright failure).

Every function follows one signature convention:
`(..., ax: Axes | None = None) -> Axes`. Pass an existing `Axes` to
compose multiple plots into one figure; omit it for a fresh one. No
function calls `plt.show()` — this is a library, not a script.

## Why `metabosim.analysis` exists without its own numbered phase

The original 18-phase roadmap has no dedicated "Analysis" phase, but
`docs/architecture.md`'s Phase 1 folder plan described one, and Phase
15's own architecture description says visualization "consumes
`metabosim.simulation` output *and* `metabosim.analysis` results."
Rather than either skip building it (leaving visualization to
re-derive the same extraction logic in every plotting function) or
invent an unplanned "Phase 15b," a minimal, honestly-scoped analysis
layer was built as direct supporting infrastructure for this phase —
documented explicitly as such in `metabosim.analysis.series`'s module
docstring, rather than silently expanding this phase's stated scope
without saying so.

## No new scientific citations this phase

Every number `metabosim.analysis` and `metabosim.visualization`
touch was already computed and validated by an earlier phase; this
phase only extracts, summarizes, and draws that data. A moving
average and a bar chart aren't competing scientific hypotheses the
way a BMR equation is — there's nothing to cite here, and
`docs/model_references.md` is correspondingly unchanged. This is the
same reasoning already applied to Phase 9 (pure composition, no new
model), stated explicitly here rather than left implicit.

## A real coverage-configuration bug, found and fixed

Phase 1's original `pyproject.toml` coverage configuration excluded
`*/visualization/*` from coverage measurement — a reasonable-looking
default at the time, written before any visualization code existed,
anticipating only "smoke tests" for chart code. Running this phase's
actual 37-test suite against that stale exclusion silently reported
"no data collected" rather than the real coverage figure. Fixed by
removing the exclusion once real, rigorous tests existed to measure —
the two remaining gaps this surfaced (an inconsistent-data guard in
`trajectory.py`, an empty-registry guard in `comparison.py`) were
then deliberately covered with dedicated tests (one hand-constructing
inconsistent `SimulationState` data, one using `monkeypatch` to
simulate an empty registry) rather than left as unreachable-in-
practice code, bringing the package to 100% coverage.

## Design decisions

1. **The `ax=None` composability convention, applied uniformly.**
   Every one of the seven plotting functions accepts an optional
   pre-existing `Axes` and returns whatever it drew on — verified
   directly with a two-panel composed figure (weight trajectory +
   energy balance on one `Figure` via `plt.subplots(1, 2)`) during
   manual testing before any test was written, to confirm the
   convention actually works end-to-end, not just in isolation.
2. **`plot_bmr_model_comparison` skips incompatible models rather
   than raising.** A strict version would fail entirely for any
   `Person` without `body_fat_percent` set, even though 2 of the 5
   registered BMR equations don't need it. Partial results (the
   equations that *can* run) are more useful for a comparison/
   showcase chart than an all-or-nothing failure — verified by a
   dedicated test confirming exactly 2 bars appear without body fat
   data, and all 5 with it.
3. **Headless testing via the `Agg` backend, configured once in
   `conftest.py`**, not scattered across individual test files or
   left to chance based on the environment's display availability.
   An `autouse` fixture also closes all figures after every test, to
   avoid unbounded memory growth across the hundreds of figures a
   full test run creates.
4. **`plot_organ_bmr_breakdown` and `plot_bmr_model_comparison` sort
   their bars largest-to-smallest** rather than plotting in
   whatever order the source data happens to provide — a genuinely
   better default for a horizontal bar chart, not merely cosmetic:
   an unsorted organ breakdown, for instance, would be noticeably
   harder to scan.

## Testing

- 30 new unit tests for `metabosim.analysis`
  (`tests/unit/analysis/{test_series,test_summary}.py`), 100%
  coverage.
- 37 new unit tests for `metabosim.visualization`
  (`tests/unit/visualization/{test_trajectory,test_energy,test_comparison}.py`),
  100% coverage, including two deliberately-added tests for defensive
  branches that the built-in registries/models can't normally reach.
- 572 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.
- Every generated chart was visually inspected (not just asserted
  programmatically) during manual verification before the test suite
  was written, confirming labels, titles, legends, and data actually
  render sensibly, not merely that the code path executes without
  raising.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/analysis --cov=metabosim.analysis --cov-report=term-missing
pytest tests/unit/visualization --cov=metabosim.visualization --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No structured report generation (PDF/HTML/Markdown combining
  multiple charts with narrative text) — Phase 16.
- No plateau-detection or other more sophisticated post-hoc
  statistics beyond the headline summary in `SimulationSummary` —
  could be added to `metabosim.analysis` later if a specific report
  or chart needs them, following the same "build infrastructure when
  a consuming phase needs it" principle applied here.
- No interactive/web-based visualization (e.g. Plotly) — matplotlib
  only, per the originally specified technology stack.
