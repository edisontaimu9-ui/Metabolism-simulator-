# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added — Phase 14: Disease modules
- `metabosim.models.disease.base.DiseaseModifier` — adjustment-logic
  interface, and `DiseaseModifiedBMRModel` — the Decorator composing
  any `BMRModel` with one or more modifiers into a single, fully
  substitutable `BMRModel`. Realizes the extensibility point promised
  by `docs/architecture.md` since Phase 1.
- `metabosim.models.disease.thyroid.ThyroidModifier` + `ThyroidStatus`
  — 7-tier severity-graded BMR adjustment (−10% to −35% hypothyroid,
  +15% to +50% hyperthyroid), calibrated to McCullagh (1938)'s
  classical clinical BMR-percentage framework.
- `metabosim.models.disease.body_temperature.BodyTemperatureModifier`
  — ±13% BMR change per °C deviation from 37°C, applied
  bidirectionally (fever/hypothermia), cited to DuBois (1937).
- `metabosim.models.disease.registry` — kwargs-forwarding model
  lookup, mirroring `models.activity.registry`.
- `metabosim.models.tdee.calculator.calculate_tdee()` and
  `calculate_tdee_from_components()` now accept `bmr_model_id` as
  either a registry string (unchanged, fully backward compatible) or
  a pre-built `BMRModel` instance — making disease-modified models
  usable throughout the existing TDEE pipeline with zero changes
  needed anywhere else. New `CUSTOM_BMR_MODEL_ID = "custom"` sentinel
  reported when an instance is passed.
- 50 new unit tests (46 for `models.disease`, 4 for the calculator
  extension); 505 tests total project-wide, 99% overall coverage;
  `mypy --strict`, `black`, `ruff`, and all doctests clean.
- `docs/phase_notes/phase_14.md`; `docs/model_references.md` updated
  with full McCullagh / DuBois citations.

### Added — Phase 13: Organ metabolism
- `metabosim.models.organ.elia.calculate_organ_bmr_breakdown_kcal` —
  decomposes whole-body BMR into brain, liver, heart, kidneys,
  residual lean tissue, and adipose tissue contributions, using
  Elia's (1992) specific metabolic rates and peer-reviewed reference
  organ masses (Molina & DiMaio, 2012). Automatically uses
  age-adjusted rates (Wang et al., 2010) for subjects over 50.
  Deliberately built without a registry, following the Phase 12
  precedent — Elia's Ki table is a cited dataset, not a competing
  hypothesis.
- `metabosim.models.bmr.elia_organ_based.EliaOrganBasedBMR` — exposes
  the organ breakdown as a fifth selectable `BMRModel`, registered as
  `"elia_organ_based"` alongside Mifflin-St Jeor, Harris-Benedict,
  Katch-McArdle, and Cunningham — usable anywhere those are,
  including `SimulationConfig.bmr_model_id`, with zero changes to any
  existing simulation machinery.
- Cross-validated against Mifflin-St Jeor for the project's standard
  worked example: 1726.7 kcal (organ-based) vs. 1780.0 kcal
  (Mifflin-St Jeor), ~3% apart — two independently-derived methods
  agreeing to a sensible margin, verified by a dedicated test.
- 24 new unit tests (18 for `models.organ`, 6 for the new BMR model),
  plus updates to the existing BMR registry and cross-model
  plausibility test suites; 455 tests total project-wide, 99%
  overall coverage; `mypy --strict`, `black`, `ruff`, and all
  doctests clean.
- `docs/phase_notes/phase_13.md`; `docs/model_references.md` updated
  with full Elia / Wang et al. / Molina & DiMaio citations.

### Added — Phase 12: Macronutrient metabolism
- `metabosim.models.macronutrient.glycogen` — four pure functions
  modeling glycogen (and associated water) mass balance:
  `max_glycogen_g`, `glycogen_and_water_kg`, `step_glycogen_g`,
  `step_reference_carbohydrate_intake_g`. Cited constants: 2.7 g
  water per g glycogen and ~500 g storage capacity at 70 kg reference
  weight (Chow & Hall, 2008; Iyer et al., 2024). Deliberately built
  without a registry — documented explicitly as not a competing
  scientific hypothesis, unlike every other model family.
- `metabosim.simulation.stepper.step()` gained `current_glycogen_g` /
  `current_reference_carbohydrate_intake_g` parameters, activating
  glycogen tracking independently of body composition tracking;
  `StepResult` gained matching `next_*` fields.
- `metabosim.simulation.engine.Simulator` gained `initial_glycogen_g`
  / `initial_reference_carbohydrate_intake_g` constructor parameters.
- `SimulationState.glycogen_g` and `.total_body_water_kg` — present
  since Phase 3, always `None` until now — finally populated.
  Clarified (not changed) the `total_body_water_kg` docstring to
  state explicitly, per Chow & Hall's own convention, that glycogen
  and its water are informational breakdowns of what's already
  inside `lean_mass_kg`, not separate additive terms — resolving an
  ambiguity in the original Phase 3 wording without loosening the
  validated `fat_mass_kg + lean_mass_kg ≈ weight_kg` invariant.
- End-to-end validation that a sudden low-carbohydrate diet switch
  produces a sharp multi-day transient weight drop (~1.1 kg from
  glycogen+water depletion) that resolves within about a week and
  hands off cleanly to the existing smooth Forbes/energy-balance
  trend — the classic "water weight" phenomenon, reproduced without
  having been tuned to hit any particular number.
- 37 new unit/integration tests (24 for `models.macronutrient`, 7 new
  in `test_stepper.py`, 6 new in `test_engine.py`); 428 tests total
  project-wide, 99% overall coverage; `mypy --strict`, `black`,
  `ruff`, and all doctests clean.
- `docs/phase_notes/phase_12.md`; `docs/model_references.md` updated
  with full Chow & Hall / Iyer et al. citations.

### Added — Phase 11: Adaptive thermogenesis
- `metabosim.models.adaptive_thermogenesis.base.AdaptiveThermogenesisModel`
  — abstract strategy interface.
- `metabosim.models.adaptive_thermogenesis.none.NoAdaptiveThermogenesisModel`
  — always zero; the default used by `metabosim.simulation`, chosen
  because the magnitude/dynamics of real adaptation are genuinely
  less settled than every other modeled component.
- `metabosim.models.adaptive_thermogenesis.threshold.ThresholdAdaptiveThermogenesisModel`
  and `.proportional.ProportionalAdaptiveThermogenesisModel` — two
  competing models (Rosenbaum & Leibel, 2016's "Model 2"/"Model 3"
  framework), both calibrated to the same cited finding: a 10%
  weight change produces ~15% expenditure adjustment (Leibel et al.,
  1995; Goldsmith et al., 2010).
- `metabosim.models.adaptive_thermogenesis.registry` — runtime model
  lookup.
- `metabosim.simulation.config.SimulationConfig.adaptive_thermogenesis_model_id`
  — new field, validated eagerly at construction time.
- `metabosim.simulation.stepper.step()` now applies the configured
  adaptation adjustment on top of the naive predicted TDEE, finally
  populating `SimulationState.adaptive_thermogenesis_kcal` (a
  Phase 3 field that had always been zero until now) and making
  `energy_expenditure_kcal` diverge from `tdee_kcal` when adaptation
  is enabled.
- End-to-end validation that enabling proportional adaptation reduces
  total weight loss over a 100-day simulation relative to no
  adaptation, for the identical person/diet — the real, citable
  physiological consequence, verified through the whole stack.
- 43 new unit tests for `models.adaptive_thermogenesis`, plus new
  stepper- and engine-level integration tests; 391 tests total
  project-wide, 99% overall coverage; `mypy --strict`, `black`,
  `ruff`, and all doctests clean.
- All calibration figures (15%, 10%, slope 1.5, 20% clamp) verified
  against directly-quoted literature sources via web search before
  being encoded.
- `docs/phase_notes/phase_11.md`; `docs/model_references.md` updated
  with full Leibel/Goldsmith/Rosenbaum/Fothergill/Martins citations.

### Added — Phase 10: Body composition simulation
- `metabosim.models.body_composition.base.BodyCompositionModel` —
  abstract strategy interface using a template-method pattern:
  concrete subclasses implement only `ffm_fraction_of_change`; the
  base class implements `partition_mass_change_kg` once, guaranteeing
  consistency between the two.
- `metabosim.models.body_composition.forbes.ForbesPartitionModel` —
  `dFFM/dBW = C/(C+FM)` (Forbes, 1987/2000; Hall, 2007), with
  sex-specific constants (10.4 kg female, 13.8 kg male).
- `metabosim.models.body_composition.registry` — runtime model lookup.
- `metabosim.simulation.config.SimulationConfig.body_composition_model_id`
  — new field, validated eagerly at construction time.
- `metabosim.simulation.stepper.step()` now accepts optional
  `current_fat_mass_kg`, activating per-day fat/lean mass tracking:
  dynamically-computed `ffm_fraction` (replacing Phase 8's static 0.25
  default), updated `body_fat_percent` on each day's `Person` copy
  (so Katch-McArdle/Cunningham BMR reflect current, not stale,
  composition), and consistent fat/lean partitioning of each day's
  mass change. **Breaking internal change:** `step()` now returns a
  `StepResult` `NamedTuple` instead of a bare 2-tuple.
- `metabosim.simulation.engine.Simulator` seeds body composition
  tracking automatically from `person.fat_mass_kg` (a Phase 3 computed
  property) whenever `person.body_fat_percent` is set; falls back
  exactly to Phase 9 behavior otherwise.
- End-to-end validation that the simulation reproduces Forbes'
  qualitative theory: a leaner subject (8% body fat) gains
  proportionally more lean mass than a fatter subject (35% body fat)
  under an identical 30-day diet and activity plan.
- 44 new unit tests (31 for `models.body_composition`, 6 rewritten +
  new in `test_stepper.py`, 7 new in `test_engine.py`); 335 tests
  total project-wide, 99% overall coverage; `mypy --strict`, `black`,
  `ruff`, and all doctests clean.
- `docs/phase_notes/phase_10.md`; `docs/model_references.md` updated
  with full Forbes/Hall/Thomas citations.

### Added — Phase 9: Body weight simulation
- `metabosim.simulation.config.DailyPlan` — one day's diet + logged
  activity.
- `metabosim.simulation.config.SimulationConfig` — model-selection
  configuration, deferred since Phase 3 pending the model registries
  it references. Eagerly validates that `energy_balance_model_id`
  won't double-count weight-dependent expenditure feedback.
- `metabosim.simulation.stepper.step()` — pure single-day state
  transition function, independently unit-testable.
- `metabosim.simulation.engine.Simulator` — runs `step()` repeatedly
  to produce a full `list[SimulationState]` day-by-day history.
- Real BMR recompute at each day's updated weight now supplies
  weight-dependent expenditure feedback from actual physiology,
  verified to shrink a sustained surplus over a 30-day simulation
  (141.1 → 132.7 kcal/day) — replacing Phase 8's approximated `γ`
  constant with the real domain models wherever a full simulation is
  run.
- Enforces the `includes_weight_dependent_feedback` flag (declared but
  not yet enforced in Phase 8) at two independent layers: eagerly in
  `SimulationConfig`, and again in `stepper.step()` as defense-in-depth.
- 32 new unit tests, 100% coverage on `metabosim.simulation`.
- 291 tests total project-wide, 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.
- `docs/phase_notes/phase_09.md`. No new scientific citations required
  — this phase composes Phases 4-8's already-cited models.

### Added — Phase 8: Energy balance engine
- `metabosim.models.energy_balance.base.EnergyBalanceModel` — abstract
  strategy interface with both an instantaneous rate method
  (`mass_change_rate_kg_per_day`) and a closed-form projection method
  (`project_weight_change_kg`); forces every subclass to declare
  `includes_weight_dependent_feedback: bool` (no default).
- `metabosim.models.energy_balance.static_rule.StaticEnergyBalanceModel`
  — the 3500 kcal/lb rule (Wishnofsky, 1958), implemented and
  explicitly labeled not recommended, kept as a documented baseline
  demonstrating its unbounded-linear-projection flaw numerically.
- `metabosim.models.energy_balance.tissue_energy_density.TissueEnergyDensityModel`
  — blended fat/FFM energy density primitive (7380 kcal/kg default,
  Heymsfield et al. 2014), with no feedback of its own — intended for
  composition with a real per-day BMR recompute in Phase 9.
- `metabosim.models.energy_balance.dynamic_quasi_exponential.DynamicQuasiExponentialModel`
  — reduced single-compartment dynamic model (after Hall & Jordan,
  2008) with a bounded steady-state response; its default feedback
  slope was back-derived from a published illustrative example via
  `web_search`, with the calibration's limitations explicitly
  disclosed rather than presented as exact.
- `metabosim.models.energy_balance.registry` — runtime model lookup.
- 58 new unit tests, 98% coverage on `models.energy_balance`; every
  docstring numeric claim independently computed and cross-checked.
- 260 tests total project-wide, 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.
- `docs/phase_notes/phase_08.md`; `docs/model_references.md` updated
  with full Wishnofsky/Hall/Heymsfield/Yoo citations.

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
