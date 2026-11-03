# Phase 17: Validation Against Published Literature

**Status:** Complete as a framework, with one plausibility check. No
digitized empirical curve is bundled yet (see "Not done").

## What was built

**`metabosim.validation`**

- **`metrics.py`**: `rmse`, `mean_bias`, `max_abs_error`.
- **`reference.py`**: `ReferenceCurve` (a digitized published weight
  curve; citation and extraction note are mandatory fields),
  `load_curve`, `compare_curve` (RMSE against a stated tolerance),
  `check_value`, and `ValidationResult`.
- **`yoo2018.py`**: `run_yoo_2018_check()`, a plausibility check against
  the worked example in Yoo (2018): a 100 kg sedentary male at a
  sustained 500 kcal/day deficit approaches about 75 kg.
- **`datasets/README.md`**: the JSON format and the rule that only data
  from a real source belongs there.
- **`tests/validation/`**: tests carrying the existing
  `@pytest.mark.validation` marker (`pytest -m validation`).

## What the Yoo check does and does not show

The source gives starting weight, sex, activity category, and the
deficit. The simulator also needs age, height, and activity energy, which
the source does not give, so the check assumes them (40 y, 175 cm, 3 MET
for 4 h/day, maintenance about 2900 kcal/day). With those assumptions the
simulator settles at about 72.6 kg, inside the plus or minus 5 kg band
around 75 kg, and the trajectory plateaus.

This is a plausibility check, not a precise fit. It would catch a badly
wrong feedback model (no plateau, or a plateau far away), not small
differences. The result also depends on the assumed inputs:

- With **no logged activity**, the same deficit drives the simulator to
  roughly 55 kg after ten years, because the simulator's only
  weight-dependent expenditure terms are then BMR and thermic effect of
  food. Activity energy is a large weight-proportional term, so the
  logged-activity assumption matters. This is worth knowing when using
  the simulator for long runs with an empty activity list.
- Other plausible activity assumptions gave 73.6 to 74.5 kg in probing.

## Design decisions

1. **Loose tolerance, stated openly.** The band reflects genuinely
   unspecified inputs. Tightening it would only fit the assumptions.
2. **No fabricated datasets.** `ReferenceCurve` refuses an empty
   citation or extraction note, and the datasets folder documents that
   values must come from a real table or a named digitization method.
   The Minnesota Starvation Experiment (Keys, 1950) is the obvious next
   candidate, but its values have not been extracted, so it is not
   included.
3. **A curve-comparison path exists and is tested with synthetic
   fixtures** (clearly labeled as such), so adding a real dataset later
   needs a JSON file and a tolerance, not new code.

## Not done

- No empirical curve is bundled. The next step is digitizing a real one
  (Minnesota or a published weight-loss trial) with a documented
  extraction method, then choosing a tolerance from its measurement
  uncertainty.
- Validation is not yet wired into the Phase 16 reports.
- Adaptive thermogenesis, which the references call contested, has no
  validation check yet.

## Testing

- Unit tests in `tests/unit/validation/`, 100% coverage of
  `metabosim.validation`.
- `tests/validation/test_yoo_2018.py` runs the full ten-year check.

## Verification commands

```bash
pytest tests/unit/validation --cov=metabosim.validation --cov-report=term-missing
pytest -m validation
metabosim validate
```
