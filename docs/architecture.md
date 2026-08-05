# Architecture

> This is a **living document**, updated as the architecture evolves across
> development phases. Last updated: Phase 2.

## 1. Architectural style

Layered, plugin-based, model-driven architecture. Strict separation between:

1. **Domain models** (`metabosim.domain`) — pure Pydantic data structures.
2. **Scientific model strategies** (`metabosim.models.*`) — interchangeable
   implementations of a common interface per model family (BMR, TDEE, TEF,
   activity, energy balance, body composition, adaptive thermogenesis,
   macronutrient, organ, disease).
3. **Simulation orchestration** (`metabosim.simulation`) — a stateful,
   time-stepping engine composing model strategies.
4. **Analysis / Visualization / Reports** (`metabosim.analysis`,
   `metabosim.visualization`, `metabosim.reports`) — read-only consumers of
   simulation output.

## 2. Data flow

```
domain models  --->  model strategies  --->  simulation engine  --->  history (time series)
                                                                          |
                                                                          v
                                                   analysis  --->  visualization  --->  reports
```

Data flows strictly forward: nothing downstream mutates anything upstream.
The simulation engine's output (`SimulationState` history) is the single
source of truth consumed by everything after it.

## 3. Design patterns in use

| Pattern | Where | Purpose |
|---|---|---|
| Strategy | `models/*` | Swap equations at runtime (e.g. Mifflin-St Jeor vs Harris-Benedict) |
| Registry / Factory | `models/*/registry.py` | Look up model classes by string ID |
| Pipeline | `models/tdee` composing `bmr` + `activity` + `tef` | Composable, independently testable stages |
| State object + stepper | `simulation/engine.py`, `simulation/stepper.py` | Separate "current truth" from "how time advances" |
| Decorator / Modifier | `models/disease`, `models/adaptive_thermogenesis` | Adjust a base rate without the base model knowing about the adjustment |
| Immutable value objects | `domain/*` (Pydantic, validated, frozen where appropriate) | Prevent silent unit/range errors |

## 4. Module dependency graph

```
domain
  ^
  |
models/bmr  models/activity  models/tef  models/organ
  ^               ^              ^
  |_______________|______________|
              |
        models/tdee
              |
    models/energy_balance
              |
    models/body_composition ---- models/adaptive_thermogenesis
              |
      models/macronutrient
              |
        models/disease  (decorates any of the above)
              |
          simulation
              |
      analysis ---- visualization ---- reports
              |
             cli
```

No arrows point backward. This is enforced by convention (and eventually
by import-linting in CI) rather than by the language itself.

## 5. Why `src/` layout

Prevents accidental imports of an uninstalled package during development
and testing; matches modern Python packaging conventions (PEP 517/518 via
`pyproject.toml`).

## 6. Extensibility points

- New BMR/TDEE/TEF/activity equations: add a module + register it, no
  changes to `simulation/`.
- New diseases: add a decorator in `models/disease/`, compose over any
  base model without modifying that base model.
- New report formats: add a renderer in `reports/`, consuming the same
  `SimulationState` history and `analysis` outputs.

## Phase log

- **Phase 1** — Architecture defined (this document's first draft).
- **Phase 2** — Folder structure and tooling scaffolded to match this
  architecture; no business logic yet.
