# Phase 7 — Physical Activity Models

**Status:** Complete

## What was built

`metabosim.models.activity`:

- **`base.py`** — `ActivityModel`, the abstract strategy interface.
  Every concrete subclass must declare `includes_average_tef: bool`
  explicitly (no default) — this is the load-bearing flag that lets
  calling code detect, at the type level, whether a given strategy's
  output is safe to add to a separately-computed TEF figure.
- **`met_based.py`** — `METBasedActivityModel` + `ActivityEntry`.
  Bottom-up: sums `(MET - 1) × weight_kg × duration_hours` across a
  logged activity diary (MET values sourced from the Ainsworth
  Compendium). `includes_average_tef = False`.
- **`iom_pal.py`** — `IOMPALActivityModel`. Top-down: `BMR × (PAL - 1)`
  using this project's own 5-tier interpolation of IOM (2005)'s
  4-tier PAL bands (documented explicitly as an interpolation, not an
  official IOM table). `includes_average_tef = True`.
- **`registry.py`** — runtime lookup by string ID. Differs from every
  other registry in this project: `get_model` forwards `**kwargs` to
  the model constructor, because `METBasedActivityModel` needs a
  logged activity list at construction time, breaking the
  zero-argument pattern used by `bmr`/`tdee`/`tef` models.

And, extending `metabosim.models.tdee.calculator`:

- **`calculate_tdee_from_components()`** + **`ComponentTDEEResult`** —
  the capstone of this phase: sums BMR + Activity Energy Expenditure +
  TEF as three *independently computed* figures, and actively checks
  `activity_model.includes_average_tef` before doing so, raising a
  clear `ValueError` if the chosen activity model would cause
  double-counting. This is the actual resolution of the caveat flagged
  in `docs/phase_notes/phase_05.md` and `phase_06.md`.

## The core scientific/architectural insight this phase turns on

Two different measurement paradigms both produce an "activity energy
expenditure" number, and they are not interchangeable:

1. **MET-based (bottom-up):** built from indirect-calorimetry
   measurements of specific movements, entirely independent of food
   intake. Safe to add to any independently-computed TEF.
2. **PAL-ratio-based (top-down):** `(measured total expenditure) /
   (measured or predicted BMR)` from doubly-labeled-water studies.
   Because the numerator is *total* expenditure, the ratio already
   contains an average TEF. NOT safe to add to a separate TEF figure
   — this is exactly the same caveat that applies to Phase 5's
   `PALMultiplierTDEE`.

This distinction is why `ActivityModel` forces every subclass to
declare `includes_average_tef` with no default, and why
`calculate_tdee_from_components` checks that flag before summing
rather than trusting the caller to pick correctly.

## Design decisions

1. **`includes_average_tef` has no default value.** A first draft
   considered defaulting it to `False` (the "safer-sounding" value),
   but that would let a future PAL-ratio-based model silently pass the
   double-counting safety check by omission. Forcing every subclass to
   set it explicitly turns "forgot to think about this" into a loud
   `AttributeError` (verified by
   `test_includes_average_tef_must_be_declared_by_subclass`) rather
   than a silently wrong simulation result.
2. **The IOM 5-tier interpolation is documented as this project's own
   choice, not attributed to IOM verbatim.** IOM (2005) defines four
   bands; this project's `ActivityLevel` enum has five tiers (a Phase
   3 decision, made before this mismatch's consequences were fully
   worked out). Rather than either forcing a fifth official IOM value
   that doesn't exist, or quietly picking values without saying so,
   the interpolation is explicit, cited, and flagged for anyone citing
   this model's output in a publication.
3. **The activity registry breaks the zero-arg convention, on
   purpose, with the deviation documented in its own module
   docstring.** `METBasedActivityModel` genuinely needs per-instance
   data (the activity log) that isn't a per-call argument like
   `Person` — forcing it into the same zero-arg registry pattern as
   `bmr`/`tdee`/`tef` would mean either a mutable `set_entries()`
   method (worse: stateful mutation after construction) or stuffing
   the log into `Person` (worse: pollutes the domain layer with a
   models-specific concept). Accepting `**kwargs` in `get_model` is
   the least-bad option and is called out explicitly as a deliberate
   deviation, not an oversight.
4. **`calculate_tdee_from_components` raises rather than warns.** A
   warning could be missed in batch/report contexts; a scientific
   simulation producing a silently double-counted TDEE is a
   correctness bug, not a style issue, so it's a hard `ValueError`.

## Testing

- 39 new unit tests for `models.activity`
  (`tests/unit/models/activity/{test_base,test_met_based,test_iom_pal,test_registry}.py`).
- 9 new unit tests for `calculate_tdee_from_components` appended to
  `tests/unit/models/tdee/test_calculator.py`, including a dedicated
  test that the IOM-PAL safety check actually fires with a message
  containing "double-count".
- 202 tests total across the whole project; 99% overall statement
  coverage; every miss is an abstract method's unreachable
  `raise NotImplementedError` body (consistent with `bmr`/`tdee`/`tef`).
- `mypy --strict`, `black`, `ruff`, and all doctests clean.
- The new `calculate_tdee_from_components` docstring example (BMR
  1780.0 + AEE 400.0 + TEF 258.9 = TDEE 2438.9) is itself an executed
  doctest, not just illustrative prose.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/activity tests/unit/models/tdee --cov=metabosim.models.activity --cov=metabosim.models.tdee --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No organ-level or MET-value lookup-by-activity-name database is
  bundled (the Compendium itself is an external, licensed/maintained
  dataset; callers supply MET values directly).
- `calculate_tdee_from_components` is not yet wired into
  `SimulationState` or any time-stepping logic — that's Phase 8/9
  territory (Energy Balance Engine, Body Weight Simulation).
- The IOM PAL interpolation's five values are a reasonable but
  unvalidated choice; Phase 17 (validation against published
  literature) is where this would be checked against real
  doubly-labeled-water cohort data if such comparison data becomes
  available.
