"""
metabosim.models.tef.registry
================================

Registry mapping string identifiers to TEF model classes, mirroring
``metabosim.models.bmr.registry`` and
``metabosim.models.tdee.registry``. Lets a caller select a TEF
strategy at runtime by name (e.g. ``"macronutrient_specific"``).
"""

from __future__ import annotations

from metabosim.models.tef.base import TEFModel
from metabosim.models.tef.fixed_percentage import FixedPercentageTEF
from metabosim.models.tef.macronutrient_specific import MacronutrientSpecificTEF

#: Maps a stable string ID -> concrete TEF model class. IDs are
#: snake_case and, once published, should be treated as a stable
#: public API.
_REGISTRY: dict[str, type[TEFModel]] = {
    "macronutrient_specific": MacronutrientSpecificTEF,
    "fixed_percentage": FixedPercentageTEF,
}


def list_models() -> list[str]:
    """Return the sorted list of registered TEF model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> TEFModel:
    """Instantiate and return the TEF model registered under
    ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"macronutrient_specific"`` or
        ``"fixed_percentage"``. See ``list_models()`` for all
        currently registered IDs.

    Returns
    -------
    TEFModel
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
            f"Unknown TEF model id {model_id!r}. Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[TEFModel]) -> None:
    """Register (or overwrite) a TEF model under ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
