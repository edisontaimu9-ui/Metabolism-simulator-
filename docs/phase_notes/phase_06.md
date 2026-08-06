# Phase 6 — Thermic Effect of Food

**Status:** Complete

## What was built

`metabosim.models.tef`:

- **`base.py`** — `TEFModel`, the abstract strategy interface.
  `calculate(macros: MacronutrientGrams) -> float`, returning the
  estimated TEF in kcal/day.
- **`macronutrient_specific.py`** — `MacronutrientSpecificTEF`.
  Weights each macronutrient's own energy contribution by its own
  published thermic cost fraction (protein 25%, carbohydrate 7.5%,
  fat 2%, alcohol 20% — midpoints of the ranges in Jequier & Tappy,
  1999). This is the scientifically preferred model whenever a
  macronutrient breakdown is available, since diet *composition*
  measurably changes TEF at matched total calories (verified by a
  test comparing a pure-protein vs. pure-fat diet at ~400 kcal each).
- **`fixed_percentage.py`** — `FixedPercentageTEF`. Flat ~10% of
  total energy intake (IOM, 2005), for when only total intake is
  known. Explicitly tested to demonstrate its documented limitation:
  it cannot distinguish a high-protein from a high-fat diet at
  matched calories, unlike the macronutrient-specific model.
- **`registry.py`** — runtime lookup by string ID, mirroring
  `models.bmr.registry` and `models.tdee.registry`.

## Design decisions

1. **Two models, not one, from the start.** Rather than pick a single
   "best" TEF model, both the scientifically richer
   (macronutrient-specific) and the practically simpler
   (fixed-percentage) approaches are implemented, since real usage
   will sometimes lack a macronutrient breakdown. The registry makes
   choosing between them a one-line decision for any future caller.
2. **Fiber's thermic cost is a documented approximation, not silently
   ignored.** Jequier & Tappy (1999) doesn't separately characterize
   fiber. Rather than drop fiber from the TEF calculation entirely
   (which would understate TEF for high-fiber diets) or invent an
   unsourced fiber-specific factor, fiber's Atwater energy is folded
   into the carbohydrate thermic fraction, with an explicit docstring
   caveat that this likely somewhat overstates fiber's true thermic
   cost (a meaningful fraction of fiber's counted energy comes from
   colonic fermentation, not the same digestion pathway as available
   carbohydrate). This is the kind of assumption the project's
   architecture explicitly wants surfaced, not buried.
3. **Point estimates, not ranges, for now.** Jequier & Tappy report
   ranges (e.g. protein 20-30%), and this implementation uses only
   the midpoint. Exposing the full range as a confidence interval is
   noted as a possible future extension rather than built now, to
   keep Phase 6's scope focused on a correct, well-tested point
   estimate.
4. **TEF is NOT wired into `calculate_tdee()` this phase.** As
   flagged in Phase 5's notes, the PAL-multiplier TDEE model's
   published multipliers already implicitly bundle an average TEF.
   Adding this phase's explicit TEF on top would double-count
   food-processing energy cost. `metabosim.models.tef` is therefore
   built, documented, and tested as a fully correct standalone
   component, but its integration into the energy-expenditure
   pipeline is deferred.

## The integration plan (deferred, not forgotten)

Resolving the double-counting issue properly requires one of:

- **(a)** Building `metabosim.models.activity` (Phase 7) with an
  explicit MET-based activity energy model, so TDEE can be assembled
  as BMR + activity-only + TEF, each computed independently, instead
  of BMR × one bundled multiplier.
- **(b)** Deriving or sourcing an alternative TDEE multiplier table
  that is explicitly activity-only (TEF excluded), so the current
  `PALMultiplierTDEE` output could be safely added to this phase's
  TEF output.

Option (a) is architecturally cleaner and consistent with the
project's existing plan to add MET-based activity modeling in Phase 7,
so it's the intended path. This decision is recorded here so it isn't
re-litigated from scratch when Phase 7 begins — the wiring work will
land in `metabosim.models.tdee.calculator` (or a new energy-balance
composition layer, Phase 8) once activity-only expenditure exists.

## Testing

- 23 unit tests across 4 test files
  (`tests/unit/models/tef/{test_base,test_macronutrient_specific,test_fixed_percentage,test_registry}.py`
  plus `conftest.py` fixtures).
- 98% statement coverage on `metabosim.models.tef` (the sole miss is
  the abstract method's `raise NotImplementedError` body, unreachable
  by construction — consistent with `models.bmr` and `models.tdee`).
- Reference values hand-computed and cross-checked in code comments
  (e.g. mixed diet -> 258.9 kcal TEF under the macronutrient-specific
  model, 258.0 kcal under the fixed-percentage model).
- A dedicated test (`test_protein_has_highest_thermic_cost_per_kcal`)
  verifies the macronutrient-specific model actually reproduces the
  qualitative literature finding that protein has a higher thermic
  cost than fat at matched calories — not just that the arithmetic is
  internally consistent.
- `mypy --strict`, `black`, `ruff` all clean.
- Full project suite: 99% overall coverage, all green, including
  doctests.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/tef --cov=metabosim.models.tef --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim/models/tef
black --check src/metabosim/models/tef tests/unit/models/tef
ruff check src/metabosim/models/tef tests/unit/models/tef
```

## Not yet done (future phases)

- TEF is not yet wired into `calculate_tdee()` or any energy-balance
  calculation — see the integration plan above (Phase 7/8).
- No MET-based activity model yet (Phase 7).
- TEF ranges (vs. point estimates) not modeled.
- No validation against measured indirect-calorimetry TEF data
  (Phase 17).
