# Phase 14 — Disease Modules

**Status:** Complete

## What was built

**`metabosim.models.disease`** — the Decorator extensibility point
`docs/architecture.md` has promised since Phase 1: "New diseases: add
a decorator in models/disease/, compose over any base model without
modifying that base model."

- **`base.py`** — `DiseaseModifier` (adjustment-logic interface:
  `apply_to_bmr_kcal(base_bmr_kcal, person) -> float`) and
  `DiseaseModifiedBMRModel` (the actual Decorator: wraps any
  `BMRModel` with one or more modifiers, applied in sequence, and
  exposes the standard `BMRModel` interface itself — fully
  substitutable anywhere a base model could be used).
- **`thyroid.py`** — `ThyroidModifier` + `ThyroidStatus` (7-tier
  severity enum). BMR adjustment −10%/−20%/−35% (hypothyroid) or
  +15%/+30%/+50% (hyperthyroid), calibrated to McCullagh's (1938)
  classical clinical BMR-percentage framework.
- **`body_temperature.py`** — `BodyTemperatureModifier`. ±13% BMR
  change per °C deviation from 37°C, applied bidirectionally
  (fever/hypothermia), cited to DuBois (1937).
- **`registry.py`** — kwargs-forwarding lookup, mirroring
  `metabosim.models.activity.registry`.

**Extending `metabosim.models.tdee.calculator`:** both `calculate_tdee()`
and `calculate_tdee_from_components()` now accept `bmr_model_id` as
either a registry string (unchanged) or a pre-built `BMRModel`
instance — which is what makes `DiseaseModifiedBMRModel` usable
throughout the existing TDEE pipeline with zero changes to any other
existing code path. Every existing string-based call site continues
to work identically; a new `CUSTOM_BMR_MODEL_ID = "custom"` sentinel
is reported when an instance was passed instead of a string.

## The literature verified two very different quantitative claims

This phase needed two independently-sourced numbers, and both were
checked against a specific citation before being used, not estimated
from general familiarity with the topic:

1. **Thyroid dysfunction**: McCullagh's 1938 clinical paper documents
   the classical practice of using BMR *itself*, expressed as a
   percentage deviation from predicted, as a diagnostic signal for
   thyroid disease — this was literally how BMR was used clinically
   before modern hormone assays existed. The specific severity tier
   boundaries in `thyroid.py` are disclosed explicitly as an
   interpolation anchored to McCullagh's documented values (the −20%
   myxedema threshold, the +14–22% typical hyperthyroid range), not
   individually re-derived data points for each of the seven tiers.
2. **Fever**: DuBois's 1937 monograph is the canonical primary source
   for the "~13% per °C" rule used across critical care and clinical
   nutrition practice today, nearly 90 years later. Search results
   also confirmed the same relationship holds, in reverse, for
   therapeutic/accidental hypothermia — motivating the bidirectional
   design rather than a fever-only, clamped-at-zero model.

## Two small classes, not one — and why that mattered immediately

Separating `DiseaseModifier` (adjustment logic) from
`DiseaseModifiedBMRModel` (the composition wrapper) meant the ordering
question — does it matter whether you apply thyroid adjustment before
or after a fever adjustment? — could be tested directly and concretely
(`test_order_matters_for_multiplicative_modifiers`), rather than left
as an implicit assumption. It also meant multiple comorbidities
(a patient with both hypothyroidism and a fever) could be composed by
simply passing a list, verified end-to-end
(1780 → ×0.80 → ×1.26 = 1794.24 kcal) without either modifier needing
to know the other exists.

## Why the TDEE calculator's signature change is safe

Widening `bmr_model_id: str` to `bmr_model_id: str | BMRModel` is a
strictly backward-compatible generalization: every existing call site
in the codebase (Phases 5–13, all their tests, and
`metabosim.simulation.stepper`) passes a string and continues to
resolve through the registry exactly as before — verified by running
the complete pre-existing test suite unchanged (all 40 pre-Phase-14
`models.tdee` tests still pass without modification). The new
capability is purely additive.

## Design decisions

1. **No registry entry for `DiseaseModifiedBMRModel` itself.** Unlike
   `ThyroidModifier`/`BodyTemperatureModifier` (which the registry
   *does* cover), the composer requires a runtime `BMRModel` instance
   as a constructor argument, which doesn't fit any registry
   convention in this project (string IDs and simple kwargs, not
   object instances). It remains a plain importable class, used
   directly by callers — the same treatment given to
   `calculate_tdee_from_components` itself, which also isn't a
   "registered model."
2. **Severity is categorical (an enum), not a continuous lab-value
   input**, for thyroid dysfunction. A dose-response model relating
   BMR directly to free T3/T4 concentration would be more precise but
   requires a calibration dataset this phase did not have verified
   access to — implementing it from an unconfirmed guess would have
   been worse than a disclosed, coarser categorical approximation.
3. **The fever/hypothermia coefficient is applied symmetrically**,
   using one cited value (13%) in both directions, even though some
   sources describe hypothermia's effect with a slightly wider
   possible range (5–13%). Documented explicitly as a simplification
   rather than silently picking a single number from within that
   range without saying so.
4. **Sequential composition only — no interaction modeling.** A
   patient with both a severe fever and hypothyroidism gets each
   effect applied to the running total in sequence; nothing in this
   phase attempts to model whether the conditions interact
   synergistically or antagonistically beyond that. Disclosed as a
   known simplification, consistent with the project's established
   practice of stating modeling boundaries plainly.

## Testing

- 46 new unit tests for `models.disease`
  (`tests/unit/models/disease/{test_base,test_thyroid,test_body_temperature,test_registry}.py`),
  99% coverage (the one miss is the abstract method's unreachable
  body, consistent with every other model family).
- 4 new tests for the TDEE calculator's pre-built-model acceptance,
  including a dedicated backward-compatibility check
  (`test_string_bmr_model_id_still_reports_its_own_id`) and a stacked-
  modifier end-to-end verification.
- 505 tests total project-wide; 99% overall coverage; `mypy --strict`,
  `black`, `ruff`, and all doctests clean.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/models/disease --cov=metabosim.models.disease --cov-report=term-missing
pytest tests/unit/models/tdee --cov=metabosim.models.tdee --cov-report=term-missing
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
```

## Not yet done (future phases)

- Disease modifiers are not yet wired into `metabosim.simulation` —
  `SimulationConfig.bmr_model_id` is a plain `str` field (Pydantic-
  typed), so a disease-modified model can't be selected there without
  either widening that field's type or adding a separate config path.
  Deferred rather than rushed, since it wasn't needed to make this
  phase's science fully usable (it already is, via direct
  `calculate_tdee`/`calculate_tdee_from_components` calls).
- No cancer cachexia or diabetes/insulin-resistance modules — both
  were considered (and are mentioned in the project's original Phase
  1 background notes) but neither has as clean a single-multiplier
  quantitative relationship as thyroid dysfunction or fever; modeling
  them properly would need either a more complex multi-factor model
  or a calibration dataset not verified for this phase.
- No sex-specific or lab-value-continuous thyroid dose-response model
  — see design decision 2 above.
- No validation against real clinical thyroid/fever patient cohort
  data — Phase 17.
