"""
metabosim.models.adaptive_thermogenesis.registry
====================================================

Registry mapping string identifiers to Adaptive Thermogenesis model
classes, mirroring the registries in every other model family in this
project.
"""

from __future__ import annotations

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.none import NoAdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.proportional import (
    ProportionalAdaptiveThermogenesisModel,
)
from metabosim.models.adaptive_thermogenesis.threshold import (
    ThresholdAdaptiveThermogenesisModel,
)

#: Maps a stable string ID -> concrete Adaptive Thermogenesis model
#: class. IDs are snake_case and, once published, should be treated
#: as a stable public API.
_REGISTRY: dict[str, type[AdaptiveThermogenesisModel]] = {
    "none": NoAdaptiveThermogenesisModel,
    "threshold": ThresholdAdaptiveThermogenesisModel,
    "proportional": ProportionalAdaptiveThermogenesisModel,
}


def list_models() -> list[str]:
    """Return the sorted list of registered Adaptive Thermogenesis
    model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> AdaptiveThermogenesisModel:
    """Instantiate and return the Adaptive Thermogenesis model
    registered under ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"none"``, ``"threshold"``, or
        ``"proportional"``. See ``list_models()`` for all currently
        registered IDs.

    Returns
    -------
    AdaptiveThermogenesisModel
        A fresh instance of the requested model, constructed with its
        default parameters.

    Raises
    ------
    KeyError
        If ``model_id`` is not registered. The error message lists the
        currently valid IDs to aid debugging.
    """
    try:
        model_cls = _REGISTRY[model_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown Adaptive Thermogenesis model id {model_id!r}. "
            f"Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[AdaptiveThermogenesisModel]) -> None:
    """Register (or overwrite) an Adaptive Thermogenesis model under
    ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
