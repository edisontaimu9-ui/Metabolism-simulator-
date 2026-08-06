# Phase 5 — TDEE Engine

**Status:** Complete

## What was built

`metabosim.models.tdee`:

- **`base.py`** — `TDEEModel`, the abstract strategy interface.
  Deliberately takes a *pre-computed* `bmr_kcal` rather than a
  `BMRModel` instance, keeping BMR selection and TDEE composition
  independently swappable (mirrors the same separation already
  established between `models.bmr` subclasses and their registry).
- **`pal_multiplier.py`** — `PALMultiplierTDEE`, the first concrete
  strategy. TDEE = BMR × activity multiplier, using the traditional
  five-tier clinical table (1.2 / 1.375 / 1.55 / 1.725 / 1.9), chosen
  specifically because it maps 1:1 onto the five
  `ActivityLevel` tiers already defined in `metabosim.domain.enums`
  (Phase 3).
- **`registry.py`** — runtime lookup by string ID, mirroring
  `models.bmr.registry` exactly for consistency.
- **`calculator.py`** — `calculate_tdee()`, the actual "engine" this
  phase's title promises: given a `Person` plus optional BMR/TDEE
  model IDs, it wires both registries together and returns a
  `TDEEResult` carrying the BMR figure, the TDEE figure, and the names
  of both strategies used — so a report can show the full breakdown,
  not just an opaque final number.

## Design decisions

1. **Sequencing gap acknowledged head-on.** The original roadmap
   orders Phase 5 (TDEE) before Phase 6 (TEF) and Phase 7 (Activity),
   even though architecturally TDEE composes BMR + Activity + TEF.
   Rather than block on that ordering, Phase 5 ships a *complete,
   usable* TDEE engine now using a self-contained multiplier table
   (documented as provisional), and defers the finer-grained
   MET-based activity modeling and explicit TEF addition to their
   dedicated phases. This is the same "ship something correct and
   complete now, refine later" principle used throughout the project.
2. **Multiplier table lives in `tdee/pal_multiplier.py`, not
   `domain`.** Per the Phase 3 note that PAL-to-numeric mapping is a
   modeling choice (multiple competing tables exist) and therefore
   belongs in `models.*`, not the dependency-free domain layer.
3. **Explicit double-counting warning documented.** The traditional
   multiplier table's published values were derived against *total*
   measured energy expenditure, meaning they implicitly bundle an
   average thermic effect of food. The module docstring flags that
   naively adding a separate Phase 6 TEF figure on top of this
   model's TDEE would double-count food-processing energy cost --
   this will be resolved explicitly when Phase 6 is built, either by
   re-deriving compatible multipliers or by offering TEF-exclusive and
   TEF-inclusive TDEE variants.
4. **`TDEEResult` as a small, frozen Pydantic model.** Chosen over a
   bare float return so every call site gets the full breakdown
   (which BMR equation, which TDEE strategy, both intermediate and
   final figures) for free, supporting the project's goal of being a
   transparent scientific instrument. `frozen=True` prevents a caller
   from mutating a result and mistaking the mutated value for a fresh
   calculation.
5. **`calculate_tdee()` defaults to `mifflin_st_jeor` + `pal_multiplier`.**
   Mifflin-St Jeor is the most consistently well-validated equation
   against measured RMR in healthy non-obese adults across the
   comparative literature, making it the most defensible default when
   the caller hasn't specified a preference.

## A real bug caught by writing the calculator before the tests

The first draft of `calculator.py` called `bmr_model.calculate_bmr_kcal(person)`,
but the actual `BMRModel` interface (Phase 4) method is named
`calculate()`. This was caught immediately by running the module's own
doctest example (`pytest --doctest-modules`) before writing the full
test suite, and is a good demonstration of why doctested usage
examples are worth keeping executable rather than as inert prose.

## A second bug caught by the full-suite run

Running the complete project test suite (not just `tests/unit/models/tdee`)
surfaced a pytest import collision: `tests/unit/models/bmr/test_base.py`
and `tests/unit/models/tdee/test_base.py` (same basename, sibling
directories, no `__init__.py` packages) were assigned the same
top-level module name under pytest's default import mode, so the
second one failed to collect. Fixed by adding
`--import-mode=importlib` to `pytest`'s `addopts` in `pyproject.toml`
-- the modern (pytest 6+) recommended fix, which uses `importlib` to
give every test file a distinct module identity regardless of
basename collisions, without requiring `__init__.py` files throughout
`tests/`. This will keep working automatically as more phases add
their own same-named test files (`test_base.py`, `test_registry.py`,
etc.) in sibling `tests/unit/models/*` directories.

## Testing

- 33 unit tests across 5 test files
  (`tests/unit/models/tdee/{test_base,test_pal_multiplier,test_registry,test_calculator}.py`
  plus `conftest.py` fixtures).
- 98% statement coverage on `metabosim.models.tdee` (the sole miss is
  the abstract method's `raise NotImplementedError` body, unreachable
  by construction).
- `mypy --strict`, `black`, `ruff` all clean.
- Full project suite (`domain` + `models.bmr` + `models.tdee`): 99%
  overall coverage, all green.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/tdee --cov=metabosim.models.tdee --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim/models/tdee
black --check src/metabosim/models/tdee tests/unit/models/tdee
ruff check src/metabosim/models/tdee tests/unit/models/tdee
```

## Not yet done (future phases)

- No explicit TEF model yet (Phase 6) -- see the double-counting
  caveat above, to be resolved then.
- No MET-based / IOM-consistent activity model yet (Phase 7) -- the
  PAL multiplier table is provisional and documented as such.
- `TDEEResult` does not yet feed into `SimulationState` (that wiring
  belongs to the simulation engine, Phase 8-9).
