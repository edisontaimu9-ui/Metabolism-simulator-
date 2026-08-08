# Phase 9 — Body Weight Simulation

**Status:** Complete

## What was built

`metabosim.simulation` — the day-by-day simulation engine that finally
assembles Phases 4-8 into an actual time-varying trajectory:

- **`config.py`** — `DailyPlan` (one day's diet + logged activity) and
  `SimulationConfig` (which model strategies to use, how many days to
  run). `SimulationConfig` eagerly validates, at construction time,
  that the chosen `energy_balance_model_id` won't double-count
  weight-dependent expenditure feedback.
- **`stepper.py`** — `step()`, a pure function: current weight + a
  day's plan + config → that day's `SimulationState` + the mass-change
  rate to apply next. Independently unit-testable, with no dependency
  on the engine's looping logic.
- **`engine.py`** — `Simulator`, which repeatedly calls `step()` to
  produce a full `list[SimulationState]` history.

This is the piece `docs/phase_notes/phase_03.md` explicitly deferred
building (`SimulationConfig` needed model registries that didn't exist
yet) and the piece every prior phase's "not yet done" section pointed
toward.

## The payoff: real physiological feedback, not an approximated constant

Every day, the stepper constructs a fresh `Person` copy at that day's
*current* weight and recomputes real BMR via
`metabosim.models.bmr`/`tdee`. This means a 30-day simulation of a
sustained ~141 kcal/day surplus shows the surplus itself *shrinking*
day over day (141.1 → 132.7 kcal/day by day 30) purely because a
heavier body has a higher Mifflin-St Jeor BMR — verified directly by
`test_real_bmr_recompute_shrinks_surplus_over_time`. This is exactly
the negative feedback that Phase 8's `DynamicQuasiExponentialModel`
had to *approximate* with a `γ` constant; here, it emerges from the
real domain models instead. This is also precisely why
`SimulationConfig` defaults to (and validates against anything but)
`energy_balance_model_id="tissue_energy_density"` — that model has no
feedback term of its own, because this simulator already supplies the
feedback for real.

## The double-counting pattern, resolved for the third time

Phase 7 introduced `includes_average_tef`; Phase 8 introduced
`includes_weight_dependent_feedback` but explicitly deferred
*enforcing* it, noting "Phase 9 will use this flag." This phase is
that enforcement, in two layers:

1. `SimulationConfig`'s `model_validator` checks the flag eagerly at
   config-construction time — the earliest possible failure point.
2. `stepper.step()` checks the same flag again, independently, as
   defense-in-depth for any caller who bypasses `SimulationConfig`'s
   validation (e.g. via `model_construct()`). A dedicated test
   (`test_feedback_including_model_raises_via_manual_bypass`)
   deliberately bypasses the config-level check specifically to prove
   the stepper-level check works on its own, not merely because the
   config never let a bad value through.

## Design decisions

1. **No `activity_model_id` option in `SimulationConfig`.** Activity
   is always MET-based, driven by `DailyPlan.activity_entries` — the
   only activity strategy documented as safe to combine with a real
   per-day BMR recompute (Phase 7). Exposing a configurable choice
   here would just be exposing a footgun with no legitimate use case
   inside this specific engine. `Person.activity_level` is
   consequently unused by this simulator — documented prominently in
   three places (`config.py`, `stepper.py`, `engine.py` docstrings) so
   it isn't a silent surprise.
2. **The row convention: `days + 1` states, not `days`.** State `i`'s
   weight is measured at the *start* of day `i`; state `i`'s energy
   figures describe what happens *during* day `i`. The final state
   (index `days`) reports genuinely useful "where things stand now"
   energetics (current BMR/TDEE at the final weight) rather than being
   an empty or wasted row — verified by
   `test_list_of_varying_plans_produces_varying_intake`, which checks
   that the final state correctly re-reports the last configured
   plan's figures.
3. **`Person` is never mutated.** Each day's BMR calculation uses
   `person_template.model_copy(update={"weight_kg": ...})`, never
   in-place mutation — verified by dedicated immutability tests at
   both the stepper and engine level. This matches the "immutable
   value objects" principle from Phase 1's coding standards.
4. **Body composition (fat vs. lean mass) is not tracked yet.**
   `SimulationState.fat_mass_kg`/`lean_mass_kg` are left `None`
   throughout — `TissueEnergyDensityModel`'s `ffm_fraction` stays at
   its static 0.25 default for the whole simulation. This is exactly
   the gap Phase 10 (Body Composition Simulation) exists to fill,
   without requiring any interface change here.

## Testing

- 32 unit tests across 3 test files
  (`tests/unit/simulation/{test_config,test_stepper,test_engine}.py`
  plus `conftest.py` fixtures).
- 100% statement coverage on `metabosim.simulation`.
- Every reference number in `test_stepper.py` (BMR 1780.0, TDEE
  2438.9, intake 2580.0, balance 141.1, rate ≈0.019119) was
  independently computed in Python and cross-checked against the
  actual values used in Phases 5-8's own tests, confirming the new
  composition layer reproduces exactly what the underlying models
  already proved correct in isolation.
- 291 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/simulation --cov=metabosim.simulation --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim/simulation
black --check src/metabosim/simulation tests/unit/simulation
ruff check src/metabosim/simulation tests/unit/simulation
```

## Not yet done (future phases)

- No fat/lean mass tracking — Phase 10 (Body Composition Simulation)
  will supply a dynamically computed `ffm_fraction` per day instead of
  the static 0.25 default, and populate
  `SimulationState.fat_mass_kg`/`lean_mass_kg`.
- No adaptive thermogenesis beyond what real BMR recompute already
  captures — Phase 11 will add the *additional* metabolic slowdown
  observed in sustained deficits beyond what mass change alone
  predicts (Minnesota Starvation Experiment, Biggest Loser follow-up).
- No macronutrient-level state (glycogen, water) — Phase 12.
- `SimulationConfig.bmr_model_id` and `tef_model_id` are not validated
  eagerly at construction time (only `energy_balance_model_id` is, for
  the double-counting safety reason above) — an unknown
  `bmr_model_id` will raise a clear `KeyError` only once `run()` is
  called. This asymmetry is documented and tested explicitly
  (`test_unknown_bmr_model_id_is_not_validated_eagerly`) rather than
  left as an implicit inconsistency; could be revisited if it proves
  confusing in practice.
