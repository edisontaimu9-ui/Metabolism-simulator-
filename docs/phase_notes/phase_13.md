# Phase 13 — Organ Metabolism

**Status:** Complete

## What was built

**`metabosim.models.organ`** — a new model family, deliberately
**without a registry**, following the precedent set in Phase 12:

- **`elia.py`** — `calculate_organ_bmr_breakdown_kcal(fat_mass_kg,
  lean_mass_kg, age_years=None) -> OrganBMRBreakdown`. Decomposes
  whole-body BMR into brain, liver, heart, kidneys, residual lean
  tissue, and adipose tissue contributions, using Elia's (1992) cited
  specific metabolic rates (Ki, kcal/kg/day) applied to fixed
  reference organ masses (Molina & DiMaio, 2012, peer-reviewed
  autopsy data) plus the subject's own tracked fat/lean mass.
  Automatically switches to age-adjusted Ki values (Wang et al., 2010)
  for subjects over 50.

**Integration into `metabosim.models.bmr`:**

- **`elia_organ_based.py`** — `EliaOrganBasedBMR`, a new `BMRModel`
  implementation wrapping the organ breakdown's `total_kcal`,
  registered as `"elia_organ_based"` in the existing BMR registry
  alongside Mifflin-St Jeor, Harris-Benedict, Katch-McArdle, and
  Cunningham. This makes Phase 13's science immediately usable
  everywhere a BMR model already is — `calculate_tdee()`,
  `calculate_tdee_from_components()`, `SimulationConfig.bmr_model_id`
  — with zero changes needed to any of that existing machinery.

## Why this phase doesn't touch the simulation engine

Every phase since 9 has modified `metabosim.simulation` because each
introduced a new *mechanism* that changes the simulated trajectory
(body composition partitioning, adaptive thermogenesis, glycogen
transients). Organ-level decomposition changes nothing about the
physics — it's a different way of *computing and explaining* the same
BMR number, not a new physical effect. Wiring it in as a fifth BMR
strategy (reusing Phase 4's registry) was the correct scope: it makes
the model fully usable without inventing integration work that
wouldn't change any simulated outcome.

## An independent cross-check, not a replacement

This is the first BMR model in the project derived from an entirely
different kind of data (organ-specific metabolic rate studies) than
the regression equations (Mifflin-St Jeor, Harris-Benedict) it now
sits alongside in the registry. For the project's standard worked
example (80 kg male, 20% body fat), the two methods agree to within
about 3% (1726.7 kcal organ-based vs. 1780.0 kcal Mifflin-St Jeor) —
close enough to be a meaningful sanity check on both, without being
suspiciously identical (which would suggest one had been tuned to
match the other, rather than genuinely independently derived). A
dedicated test (`test_reference_total_reasonably_close_to_mifflin_st_jeor`)
asserts this agreement stays within 10%, and the existing
cross-model plausibility suite (Phase 4) now includes this model in
its "no two equations should disagree wildly" check.

## Why there's no registry (again)

Same reasoning as Phase 12: Elia's Ki table is a cited empirical
dataset, not a competing hypothesis with named scientific
alternatives. A registry with one entry per organ-mass model would be
false symmetry with the genuinely-competing-strategy families
elsewhere in this project (BMR equations, adaptive thermogenesis
archetypes). The module docstring says so explicitly rather than
silently breaking the established pattern without explanation, again
following the precedent this project set in Phase 12.

## Design decisions

1. **Skeletal muscle and residual mass are blended into one
   "residual lean" bucket**, because this project tracks only total
   lean mass, not skeletal muscle mass separately, and because Elia's
   own rates for the two tissues (13 vs. 12 kcal/kg/day) are close
   enough that the simplification's impact on the total is minimal —
   stated explicitly rather than silently absorbed.
2. **Reference organ masses are fixed constants, not scaled to the
   subject's size.** This is the standard practice in this literature
   when individual organ imaging isn't available (contrast with Wang
   et al.'s own MRI-based validation studies, a different use case).
   Disclosed explicitly, including the fact that only male autopsy
   data was used as the default (companion female-specific studies
   exist but their exact figures weren't verified for this phase, so
   they were not used rather than guessed at).
3. **Age adjustment uses a hard threshold (>50 years) between two
   discrete cited datasets**, rather than a continuous interpolation
   between them — Wang et al. (2010) report the adjustment for an
   over-50 cohort as a single set of values, not a continuous
   age-dependent function, so a threshold switch is the most faithful
   reading of that source without inventing an interpolation the
   primary literature doesn't provide.
4. **A minimum lean mass is enforced** (must exceed the combined
   fixed-organ reference mass, ~3.53 kg) — a subject smaller than that
   is incompatible with the adult reference constants this model
   assumes, and the resulting negative "residual lean mass" would be
   physiologically meaningless. The model raises a clear error rather
   than silently producing a nonsensical negative tissue mass.

## Testing

- 18 new unit tests for `models.organ`
  (`tests/unit/models/organ/test_elia.py`), 100% coverage.
- 6 new unit tests for `EliaOrganBasedBMR`
  (`tests/unit/models/bmr/test_elia_organ_based.py`), plus updates to
  the existing registry test (five models now, not four) and the
  cross-model plausibility suite (added to `_LEAN_MASS_MODELS`,
  confirmed sex-independence, confirmed all five equations still
  agree within a plausible range for a typical adult).
- 455 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.
- Every numeric claim (Ki values, reference organ masses, the
  worked-example totals, the age-adjustment figures) was verified via
  web search against a specific cited source before being written
  into code, tests, or documentation.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/organ --cov=metabosim.models.organ --cov-report=term-missing
pytest tests/unit/models/bmr --cov=metabosim.models.bmr --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- No disease-specific modifiers yet — Phase 14, which will likely
  decorate over both the regression-based and organ-based BMR models
  (e.g. thyroid dysfunction affecting specific organ Ki values would
  be a natural extension point this phase's structure enables, though
  not implemented now).
- Sex-specific reference organ masses are not implemented — the
  companion Molina et al. (2015) women's studies exist but weren't
  verified precisely enough to use confidently in this phase; using
  one sex-unadjusted set for both sexes is disclosed as a known
  approximation.
- No validation against real doubly-labeled-water or organ-imaging
  cohort data — Phase 17.
