# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
