# Phase 2 — Project Setup & Folder Structure

**Status:** Complete

## What was done

- Created the full `src/metabosim/` package skeleton exactly matching
  the Phase 1 architecture diagram: `domain`, `models/{bmr, tef,
  activity, tdee, energy_balance, body_composition,
  adaptive_thermogenesis, macronutrient, organ, disease}`,
  `simulation`, `analysis`, `visualization`, `reports`, `validation`
  (with `validation/datasets/`), `cli`.
- Every package received a documented `__init__.py` stating its
  responsibility, its dependencies (or explicit lack thereof), and
  which development phase will populate it — no business logic yet,
  per instructions.
- Created `tests/` mirroring `src/metabosim/` 1:1 under `tests/unit/`,
  plus `tests/integration/` and `tests/validation/`.
- Configured `pyproject.toml`:
  - Runtime deps: numpy, scipy, pandas, matplotlib, pydantic.
  - Dev deps: pytest, pytest-cov, hypothesis, black, mypy, ruff,
    pre-commit.
  - Optional `gui` extra for PyQt6 (deferred, not installed by default).
  - Tool configs for black (line-length 88), ruff, mypy (`--strict`),
    pytest (with `unit`/`integration`/`validation` markers), and
    coverage (excluding visualization/reports/cli from strict coverage
    targets, per Phase 1 testing strategy).
- Added `.pre-commit-config.yaml` wiring black, ruff, mypy, and basic
  hygiene hooks.
- Added `.gitignore` tuned for a scientific Python project (caches,
  venvs, coverage artifacts, generated report/figure output
  directories treated as build artifacts, not source).
- Added `README.md` (project overview, architecture summary, roadmap
  table, setup/test instructions), `CHANGELOG.md` (Keep a Changelog
  format), `LICENSE` (MIT placeholder — **update the copyright name**),
  `docs/architecture.md` (living document), `docs/model_references.md`
  (bibliography skeleton to be filled in per phase), and this file.
- Added empty `examples/notebooks/` and `scripts/` directories for
  future example notebooks and one-off utility scripts.

## Rationale for doing this before any logic

Scaffolding the entire structure up front — even for phases 13/14 that
are far away — means every future phase is additive: we `cd` into an
existing folder and add a file, we never restructure. This keeps Git
history clean (no large structural-move commits later) and makes the
dependency graph in `docs/architecture.md` verifiable against the
actual folder tree from day one.

## Verification performed

- `pip install -e .` dry-run structure check (package discovery via
  `tool.setuptools.packages.find` against `src/`).
- Confirmed no `__init__.py` was placed under `tests/` — pytest's
  rootdir-based discovery is used instead, avoiding potential test
  module name collisions without needing package markers there.

## Not yet done (future phases)

- No `Person`, `SimulationState`, or any Pydantic model yet (Phase 3).
- No equations implemented (Phase 4+).
- `metabosim.cli.main:app` entry point referenced in `pyproject.toml`
  does not exist yet — this is intentional; it will be created when
  Phase 8+ produces something worth exposing via CLI. Running
  `pip install -e .` now installs cleanly; only invoking the `metabosim`
  console script before then would fail, which is expected and fine
  during development.
