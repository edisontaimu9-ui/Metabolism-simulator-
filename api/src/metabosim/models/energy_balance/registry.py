"""
metabosim.models.energy_balance.registry
============================================

Registry mapping string identifiers to Energy Balance model classes,
mirroring ``metabosim.models.bmr.registry`` /
``metabosim.models.tdee.registry`` / ``metabosim.models.tef.registry``.
All three models in this package are zero-argument constructible
(unlike ``metabosim.models.activity.registry``), so this registry
follows the simpler, stateless pattern.
"""

from __future__ import annotations

from metabosim.models.energy_balance.base import EnergyBalanceModel
from metabosim.models.energy_balance.dynamic_quasi_exponential import (
    DynamicQuasiExponentialModel,
)
from metabosim.models.energy_balance.static_rule import StaticEnergyBalanceModel
from metabosim.models.energy_balance.tissue_energy_density import (
    TissueEnergyDensityModel,
)

#: Maps a stable string ID -> concrete Energy Balance model class. IDs
#: are snake_case and, once published, should be treated as a stable
#: public API.
_REGISTRY: dict[str, type[EnergyBalanceModel]] = {
    "static_rule": StaticEnergyBalanceModel,
    "tissue_energy_density": TissueEnergyDensityModel,
    "dynamic_quasi_exponential": DynamicQuasiExponentialModel,
}


def list_models() -> list[str]:
    """Return the sorted list of registered Energy Balance model IDs."""
    return sorted(_REGISTRY.keys())


def get_model(model_id: str) -> EnergyBalanceModel:
    """Instantiate and return the Energy Balance model registered
    under ``model_id``.

    Parameters
    ----------
    model_id:
        A key such as ``"static_rule"``, ``"tissue_energy_density"``,
        or ``"dynamic_quasi_exponential"``. See ``list_models()`` for
        all currently registered IDs.

    Returns
    -------
    EnergyBalanceModel
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
            f"Unknown Energy Balance model id {model_id!r}. "
            f"Available: {list_models()}"
        ) from exc
    return model_cls()


def register_model(model_id: str, model_cls: type[EnergyBalanceModel]) -> None:
    """Register (or overwrite) an Energy Balance model under
    ``model_id``.

    Exists to support experimental models being added without
    modifying this module directly -- see the equivalent function in
    ``metabosim.models.bmr.registry`` for the full rationale.
    """
    _REGISTRY[model_id] = model_cls
