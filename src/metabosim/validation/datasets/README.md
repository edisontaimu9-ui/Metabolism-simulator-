# Validation datasets

Only data digitized from a real published source belongs here. Each
dataset is one JSON file matching `ReferenceCurve`
(`metabosim.validation.reference`):

```json
{
  "id": "short_identifier",
  "description": "What the curve shows and under which conditions.",
  "citation": "Full citation of the source.",
  "extraction_note": "How values were obtained (table copied, figure digitized with <tool>), and known uncertainty.",
  "days": [0, 30, 60],
  "weight_kg": [70.0, 66.5, 63.1]
}
```

`days` must be strictly increasing; `weight_kg` must have the same length.
Never add values from memory or estimated by eye without saying so in
`extraction_note`. Load with `load_curve(path)` and compare with
`compare_curve(states, curve, tolerance_rmse_kg)`.

Candidate source already in `docs/model_references.md`: Keys A, et al.
*The Biology of Human Starvation* (1950), the Minnesota Starvation
Experiment. It is not bundled because its values have not yet been
digitized from the original tables.
