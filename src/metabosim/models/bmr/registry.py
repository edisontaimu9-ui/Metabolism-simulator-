"""
metabosim.models.bmr.registry
================================

Registry mapping string identifiers to BMR model classes.

This is what lets a caller -- a config file, a CLI flag, or (from
Phase 5 onward) ``metabosim.models.tdee`` -- select a BMR equation at
runtime by name, e.g. ``"mifflin_st_jeor"``, without importing any
concrete model class directly. This is the mechanism that makes BMR
equations genuinely interchangeable rather than merely
polymorphic-in-theory.
"""

from __future__ import annotations

from metabosim.models.bmr.base import BMRModel
from metabosim.models.bmr.cunningham import CunninghamBMR
from metabosim.models.bmr.harris_benedict import HarrisBenedictBMR
from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR
from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR

#: Maps a stable string ID -> concrete BMR model class. IDs are
#: snake_case and, once published, should be treated as a stable
#: public API -- renaming an ID is a breaking change for any saved
#: ``SimulationConfig`` (Phase 5+) that references it by name.
_REGISTRY: dict[str, type[BMRModel]] = {
    "mifflin_st_jeor": MifflinStJeorBMR,
    "harris_benedict": HarrisBenedictBMR,
    "katch_mcardle": KatchMcArdleBMR,
    "cunningham": CunninghamBMR,
}


def list_models() -> list[str]:
    """Return the sorted list of registered BMR model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> BMRModel:
    """Instantiate and return the BMR model registered under
    ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"mifflin_st_jeor"``. See ``list_models()`` for
        all currently registered IDs.

    Returns
    -------
    BMRModel
        A fresh instance of the requested model. Every current
        ``BMRModel`` subclass is stateless (all state relevant to a
        calculation lives on the ``Person`` passed to ``calculate``),
        so a new instance per call is cheap and avoids any risk of
        shared mutable state between callers.

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
            f"Unknown BMR model id {model_id!r}. Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[BMRModel]) -> None:
    """Register (or overwrite) a BMR model under ``model_id``.

    Exists to support experimental or third-party models being added
    without modifying this module -- e.g. from a research notebook in
    ``examples/notebooks`` -- without requiring a code change here.

    Parameters
    ----------
    model_id:
        The string key future ``get_model()`` calls will use.
    model_cls:
        A concrete ``BMRModel`` subclass (not an instance).
    """
    _REGISTRY[model_id] = model_cls
