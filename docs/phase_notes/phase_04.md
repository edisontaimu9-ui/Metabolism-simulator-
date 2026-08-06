# Phase 4 — BMR Equations

**Status:** Complete

## What was built

`metabosim.models.bmr` — four BMR/RMR equations behind a common
`BMRModel` interface, selectable at runtime via a string-ID registry.

- **`base.py`** — `BMRModel` (ABC). Defines `calculate(person) -> float`,
  a `name` class attribute, a `requires_body_fat` flag, and a `__call__`
  convenience alias so instances are directly callable.
- **`mifflin_st_jeor.py`** — Mifflin-St Jeor (1990). Weight-based,
  sex-specific, no body composition required.
- **`harris_benedict.py`** — Harris-Benedict (1919, rev. Roza & Shizgal
  1984). Weight-based, sex-specific.
- **`katch_mcardle.py`** — Katch-McArdle. Lean-mass-based,
  sex-independent, **requires** `Person.body_fat_percent`.
- **`cunningham.py`** — Cunningham (1980). Lean-mass-based,
  sex-independent, **requires** `Person.body_fat_percent`.
- **`registry.py`** — `get_model(id)`, `list_models()`,
  `register_model(id, cls)` for runtime model selection without
  importing concrete classes.

## Design decisions

1. **Lean-mass models raise `ValueError`, not a silent fallback**, if
   `Person.body_fat_percent` is `None`. An earlier design considered
   silently falling back to a population-average body fat % — rejected
   for the same reason `Person.fat_mass_kg` returns `None` rather than
   guessing (Phase 3): a silent default would look identical to real
   measured data to every downstream caller. The error message names
   the missing field and suggests a weight-based alternative.
2. **Registry returns a fresh instance per call.** All four `BMRModel`
   subclasses are stateless — every value they need comes from the
   `Person` argument to `calculate()`, never from instance state — so
   there's no correctness reason to cache/reuse instances, and a fresh
   instance per `get_model()` call removes any possibility of shared
   mutable state between callers using the registry concurrently.
3. **`register_model()` included from the start**, even though nothing
   in this codebase calls it yet. This is the extensibility point the
   Phase 1 architecture promised — a third-party or experimental
   equation should be addable from a notebook without editing
   `registry.py`. Tests exercise it directly (`test_registry.py`).
4. **Cross-model plausibility tests, not just per-equation reference
   values.** In addition to hand-computed reference values for every
   equation, `test_cross_model_plausibility.py` checks properties that
   should hold for *any* correct implementation (BMR rises with
   weight/lean mass, falls with age, lean-mass models are sex-blind,
   and all four equations stay within a plausible band of each other
   for a typical adult). This is deliberately distinct from Phase 17's
   literature-validation tests — these are internal consistency checks,
   not claims that the equations match published data (they already
   are the published equations).

## Reference values used in tests

All hand-computed from each equation as published (see module
docstrings for the citations):

| Case | Model | Result (kcal/day) |
|---|---|---|
| M, 30y, 180cm, 80kg | Mifflin-St Jeor | 1780.0 |
| F, 25y, 165cm, 60kg | Mifflin-St Jeor | 1345.25 |
| M, 30y, 180cm, 80kg | Harris-Benedict | 1853.632 |
| F, 25y, 165cm, 60kg | Harris-Benedict | 1405.333 |
| M, 80kg, 20% BF (64kg lean) | Katch-McArdle | 1752.4 |
| F, 60kg, 30% BF (42kg lean) | Katch-McArdle | 1277.2 |
| M, 80kg, 20% BF (64kg lean) | Cunningham | 1908.0 |
| F, 60kg, 30% BF (42kg lean) | Cunningham | 1424.0 |

## Testing

- 45 new unit tests (99 total across the project) across 8 test files:
  one per equation, one for the base contract, one for the registry,
  and one cross-cutting plausibility suite.
- 99% statement coverage on `metabosim.models.bmr` (the 1% gap is the
  abstract method's unreachable-by-design body in `base.py`).
- `mypy --strict`, `black`, `ruff` all clean.

## Verification commands

```bash
pytest tests/unit --cov=metabosim.models.bmr --cov-report=term-missing
mypy --strict src/metabosim/models/bmr
black --check src/metabosim/models/bmr tests/unit/models/bmr
ruff check src/metabosim/models/bmr tests/unit/models/bmr
```

## Not yet done (future phases)

- No selection logic wiring BMR models into a TDEE pipeline yet
  (Phase 5).
- `SimulationConfig` still deferred (see Phase 3 notes) — it will be
  the object that stores *which* BMR model ID a given simulation run
  uses.
- Pediatric-specific BMR equations (e.g. Schofield) are out of scope
  for now; all four implemented equations were validated on adult
  populations per their own source literature (see module docstrings
  for each equation's stated limitations).
