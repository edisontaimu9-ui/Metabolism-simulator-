# Phase 11 — Adaptive Thermogenesis

**Status:** Complete

## What was built

**`metabosim.models.adaptive_thermogenesis`** — a new model family
implementing three competing strategies, matching a framework taken
directly from the literature rather than invented for this project:

- **`base.py`** — `AdaptiveThermogenesisModel`, the strategy
  interface: `calculate_adjustment_kcal(baseline_weight_kg,
  current_weight_kg, reference_expenditure_kcal) -> float`.
- **`none.py`** — `NoAdaptiveThermogenesisModel`. Always returns 0.0.
  Rosenbaum & Leibel's "Model 1."
- **`threshold.py`** — `ThresholdAdaptiveThermogenesisModel`. A fixed
  ±15% adjustment activates once weight change reaches ±10%, with no
  further scaling beyond that. Rosenbaum & Leibel's "Model 2."
- **`proportional.py`** — `ProportionalAdaptiveThermogenesisModel`.
  The adjustment scales continuously and linearly with the
  weight-change fraction (calibrated so 10% change → 15% adjustment,
  i.e. slope = 1.5), clamped at ±20% (Leibel's most extreme tested
  condition) to avoid unbounded extrapolation. Rosenbaum & Leibel's
  "Model 3" ("spring-loading").
- **`registry.py`** — runtime lookup by string ID.

**Integration into `metabosim.simulation`:**

- `SimulationConfig` gained `adaptive_thermogenesis_model_id`
  (default `"none"`), validated eagerly at construction time.
- `stepper.step()` now computes the naive predicted TDEE (real BMR +
  activity + TEF, unchanged from Phase 7), then applies the
  configured adaptation model's adjustment on top of it to get the
  *effective* expenditure that actually drives the day's energy
  balance. `SimulationState.tdee_kcal` keeps the naive prediction;
  `energy_expenditure_kcal` and `adaptive_thermogenesis_kcal` both
  reflect the adjustment — exactly the relationship the domain
  model's own docstring described since Phase 3, now finally
  populated with real values instead of an always-zero placeholder.

## The literature gave the architecture, not the other way around

Rosenbaum & Leibel's 2016 *Obesity* paper doesn't just report a
finding — it explicitly frames and statistically compares three named
competing model structures for how adaptation relates to weight
change magnitude. That framework maps directly onto this project's
established Strategy-pattern architecture without any translation
effort: three named, independently selectable, independently citable
classes. This is worth noting because it's the cleanest case yet of
the literature itself suggesting the software architecture, rather
than the architecture being imposed on the literature.

## Verifying the real-world consequence, not just the formula

A dedicated engine-level test
(`test_proportional_adaptation_slows_weight_loss_over_a_full_simulation`)
runs the *same* person, the *same* deficit-inducing diet, for the
*same* 100 days — once with `"none"`, once with `"proportional"` — and
confirms strictly less total weight is lost when adaptation is
modeled. This is the actual, citable, real-world phenomenon (adaptive
thermogenesis measurably slows further weight loss) reproduced
end-to-end through the whole simulation stack, not just verified as
isolated arithmetic on the adaptation formula itself. A companion test
confirms the threshold model's adjustment stays pinned at exactly
-15% of that day's own TDEE once activated, regardless of how far
weight drops beyond the 10% threshold — the defining behavioral
difference from the continuously-scaling proportional model.

## Design decisions

1. **The default is `"none"`, deliberately, and this is argued for
   rather than assumed.** Every other model family in this project
   (BMR, TDEE, TEF, Activity, Energy Balance, Body Composition) has a
   clearly best-supported default. Adaptive thermogenesis does not:
   Martins et al. (2020) directly titled a paper "Metabolic adaptation
   is an illusion, only present when participants are in negative
   energy balance," arguing much of the *apparent* adaptation
   reported acutely resolves once weight stabilizes. Given that live
   scientific disagreement, defaulting to an unadjusted prediction
   was judged more defensible than silently picking a side.
2. **Both `threshold` and `proportional` share one calibration
   point** (10% change → 15% adjustment), traced to a single,
   specific, quoted sentence from Goldsmith et al. (2010) rather than
   to a vaguely-remembered percentage — the exact source and quote
   are in `proportional.py`'s module docstring.
3. **The proportional model's linear extrapolation beyond ±20% is
   named as an assumption of the model's own definition, not an
   independently measured data point.** Leibel's protocol tested up
   to ~20% weight change; nothing in the cited literature confirms
   that, say, a 40% weight change produces exactly 60% adaptation.
   Clamping at ±20% keeps the model from extrapolating into
   physiologically implausible territory while being explicit that
   this is where the empirical evidence actually stops.
4. **Fothergill (2016)'s ~500 kcal/day Biggest Loser figure is cited
   as qualitative supporting context, not as a calibration source.**
   That cohort's weight change (up to 58 kg on some subjects) is far
   outside the ~10-20% range Leibel's controlled experiments actually
   tested; using it to fit this project's default parameters would
   have been extrapolating from a very different population and
   protocol. It's cited for what Fothergill's own paper concludes
   ("proportional, but incomplete") as corroboration of the
   proportional archetype's general shape, with that distinction
   made explicit in the citation itself.

## Testing

- 43 new unit tests for `models.adaptive_thermogenesis`
  (`tests/unit/models/adaptive_thermogenesis/{test_base,test_none,test_proportional,test_threshold,test_registry}.py`).
- New tests in `test_stepper.py` (adaptation wiring at the single-day
  level: naive TDEE stays unchanged, effective expenditure reflects
  the adjustment, mass-change rate responds correctly) and
  `test_engine.py` (the full end-to-end weight-loss-slowing
  demonstration, and the threshold model's flat-fraction-once-activated
  property).
- 99% coverage on `metabosim.models.adaptive_thermogenesis` (the one
  miss is the abstract method's unreachable `raise NotImplementedError`
  body, consistent with every other model family); 100% coverage on
  `metabosim.simulation`.
- 391 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.
- Every calibration number (15%, 10%, 1.5 slope, 20% clamp) was
  verified against a directly-quoted literature source via web search
  before being written into code or documentation — none were
  asserted from memory alone.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/adaptive_thermogenesis --cov=metabosim.models.adaptive_thermogenesis --cov-report=term-missing
pytest tests/unit/simulation --cov=metabosim.simulation --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No macronutrient-level state (glycogen, water) — Phase 12.
- No organ-level metabolic contributions — Phase 13.
- The proportional/threshold models scale against the *current day's*
  naive TDEE; neither models the *time course* of adaptation onset
  (real adaptation is thought to build gradually over weeks, not
  appear instantly at the new weight) — a relaxation/lag dynamic (as
  hinted at by Martins et al. 2020's finding that ~half of acute
  adaptation resolves within 4 weeks of stabilization) is a plausible
  future refinement, not implemented here.
- No validation against real longitudinal metabolic adaptation cohort
  data beyond the calibration/qualitative-comparison points already
  used — formal validation belongs to Phase 17.
