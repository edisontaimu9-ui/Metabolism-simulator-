"""
metabosim.models.disease.registry
=====================================

Registry mapping string identifiers to Disease Modifier classes.

Like ``metabosim.models.activity.registry`` (and for the same reason),
this registry's ``get_model`` accepts ``**kwargs`` forwarded to the
model constructor, rather than following the simpler zero-argument
pattern used by ``bmr``/``tdee``/``tef``/``energy_balance``/
``body_composition``/``adaptive_thermogenesis``: disease modifiers are
parameterized by clinical data at construction time (a
``ThyroidStatus`` category, a body temperature in Celsius), not
supplied per-call like ``Person``.
"""

from __future__ import annotations

from typing import Any

from metabosim.models.disease.base import DiseaseModifier
from metabosim.models.disease.body_temperature import BodyTemperatureModifier
from metabosim.models.disease.thyroid import ThyroidModifier

#: Maps a stable string ID -> concrete Disease Modifier class. IDs are
#: snake_case and, once published, should be treated as a stable
#: public API.
_REGISTRY: dict[str, type[DiseaseModifier]] = {
    "thyroid": ThyroidModifier,
    "body_temperature": BodyTemperatureModifier,
}


def list_models() -> list[str]:
    """Return the sorted list of registered Disease Modifier IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str, **kwargs: Any) -> DiseaseModifier:
    """Instantiate and return the Disease Modifier registered under
    ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"thyroid"`` or ``"body_temperature"``. See
        ``list_models()`` for all currently registered IDs.
    **kwargs:
        Forwarded to the model class's constructor. ``"thyroid"``
        accepts ``status=ThyroidStatus.MODERATE_HYPOTHYROID`` (or
        similar); ``"body_temperature"`` requires
        ``body_temperature_c=<float>``.

    Returns
    -------
    DiseaseModifier
        A fresh instance of the requested modifier.

    Raises
    ------
    KeyError
        If ``model_id`` is not registered.
    TypeError
        If required constructor arguments were not supplied.
    ValueError
        If supplied constructor arguments are out of the model's
        valid range.
    """
    try:
        model_cls = _REGISTRY[model_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown Disease Modifier id {model_id!r}. Available: {list_models()}"
        ) from exc
    return model_cls(**kwargs)


def register_model(model_id: str, model_cls: type[DiseaseModifier]) -> None:
    """Register (or overwrite) a Disease Modifier under ``model_id``.

    Exists to support experimental modifiers being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
