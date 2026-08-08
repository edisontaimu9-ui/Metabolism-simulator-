# Phase 8 — Energy Balance Engine

**Status:** Complete

## What was built

`metabosim.models.energy_balance`, three strategies behind a common
`EnergyBalanceModel` interface converting net daily energy balance
(kcal/day) into a rate of body mass change (kg/day):

- **`static_rule.py`** — `StaticEnergyBalanceModel`. The classic 3500
  kcal/lb rule (Wishnofsky, 1958), implemented deliberately and
  explicitly labeled `-- NOT RECOMMENDED`. Kept purely as a documented
  baseline for demonstrating exactly how and why it fails (unbounded
  linear projection — a -500 kcal/day deficit sustained for 10 years
  projects an obviously impossible ~236.5 kg loss).
- **`tissue_energy_density.py`** — `TissueEnergyDensityModel`. The
  minimal, composable "pure conversion" primitive: `rate = balance /
  ρ`, where `ρ` is a blended fat/fat-free-mass energy density (default
  7380 kcal/kg, from Heymsfield et al.'s 2014 "Quarter FFM Rule"
  review). Has no weight-dependent feedback of its own — deliberately,
  since it's intended for composition inside Phase 9's day-by-day
  simulation, which will recompute real BMR/TDEE at each day's updated
  weight and thereby supply that feedback from actual physiology.
- **`dynamic_quasi_exponential.py`** — `DynamicQuasiExponentialModel`.
  A standalone, reduced single-compartment approximation (in the
  spirit of Hall & Jordan, 2008) of the full nonlinear two-compartment
  dynamic model, with a closed-form solution that approaches a
  bounded steady state rather than changing forever. Has its own
  feedback term (`γ`) and must NOT be combined with a real per-day BMR
  recompute.
- **`registry.py`** — runtime lookup by string ID, following the
  simple zero-arg pattern (all three models are zero-arg
  constructible, unlike `models.activity`).

## The double-counting pattern, now seen a second time

This phase is architecturally the same problem already solved in
Phase 7 for TEF/Activity, appearing again one layer up the stack:
**some models build a feedback mechanism into their own closed-form
math, and some models expect that same feedback to be supplied
externally.** Just as `includes_average_tef` distinguished MET-based
from PAL-ratio-based activity models, `includes_weight_dependent_feedback`
distinguishes `TissueEnergyDensityModel` (expects external feedback,
from a real per-day BMR recompute in Phase 9) from
`DynamicQuasiExponentialModel` (supplies its own approximate feedback,
for standalone use without a full simulation). Recognizing this as the
*same class of bug* as Phase 7's, not a new one, is itself a useful
architectural insight worth recording.

## Honest disclosure of an imperfect calibration

`DynamicQuasiExponentialModel`'s default `γ = 20.0 kcal/kg/day` was
**not** taken as a verbatim published parameter — I could not verify
an exact figure from Hall & Jordan (2008) directly from memory, and
rather than assert false precision, I used `web_search` to find a
different, verifiable anchor: a widely-cited illustrative example (a
100 kg sedentary male at a sustained -500 kcal/day deficit approaching
a ~75 kg steady state, per Yoo, 2018, citing Hall's model) and
back-derived `γ = 500/25 = 20` from that example's implied steady
state. This is disclosed explicitly, both in the module docstring and
here, as a back-of-envelope calibration against one illustrative
example, not a formally re-fitted parameter. The reduced model's own
predictions were then checked against the same source's qualitative
timeline claims (roughly half the total loss within 1 year, ~95%
within 3 years for the full nonlinear model): this reduced model's
3-year prediction (95% of steady state) matches well; its 1-year
prediction (63% of steady state) is higher than the ~50% reported for
the full model — an expected, disclosed consequence of using a linear
single-compartment approximation for a genuinely nonlinear,
two-compartment system. Nothing here was smoothed over to look more
precise than it is.

## Design decisions

1. **Two return methods on the interface, not one.** `EnergyBalanceModel`
   exposes both `mass_change_rate_kg_per_day` (an instantaneous rate,
   for Phase 9's day-by-day stepper to call repeatedly) and
   `project_weight_change_kg` (a closed-form total over a sustained
   constant period, for fast standalone projections and for validating
   the rate function against a known analytic solution). A dedicated
   test (`test_rate_integral_matches_closed_form_numerically`)
   confirms the two are mutually consistent by numerically integrating
   the rate function and comparing it to the closed form.
2. **`includes_weight_dependent_feedback` has no default**, mirroring
   Phase 7's `includes_average_tef` — forgetting to declare it is a
   loud `AttributeError`, not a silent wrong assumption.
3. **The static rule is implemented, not just described.** Rather than
   only writing about why the 3500 kcal/lb rule is wrong, it's a real,
   working, tested model in the registry — so any future report or
   comparison (Phase 16/17) can literally run both models side by side
   on the same scenario and show the divergence numerically, not just
   assert it in prose.
4. **`TissueEnergyDensityModel.ffm_fraction` is a constructor
   parameter, not a hardcoded constant.** This is a forward hook for
   Phase 10 (body composition) to supply a dynamically computed,
   subject-specific FFM fraction (via the Forbes partitioning curve)
   instead of the static 0.25 population-average default, without
   requiring any interface change.

## Testing

- 58 unit tests across 5 test files
  (`tests/unit/models/energy_balance/{test_base,test_static_rule,test_tissue_energy_density,test_dynamic_quasi_exponential,test_registry}.py`).
- 98% statement coverage on `metabosim.models.energy_balance` (the two
  misses are the abstract methods' unreachable `raise NotImplementedError`
  bodies, consistent with every other model family).
- Every closed-form docstring number (23.65 kg, 236.5 kg, 15.7 kg,
  23.7 kg, 25.0 kg, 7380 kcal/kg, 369-day time constant) was computed
  in Python and cross-checked before being written into documentation
  or tests — none were asserted from memory alone.
- 260 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/energy_balance --cov=metabosim.models.energy_balance --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim/models/energy_balance
black --check src/metabosim/models/energy_balance tests/unit/models/energy_balance
ruff check src/metabosim/models/energy_balance tests/unit/models/energy_balance
```

## Not yet done (future phases)

- No day-by-day time-stepping simulation yet — that's Phase 9 (Body
  Weight Simulation), which will consume
  `TissueEnergyDensityModel.mass_change_rate_kg_per_day` alongside a
  real per-day BMR/TDEE recompute.
- No fat/lean mass split — `ffm_fraction` is a single static
  population-average default until Phase 10 (Body Composition
  Simulation) supplies a dynamically computed, subject-specific value
  via the Forbes curve.
- The full nonlinear two-compartment Hall model itself is not
  implemented — `DynamicQuasiExponentialModel` is an explicitly
  reduced, single-compartment linear approximation, with its
  divergence from the full model's reported timeline disclosed above.
- No validation against real cohort data — Phase 17.
