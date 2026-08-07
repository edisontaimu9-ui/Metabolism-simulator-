"""
metabosim.models.activity.registry
=====================================

Registry mapping string identifiers to Activity model classes.

Design note -- why this registry's ``get_model`` differs from
``metabosim.models.bmr.registry`` / ``models.tdee.registry`` /
``models.tef.registry``:
    Every other model family in this project is stateless and
    zero-argument-constructible (``model_cls()``); all calculation
    inputs arrive via ``calculate()``. ``METBasedActivityModel`` breaks
    that pattern -- it needs a logged list of ``ActivityEntry`` objects
    at construction time, since a MET-based activity log is properly
    the *strategy's* data (which activities happened), not a per-call
    argument like ``Person`` or ``bmr_kcal``. This registry's
    ``get_model`` therefore accepts ``**kwargs`` and forwards them to
    the model's constructor, e.g.
    ``get_model("met_based", entries=[...])`` vs.
    ``get_model("iom_pal")``.
"""

from __future__ import annotations

from typing import Any

from metabosim.models.activity.base import ActivityModel
from metabosim.models.activity.iom_pal import IOMPALActivityModel
from metabosim.models.activity.met_based import METBasedActivityModel

#: Maps a stable string ID -> concrete Activity model class. IDs are
#: snake_case and, once published, should be treated as a stable
#: public API.
_REGISTRY: dict[str, type[ActivityModel]] = {
    "met_based": METBasedActivityModel,
    "iom_pal": IOMPALActivityModel,
}


def list_models() -> list[str]:
    """Return the sorted list of registered Activity model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str, **kwargs: Any) -> ActivityModel:
    """Instantiate and return the Activity model registered under
    ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"met_based"`` or ``"iom_pal"``. See
        ``list_models()`` for all currently registered IDs.
    **kwargs:
        Forwarded to the model class's constructor. ``"met_based"``
        requires ``entries=[...]`` (a list of
        ``metabosim.models.activity.met_based.ActivityEntry``);
        ``"iom_pal"`` takes no constructor arguments.

    Returns
    -------
    ActivityModel
        A fresh instance of the requested model.

    Raises
    ------
    KeyError
        If ``model_id`` is not registered.
    TypeError
        If the required constructor arguments for the requested model
        were not supplied (e.g. calling
        ``get_model("met_based")`` without ``entries``).
    """
    try:
        model_cls = _REGISTRY[model_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown Activity model id {model_id!r}. " f"Available: {list_models()}"
        ) from exc
    return model_cls(**kwargs)


def register_model(model_id: str, model_cls: type[ActivityModel]) -> None:
    """Register (or overwrite) an Activity model under ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
