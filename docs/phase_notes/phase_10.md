# Phase 10 — Body Composition Simulation

**Status:** Complete

## What was built

**`metabosim.models.body_composition`** — a new model family:

- **`base.py`** — `BodyCompositionModel`, using a template-method
  pattern: concrete subclasses implement only
  `ffm_fraction_of_change(current_fat_mass_kg, sex) -> float`; the
  base class implements `partition_mass_change_kg` once, in terms of
  that method, guaranteeing the two are always mutually consistent by
  construction rather than by convention.
- **`forbes.py`** — `ForbesPartitionModel`. `dFFM/dBW = C/(C+FM)`
  (Forbes, 1987/2000; Hall, 2007), with sex-specific constants
  (`C=10.4` kg female, Forbes' own derivation; `C=13.8` kg male,
  Thomas et al. 2010 — disclosed as resting on a smaller evidence
  base than the female constant).
- **`registry.py`** — runtime lookup by string ID.

**Integration into `metabosim.simulation`:**

- `SimulationConfig` gained `body_composition_model_id` (default
  `"forbes"`), validated eagerly at construction time.
- `stepper.step()` now accepts an optional `current_fat_mass_kg`.
  When provided, it: (1) updates the day's `Person` copy's
  `body_fat_percent` too, not just `weight_kg`; (2) constructs a
  fresh `TissueEnergyDensityModel` with an `ffm_fraction` computed
  *for that day's current fat mass*, replacing the Phase 8 static
  0.25 default; (3) partitions that day's mass change into fat/lean
  components via the same body composition model, guaranteeing
  consistency with step 2's fraction.
- `Simulator.run()` seeds `current_fat_mass_kg` from
  `person.fat_mass_kg` — a computed property that has existed since
  Phase 3, now finally consumed by something.

## The signature change, and why it was worth it

`step()`'s return type changed from a bare `tuple[SimulationState, float]`
to a `StepResult` `NamedTuple` with four fields
(`state`, `mass_change_rate_kg_per_day`, `next_fat_mass_kg`,
`next_lean_mass_kg`). This is a breaking change to an internal API
within the same evolving package (no external consumers exist yet),
made because a 4-tuple with two conditionally-`None` trailing elements
would have been unclear at every call site, whereas
`result.next_fat_mass_kg` is self-documenting. All Phase 9 tests that
unpacked the old 2-tuple were updated to use attribute access instead.

## Verifying the theory, not just the arithmetic

The Forbes constant has a specific, checkable physical meaning: at
`current_fat_mass_kg == C`, fat and fat-free mass must change in
*exactly* equal amounts (`ffm_fraction_of_change` must return exactly
0.5). This is asserted directly
(`test_exactly_half_at_fat_mass_equal_to_constant`), not just backed
into from the formula.

More importantly, a dedicated engine-level test
(`test_leaner_starting_person_gains_relatively_more_lean_mass`) runs
two full 30-day simulations — one subject at 8% body fat, one at 35%
— under the *identical* diet and activity plan, and confirms the
leaner subject's weight gain is proportionally more lean mass than
the fatter subject's. This checks the model reproduces Forbes'
actual qualitative claim end-to-end through the whole simulation
stack, not merely that the isolated formula evaluates correctly.

## Design decisions

1. **Composition tracking activates automatically, with no new
   boolean flag.** Whether `Simulator` tracks fat/lean mass is
   determined entirely by whether `person.body_fat_percent` is set —
   reusing a Phase 3 computed property (`person.fat_mass_kg`) as the
   activation signal and the initial seed value in one move. A
   separate `track_body_composition: bool` config field was
   considered and rejected: it would create a redundant, potentially
   contradictory second source of truth (what happens if the flag is
   `True` but `body_fat_percent` is `None`?).
2. **The `ffm_fraction` override only applies to
   `tissue_energy_density`.** The other two energy balance models
   (`static_rule`, `dynamic_quasi_exponential`) have no `ffm_fraction`
   concept at all. Rather than silently ignore composition tracking
   for those, or force an interface change onto models that don't
   need one, the stepper checks
   `config.energy_balance_model_id == "tissue_energy_density"`
   explicitly before attempting the override — composition is still
   tracked and reported either way
   (`test_only_overrides_ffm_fraction_for_tissue_energy_density`
   verifies this explicitly with `static_rule` selected).
3. **Per-day discrete application of an infinitesimal formula,
   disclosed as a deliberate choice, not an oversight.** Forbes'
   equation is strictly valid only for infinitesimal changes; Hall
   (2007) derived an exact macroscopic correction for large, single-
   step changes (e.g. bariatric surgery). This project's daily steps
   are small (typically well under 0.1 kg/day), so applying the
   infinitesimal formula as a per-day Euler step is consistent with
   how the rest of the simulation already treats each day as one
   small discrete-time step — documented explicitly in
   `forbes.py`'s module docstring, with Hall's exact solution named
   as the natural extension if large single-step jumps are ever
   needed.
4. **The male-specific Forbes constant is disclosed as
   less-established than the female one.** Forbes' original 10.4 kg
   constant came from his own female-only cross-sectional data;
   13.8 kg for males comes from a different paper (Thomas et al.,
   2010) fitting a different equation form. Both are used as sex-
   specific defaults, but the asymmetry in evidentiary weight is
   stated plainly in the docstring rather than presented as equally
   solid.

## Testing

- 31 new unit tests for `models.body_composition`
  (`tests/unit/models/body_composition/{test_base,test_forbes,test_registry}.py`).
- 6 new/rewritten unit tests in `test_stepper.py` for composition
  tracking (including the Katch-McArdle stale-vs-fresh
  `body_fat_percent` test, and the static-rule-doesn't-break-tracking
  test).
- 7 new unit tests in `test_engine.py`, including the end-to-end
  Forbes-theory validation test described above.
- 98% coverage on `metabosim.models.body_composition` (the one miss
  is `ffm_fraction_of_change`'s unreachable abstract-method body,
  consistent with every other model family); 100% coverage on
  `metabosim.simulation`.
- 335 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/body_composition --cov=metabosim.models.body_composition --cov-report=term-missing
pytest tests/unit/simulation --cov=metabosim.simulation --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No adaptive thermogenesis beyond what real BMR recompute already
  captures — Phase 11 will add the *additional* metabolic slowdown
  observed in sustained deficits beyond what mass and composition
  change alone predict.
- No macronutrient-level state (glycogen, water) — Phase 12. Note
  that short-term weight fluctuations from glycogen-associated water
  are NOT modeled here; every gram of "lean mass" change in this
  phase is treated as structural fat-free tissue, which will
  overstate the smoothness of real short-term weight trajectories
  until Phase 12 separates out water/glycogen dynamics.
- Hall's (2007) exact macroscopic correction is not implemented — see
  design decision 3 above; would matter for large single-step mass
  changes, which this day-by-day simulator doesn't produce.
- No validation against real longitudinal body composition cohort
  data — Phase 17.
