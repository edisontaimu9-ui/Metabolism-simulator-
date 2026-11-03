"""
metabosim.models.tdee.registry
=================================

Registry mapping string identifiers to TDEE model classes, mirroring
``metabosim.models.bmr.registry``. Lets a caller select a TDEE
strategy at runtime by name (e.g. ``"pal_multiplier"``).
"""

from __future__ import annotations

from metabosim.models.tdee.base import TDEEModel
from metabosim.models.tdee.pal_multiplier import PALMultiplierTDEE

#: Maps a stable string ID -> concrete TDEE model class. IDs are
#: snake_case and, once published, should be treated as a stable
#: public API.
_REGISTRY: dict[str, type[TDEEModel]] = {
    "pal_multiplier": PALMultiplierTDEE,
}


def list_models() -> list[str]:
    """Return the sorted list of registered TDEE model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> TDEEModel:
    """Instantiate and return the TDEE model registered under
    ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"pal_multiplier"``. See ``list_models()`` for
        all currently registered IDs.

    Returns
    -------
    TDEEModel
        A fresh instance of the requested model.

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
            f"Unknown TDEE model id {model_id!r}. Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[TDEEModel]) -> None:
    """Register (or overwrite) a TDEE model under ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
