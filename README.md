# metabosim

**Human Metabolism & Energy Expenditure Simulation Engine**

A scientific software package for simulating human metabolism *dynamically
over time* — not a simple calorie calculator. Built for research,
education, and clinical nutrition applications.

> Status: **Phase 2 of 18 — Project setup & folder structure.**
> See `docs/phase_notes/` for the design log of every completed phase.

## Why this exists

Most "calorie calculators" apply a single static equation once. Real
human metabolism is dynamic: energy expenditure adapts to weight change,
body composition shifts non-linearly with energy balance, and metabolic
adaptation (adaptive thermogenesis) alters the picture over weeks and
months. `metabosim` treats metabolism as a simulated dynamic system,
using published, citable physiological models at every step.

## Architecture at a glance

```
domain/        -> pure data models (Pydantic)
models/        -> interchangeable scientific model strategies
                   (bmr, tef, activity, tdee, energy_balance,
                    body_composition, adaptive_thermogenesis,
                    macronutrient, organ, disease)
simulation/    -> time-stepping orchestration engine
analysis/      -> read-only post-hoc statistics on simulation output
visualization/ -> matplotlib figures
reports/       -> generated Markdown/HTML/PDF simulation reports
validation/    -> comparison against published literature datasets
cli/           -> command-line entry points
```

Full architectural rationale: [`docs/architecture.md`](docs/architecture.md).

## Development roadmap

| Phase | Scope |
|---|---|
| 1 | Project planning and architecture |
| 2 | Project setup and folder structure |
| 3 | Data models |
| 4 | BMR equations |
| 5 | TDEE engine |
| 6 | Thermic Effect of Food |
| 7 | Physical activity models |
| 8 | Energy balance engine |
| 9 | Body weight simulation |
| 10 | Body composition simulation |
| 11 | Adaptive thermogenesis |
| 12 | Macronutrient metabolism |
| 13 | Organ metabolism |
| 14 | Disease modules |
| 15 | Visualization engine |
| 16 | Simulation reports |
| 17 | Validation against published literature |
| 18 | Optimization and packaging |

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running tests

```bash
pytest                     # all tests
pytest tests/unit          # unit tests only
pytest -m validation        # literature-validation tests only
pytest --cov=metabosim     # with coverage report
```

## Scientific references

See [`docs/model_references.md`](docs/model_references.md) for the full,
per-model bibliography that grounds every equation implemented in this
package.

## License

MIT (see `LICENSE`).
