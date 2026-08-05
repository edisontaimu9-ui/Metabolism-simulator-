# Phase 1 — Project Planning & Architecture

**Status:** Complete

## Decisions made

1. **Architecture style:** layered, strategy-pattern, plugin-based —
   chosen because nutrition science has multiple co-existing, competing
   equations (e.g. Mifflin-St Jeor vs Harris-Benedict) that must remain
   swappable at runtime, and because the simulation is inherently
   time-stepped/stateful while individual model calculations are
   stateless.
2. **Pydantic for domain models** — chosen specifically to prevent unit
   and range errors, which are a common and dangerous class of bug in
   biomedical software (e.g. kg vs lb, kcal vs kJ, age in months vs
   years for pediatric edge cases).
3. **`src/` layout** — modern packaging convention, prevents accidental
   import of uninstalled code during development.
4. **Strict forward data flow** — domain -> models -> simulation ->
   analysis/visualization/reports. No downstream layer is ever mutated
   by an upstream one; this makes the eventual Phase 17 validation work
   tractable because models can be swapped without touching the engine.
5. **Testing split**: unit tests (exact/golden values) vs validation
   tests (tolerance-band comparison against literature) are intentionally
   kept in separate directories (`tests/unit` vs `tests/validation`)
   since they have different pass/fail semantics.

## Deferred to later phases

- No implementation code written (per instructions).
- GUI (PyQt) is optional and deferred indefinitely; architecture keeps
  it decoupled via the `visualization`/`simulation` boundary so it can
  be added without touching core logic.

## Open questions for future phases

- Exact numerical integration approach for `simulation/stepper.py`
  (fixed daily timestep vs adaptive ODE solver via SciPy) — to be
  decided in Phase 8 (Energy Balance Engine) based on the Hall et al.
  dynamic model's mathematical form.
