# Phase 12 — Macronutrient Metabolism

**Status:** Complete

## What was built

**`metabosim.models.macronutrient`** — glycogen (and associated water)
dynamics, deliberately **without a registry**, unlike every other
model family in this project:

- **`glycogen.py`** — four pure functions: `max_glycogen_g(weight_kg)`,
  `glycogen_and_water_kg(glycogen_g)`, `step_glycogen_g(...)`, and
  `step_reference_carbohydrate_intake_g(...)`. Cited constants:
  hydration coefficient 2.7 g water/g glycogen and ~500 g storage
  capacity at 70 kg reference weight (both from Chow & Hall, 2008 and
  a 2024 peer-reviewed physiology-education article, respectively).

**Integration into `metabosim.simulation`:**

- `stepper.step()` gained `current_glycogen_g` and
  `current_reference_carbohydrate_intake_g` parameters, activating
  glycogen tracking independently of body composition tracking.
  `StepResult` gained two corresponding `next_*` fields.
- `Simulator` gained `initial_glycogen_g` and
  `initial_reference_carbohydrate_intake_g` constructor parameters.
- `SimulationState.glycogen_g` and `.total_body_water_kg` — both
  present but always `None` since Phase 3 — are finally populated.

## Why there's no registry here

Every other model family in this project uses the Strategy pattern
with a registry because it represents genuinely competing scientific
hypotheses (BMR equations, adaptive thermogenesis archetypes, etc.).
Glycogen's hydration coefficient is not a competing hypothesis — it's
a cited physical/chemical property of glycogen granules. Building a
registry with one entry would be false symmetry with the rest of the
codebase, so this phase's module docstring says so explicitly rather
than silently breaking the established pattern without explanation.

## The literature handed this phase its own scope, precisely

Chow & Hall (2008) doesn't just supply the hydration constant — it
explicitly states that carbohydrate balance is maintained at
quasi-equilibrium (`dG/dt ≈ 0`) on timescales beyond "a few days,"
and that this is *why* reduced models (fat + lean mass only, ignoring
glycogen) are valid for anything longer. That is a precise,
citable description of exactly what Phases 8–11 already do. This
phase's job was therefore not to replace that reduced model, but to
fill in precisely the short transient window the reduced model
deliberately skips — and to hand off cleanly once the transient
resolves. Recognizing that the primary literature had already drawn
the exact boundary this project's phases fall on either side of was
the single most useful thing this phase's research turned up.

## No double-counting, verified structurally and by test

The glycogen transient is computed independently of the energy-
balance-driven rate, then added to it afterward; the Forbes
partitioning (Phase 10) is applied only to the energy-balance-driven
portion, never to the glycogen transient, which — when body
composition is also tracked — is attributed entirely to lean mass
(matching Chow & Hall's own convention that glycogen and its water
are part of fat-free mass). A dedicated test
(`test_glycogen_transient_is_attributed_to_lean_not_fat`) confirms
`next_fat_mass_kg + next_lean_mass_kg` still equals
`current_weight_kg + total_rate` exactly, even with both fat/lean
and glycogen tracking active simultaneously.

## An existing docstring needed clarifying, not changing

Phase 3's original wording for `total_body_water_kg` ("relevant for
explaining short-term weight fluctuations that are not fat/lean mass
changes") could be read as implying water sits *outside* the
fat/lean partition — which would conflict with Chow & Hall's actual
convention (glycogen + water *are* part of lean mass) and would have
required loosening the `fat_mass_kg + lean_mass_kg ≈ weight_kg`
invariant that Phase 10 already validated. Rather than either
silently contradicting the primary literature or breaking a tested
invariant, the docstring was clarified (not the field types or the
validator) to state the Chow & Hall convention explicitly: these two
fields are informational breakdowns of what's already inside
`lean_mass_kg`, not separate additive ledger entries.

## What was verified, not assumed

- The end-to-end low-carb switch scenario (300g habitual → 20g/day)
  depletes glycogen to near-zero within 2 days, losing ~1.1 kg of
  glycogen+water — independently matching commonly-described
  magnitudes for the real "water weight" phenomenon, without having
  been tuned to hit that number.
- The reverse (refeed) scenario replenishes glycogen back to capacity
  within a similar timeframe.
- A dedicated engine-level test
  (`test_diet_switch_produces_sharp_transient_drop`) confirms the
  transition day's weight drop is more than 5x any single day's drop
  once the transient has resolved and only the smooth underlying
  trend remains.
- `test_transient_resolves_and_hands_off_to_smooth_trend` confirms
  glycogen reaches a stable near-zero level and subsequent day-to-day
  weight deltas become small and consistent — i.e. the transient
  genuinely fades rather than persisting or oscillating.

## Design decisions

1. **Carbohydrate oxidation is estimated via an exponential moving
   average of recent intake, disclosed as a pragmatic simplification
   — the one piece of this phase that is NOT a directly cited
   parameter.** True oxidation estimation requires respiratory-
   quotient/indirect-calorimetry data or Hall's full mechanistic
   partitioning model, both out of scope. The EMA's 3-day time
   constant is chosen only to match Chow & Hall's qualitative "a few
   days" description, not independently fitted.
2. **Storage capacity scales linearly with total body weight**, a
   documented simplification — true capacity tracks muscle mass
   specifically, which this project does not track as a separate
   compartment.
3. **The default reference-intake seed is day 0's own planned
   carbohydrate intake**, not a separate required parameter. This
   means a `Simulator` run with a single constant `DailyPlan` and
   glycogen tracking enabled produces *zero* transient by
   construction (verified by
   `test_default_reference_matches_day_zero_intake_giving_no_initial_transient`)
   — the transient only appears when intake actually changes, which
   is the physiologically correct behavior and requires no special-
   casing in the implementation.
4. **De novo lipogenesis (excess carbohydrate beyond glycogen capacity
   converting to fat) is not modeled.** Glycogen is simply clamped at
   capacity; carbohydrate balance beyond that point is not separately
   tracked. Disclosed as a known simplification in `glycogen.py`'s
   module docstring rather than silently ignored.

## Testing

- 24 new unit tests for `models.macronutrient`
  (`tests/unit/models/macronutrient/test_glycogen.py`), 100% coverage.
- New stepper-level tests (`TestStepGlycogenTracking`, 7 tests)
  covering activation, validation of the paired-parameter
  requirement, state population, and non-double-counting with
  simultaneous composition tracking.
- New engine-level tests (`TestSimulatorGlycogenTracking`, 6 tests)
  covering the full diet-switch scenario, transient resolution, and
  explicit reference seeding.
- 428 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/macronutrient --cov=metabosim.models.macronutrient --cov-report=term-missing
pytest tests/unit/simulation --cov=metabosim.simulation --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No organ-level metabolic contributions — Phase 13.
- No full substrate oxidation / respiratory quotient modeling (fat
  vs. carbohydrate vs. protein oxidation rates) — carbohydrate
  oxidation is estimated only as a simple EMA, not derived from
  indirect calorimetry principles.
- No de novo lipogenesis modeling for carbohydrate intake exceeding
  glycogen storage capacity (see design decision 4 above).
- No sodium/electrolyte-driven fluid shifts or broader hydration
  status modeling — `total_body_water_kg` captures only the
  glycogen-associated component, as documented.
- No validation against real short-term weight-fluctuation cohort
  data — Phase 17.
