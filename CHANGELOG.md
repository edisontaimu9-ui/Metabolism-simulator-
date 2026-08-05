# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
