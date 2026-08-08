"""
metabosim.models.body_composition.registry
==============================================

Registry mapping string identifiers to Body Composition model classes,
mirroring the registries in ``metabosim.models.bmr`` /
``metabosim.models.tdee`` / ``metabosim.models.tef`` /
``metabosim.models.energy_balance``.
"""

from __future__ import annotations

from metabosim.models.body_composition.base import BodyCompositionModel
from metabosim.models.body_composition.forbes import ForbesPartitionModel

#: Maps a stable string ID -> concrete Body Composition model class.
#: IDs are snake_case and, once published, should be treated as a
#: stable public API.
_REGISTRY: dict[str, type[BodyCompositionModel]] = {
    "forbes": ForbesPartitionModel,
}


def list_models() -> list[str]:
    """Return the sorted list of registered Body Composition model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> BodyCompositionModel:
    """Instantiate and return the Body Composition model registered
    under ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"forbes"``. See ``list_models()`` for all
        currently registered IDs.

    Returns
    -------
    BodyCompositionModel
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
            f"Unknown Body Composition model id {model_id!r}. "
            f"Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[BodyCompositionModel]) -> None:
    """Register (or overwrite) a Body Composition model under
    ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
