# Phase 3 — Data Models

**Status:** Complete

## What was built

Five modules in `metabosim.domain`, all dependency-free (no imports
from `metabosim.models` or `metabosim.simulation`, per the Phase 1
architecture rule that data flows strictly forward):

- **`constants.py`** — physiological plausibility bounds (age, height,
  weight, body fat %) and Atwater general energy factors, each with an
  inline citation (FAO 2003, IOM 2005, Gallagher et al. 2000, Guinness
  World Records for extreme-but-real height/age bounds).
- **`enums.py`** — `Sex`, `ActivityLevel`, `UnitSystem`, implemented as
  `enum.StrEnum` (Python 3.12+) rather than the older `(str, Enum)`
  idiom, per `ruff`'s `UP042` recommendation.
- **`units.py`** — pure conversion helpers (kg↔lb, cm↔in, kcal↔kJ,
  cm↔ft/in) for presentation-layer use only; internal calculations
  never call these, since domain models always store canonical units.
- **`person.py`** — `Person`: the subject snapshot. Includes computed
  fields `bmi`, `fat_mass_kg`, `lean_mass_kg`. `fat_mass_kg`/
  `lean_mass_kg` deliberately return `None` (not a population-average
  guess) when `body_fat_percent` is unknown, to avoid silently
  injecting an unstated assumption into downstream models.
- **`diet.py`** — `MacronutrientGrams` (grams → energy via Atwater
  factors) and `DietPlan` (a named/labeled prescribed intake).
- **`simulation_state.py`** — `SimulationState`: one timestep's
  snapshot of a simulation run. Includes a cross-field validator
  ensuring `fat_mass_kg + lean_mass_kg ≈ weight_kg` (0.05 kg tolerance)
  whenever both are populated, to catch composition/weight drift bugs
  early in later phases.

## Design decisions

1. **`extra="forbid"` on every model.** Chosen over the default
   `"ignore"` specifically to catch typos and unit-name mistakes at
   construction time (e.g. `weight=80` instead of `weight_kg=80` should
   fail loudly, not silently populate nothing). Trade-off: this means
   `model_dump()` output (which includes computed fields) cannot be
   fed straight back into `model_validate_json()`, since computed
   fields aren't settable inputs. Tests demonstrate the correct
   round-trip pattern: dump/validate through `model_fields.keys()`
   only. This is documented inline in both the model docstrings and
   the affected tests.
2. **No unreachable "defensive" validators.** An initial draft of
   `Person` included a cross-field check for "fat mass exceeding total
   weight" and `DietPlan` included a fiber/carbohydrate sanity check —
   both were mathematically unreachable given the field-level bounds
   already in place, confirmed by 100% branch coverage flagging them as
   dead code. Removed rather than kept as decorative-but-useless code.
3. **`fat_mass_kg`/`lean_mass_kg` are `None`, not defaulted**, when
   `body_fat_percent` is unknown on `Person`. Guessing a population
   average silently would look like real data to every downstream
   model.
4. **`SimulationConfig` deliberately NOT built this phase.** The
   original folder structure anticipated a `simulation/config.py`, but
   that object would need to reference model registry string IDs
   (e.g. `"mifflin_st_jeor"`) that don't exist until `models.bmr`
   (Phase 4) is built. Building it now would either be an empty
   placeholder with no real fields, or would create a forward
   dependency from `domain`/`simulation` onto not-yet-existing
   registries. Deferred to whichever phase first needs to select
   between concrete model strategies (likely Phase 5, TDEE engine).

## Testing

- 54 unit tests across 5 test files, one per domain module, mirroring
  `tests/unit/domain/`.
- 100% statement coverage on `metabosim.domain` (verified via
  `pytest --cov`).
- `mypy --strict` passes with zero issues.
- `black --check` and `ruff check` both pass with zero issues.

## Verification commands

```bash
pip install -e ".[dev]"
pytest tests/unit/domain --cov=metabosim.domain --cov-report=term-missing
mypy --strict src/metabosim/domain
black --check src/metabosim/domain tests/unit/domain
ruff check src/metabosim/domain tests/unit/domain
```

## Not yet done (future phases)

- No BMR/TDEE/activity model implementations (Phase 4+) — `Person` and
  `SimulationState` are the data shapes those models will consume and
  produce, respectively.
- `SimulationConfig` (deferred, see above).
- No GUI/CLI input parsing using `metabosim.domain.units` yet
  (Phase 18 / GUI is optional and out of current scope).
