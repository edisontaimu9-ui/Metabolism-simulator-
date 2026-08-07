# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added — Phase 7: Physical activity models
- `metabosim.models.activity.base.ActivityModel` — abstract strategy
  interface. Forces every subclass to explicitly declare
  `includes_average_tef: bool` (no default), the flag that determines
  whether a strategy's output can be safely summed with a separately
  computed TEF figure.
- `metabosim.models.activity.met_based.METBasedActivityModel` +
  `ActivityEntry` — bottom-up MET-based AEE model (Ainsworth
  Compendium, 2011); safe to combine with TEF
  (`includes_average_tef = False`).
- `metabosim.models.activity.iom_pal.IOMPALActivityModel` — top-down
  PAL-ratio AEE model using this project's documented 5-tier
  interpolation of IOM (2005) PAL bands; NOT safe to combine with a
  separate TEF (`includes_average_tef = True`).
- `metabosim.models.activity.registry` — runtime model lookup,
  supporting constructor kwargs (a deliberate deviation from the
  zero-arg pattern used elsewhere, documented in-module).
- `metabosim.models.tdee.calculator.calculate_tdee_from_components()` +
  `ComponentTDEEResult` — sums independently-computed BMR + Activity +
  TEF, with an enforced safety check that raises `ValueError` if the
  chosen activity model would double-count TEF. This resolves the
  caveat flagged in Phases 5 and 6.
- 48 new unit tests (39 for `models.activity`, 9 for the new
  calculator function); 202 tests total project-wide, 99% overall
  coverage; `mypy --strict`, `black`, `ruff`, and all doctests clean.
- `docs/phase_notes/phase_07.md`; `docs/model_references.md` updated
  with full Ainsworth/Jette/IOM citations.

### Added — Phase 6: Thermic Effect of Food
- `metabosim.models.tef.base.TEFModel` — abstract strategy interface.
- `metabosim.models.tef.macronutrient_specific.MacronutrientSpecificTEF`
  — weighted, per-macronutrient thermic cost model (protein 25% /
  carbohydrate 7.5% / fat 2% / alcohol 20%, midpoints from Jequier &
  Tappy 1999), with a documented fiber-approximation caveat.
- `metabosim.models.tef.fixed_percentage.FixedPercentageTEF` — flat
  ~10%-of-intake approximation (IOM, 2005), for when macronutrient
  breakdown is unavailable.
- `metabosim.models.tef.registry` — runtime model lookup by string ID.
- 23 unit tests, 98% coverage on `models.tef`; `mypy --strict`,
  `black`, `ruff` all clean.
- Documented (not yet implemented) integration plan for combining TEF
  with `calculate_tdee()` without double-counting food-processing
  energy cost — deferred pending Phase 7's activity model.
- `docs/phase_notes/phase_06.md`; `docs/model_references.md` updated
  with full TEF citations.

### Added — Phase 5: TDEE engine
- `metabosim.models.tdee.base.TDEEModel` — abstract strategy interface
  for BMR-to-TDEE scaling.
- `metabosim.models.tdee.pal_multiplier.PALMultiplierTDEE` — traditional
  five-tier clinical activity multiplier (1.2-1.9), cited, with an
  explicit documented caveat about TEF double-counting once Phase 6
  lands.
- `metabosim.models.tdee.registry` — runtime model lookup by string ID.
- `metabosim.models.tdee.calculator.calculate_tdee()` — the TDEE
  engine entry point composing BMR selection + TDEE scaling into a
  single `TDEEResult` (BMR figure, TDEE figure, both strategy names).
- 33 unit tests, 98% coverage on `models.tdee`; `mypy --strict`,
  `black`, `ruff` all clean.
- Fixed a pytest import-collision bug (duplicate `test_base.py` /
  `test_registry.py` basenames across `models/bmr` and `models/tdee`
  test directories) by switching to `--import-mode=importlib`.
- `docs/phase_notes/phase_05.md`; `docs/model_references.md` updated
  with the activity-multiplier citation.

### Added — Phase 4: BMR equations
- `metabosim.models.bmr.base.BMRModel` — abstract interface for all
  BMR/RMR strategies (`calculate()`, `name`, `requires_body_fat`,
  `__call__` alias).
- Four equations, each in its own module with full citation and
  documented limitations: `MifflinStJeorBMR`, `HarrisBenedictBMR`,
  `KatchMcArdleBMR`, `CunninghamBMR`.
- `metabosim.models.bmr.registry` — `get_model()`, `list_models()`,
  `register_model()` for runtime model selection by string ID.
- 45 new unit tests (99 total project-wide): per-equation reference
  values, base-contract tests, registry tests, and a cross-model
  plausibility suite. 99% statement coverage on `models.bmr`.
- `docs/phase_notes/phase_04.md`.

### Added — Phase 3: Data models
- `metabosim.domain.constants` — physiological validation bounds and
  Atwater general energy factors, each cited (FAO 2003, IOM 2005,
  Gallagher et al. 2000).
- `metabosim.domain.enums` — `Sex`, `ActivityLevel`, `UnitSystem` as
  `enum.StrEnum`.
- `metabosim.domain.units` — pure conversion helpers (kg↔lb, cm↔in,
  cm↔ft/in, kcal↔kJ) for presentation-layer use.
- `metabosim.domain.person.Person` — validated subject profile with
  computed `bmi`, `fat_mass_kg`, `lean_mass_kg`.
- `metabosim.domain.diet.MacronutrientGrams` and `DietPlan` — dietary
  intake data structures with Atwater-factor energy calculation.
- `metabosim.domain.simulation_state.SimulationState` — single-timestep
  simulation snapshot with a fat/lean-mass-vs-weight consistency
  validator.
- 54 unit tests (`tests/unit/domain/`), 100% statement coverage,
  `mypy --strict` clean, `black`/`ruff` clean.
- `docs/phase_notes/phase_03.md`; `docs/model_references.md` updated
  with domain-layer citations.

### Added — Phase 2: Project setup and folder structure
- Established `src/` layout package skeleton: `metabosim` with subpackages
  `domain`, `models` (bmr, tef, activity, tdee, energy_balance,
  body_composition, adaptive_thermogenesis, macronutrient, organ, disease),
  `simulation`, `analysis`, `visualization`, `reports`, `validation`, `cli`.
- Added `pyproject.toml` with dependencies (NumPy, SciPy, Pandas,
  Matplotlib, Pydantic) and dev tooling (pytest, mypy, ruff, black,
  pre-commit) configuration.
- Added `.gitignore`, `.pre-commit-config.yaml`.
- Added `tests/` tree mirroring `src/metabosim/` structure
  (`tests/unit`, `tests/integration`, `tests/validation`).
- Added `docs/architecture.md`, `docs/model_references.md`,
  `docs/phase_notes/phase_01.md`, `docs/phase_notes/phase_02.md`.
- Added `examples/notebooks/` and `scripts/` placeholders.

### Added — Phase 1: Project planning and architecture
- Defined scientific objectives, layered/strategy-based architecture,
  module responsibilities, coding standards, testing strategy,
  documentation strategy, Git workflow, and scientific reference list.
