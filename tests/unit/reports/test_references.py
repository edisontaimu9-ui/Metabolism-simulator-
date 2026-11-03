"""Unit tests for metabosim.reports.references."""

import re
from pathlib import Path
from types import ModuleType

import pytest

from metabosim.models.adaptive_thermogenesis import registry as adaptive_registry
from metabosim.models.bmr import registry as bmr_registry
from metabosim.models.body_composition import registry as body_registry
from metabosim.models.energy_balance import registry as balance_registry
from metabosim.models.tef import registry as tef_registry
from metabosim.reports import references as refs
from metabosim.simulation.config import SimulationConfig

_DOC = Path(__file__).resolve().parents[3] / "docs" / "model_references.md"


def _package_ids(registry: ModuleType) -> set[str]:
    """IDs of models defined inside the metabosim package.

    Other test modules register throwaway dummy models into the global
    registries; those live in test modules and must not be required to
    have citations.
    """
    return {
        model_id
        for model_id in registry.list_models()
        if type(registry.get_model(model_id)).__module__.startswith("metabosim.")
    }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).strip()


@pytest.mark.unit
class TestCoverageOfRegistries:
    """A newly registered model must get citations before it can be
    reported on; these tests fail loudly if one is forgotten."""

    def test_every_bmr_model_has_references(self) -> None:
        assert _package_ids(bmr_registry) <= set(refs.BMR_REFERENCES)

    def test_every_tef_model_has_references(self) -> None:
        assert _package_ids(tef_registry) <= set(refs.TEF_REFERENCES)

    def test_every_energy_balance_model_has_references(self) -> None:
        assert _package_ids(balance_registry) <= set(refs.ENERGY_BALANCE_REFERENCES)

    def test_every_body_composition_model_has_references(self) -> None:
        assert _package_ids(body_registry) <= set(refs.BODY_COMPOSITION_REFERENCES)

    def test_every_adaptive_model_has_references_entry(self) -> None:
        assert _package_ids(adaptive_registry) <= set(
            refs.ADAPTIVE_THERMOGENESIS_REFERENCES
        )

    def test_non_trivial_models_have_at_least_one_citation(self) -> None:
        for table in (
            refs.BMR_REFERENCES,
            refs.TEF_REFERENCES,
            refs.ENERGY_BALANCE_REFERENCES,
            refs.BODY_COMPOSITION_REFERENCES,
        ):
            assert all(len(citations) >= 1 for citations in table.values())


@pytest.mark.unit
@pytest.mark.skipif(not _DOC.exists(), reason="docs/model_references.md not present")
def test_citations_still_appear_in_bibliography() -> None:
    """Guards against drift from docs/model_references.md: the opening
    of every citation here must still be present in that file."""
    doc = _norm(_DOC.read_text(encoding="utf-8"))
    all_citations: set[str] = set(refs.ALWAYS_REFERENCES) | set(
        refs.GLYCOGEN_REFERENCES
    )
    for table in (
        refs.BMR_REFERENCES,
        refs.TEF_REFERENCES,
        refs.ENERGY_BALANCE_REFERENCES,
        refs.BODY_COMPOSITION_REFERENCES,
        refs.ADAPTIVE_THERMOGENESIS_REFERENCES,
    ):
        for citations in table.values():
            all_citations.update(citations)
    for citation in all_citations:
        assert _norm(citation)[:60] in doc, citation[:60]


@pytest.mark.unit
class TestReferencesForRun:
    def test_default_run_cites_selected_models_only(self) -> None:
        result = refs.references_for_run(
            SimulationConfig(days=5),
            tracked_body_composition=False,
            tracked_glycogen=False,
        )
        assert any("Mifflin" in c for c in result)
        assert any("Jequier" in c for c in result)
        assert any("Heymsfield" in c for c in result)
        assert not any("Harris" in c for c in result)
        assert not any("Forbes" in c for c in result)
        assert not any("Chow" in c for c in result)

    def test_always_cited_present(self) -> None:
        result = refs.references_for_run(
            SimulationConfig(days=5),
            tracked_body_composition=False,
            tracked_glycogen=False,
        )
        for citation in refs.ALWAYS_REFERENCES:
            assert citation in result

    def test_body_composition_cited_only_when_tracked(self) -> None:
        config = SimulationConfig(days=5)
        without = refs.references_for_run(
            config, tracked_body_composition=False, tracked_glycogen=False
        )
        with_ = refs.references_for_run(
            config, tracked_body_composition=True, tracked_glycogen=False
        )
        assert not any("Forbes" in c for c in without)
        assert any("Forbes" in c for c in with_)

    def test_glycogen_cited_only_when_tracked(self) -> None:
        config = SimulationConfig(days=5)
        result = refs.references_for_run(
            config, tracked_body_composition=False, tracked_glycogen=True
        )
        assert any("Chow" in c for c in result)

    def test_adaptive_none_adds_no_citation(self) -> None:
        base = refs.references_for_run(
            SimulationConfig(days=5),
            tracked_body_composition=False,
            tracked_glycogen=False,
        )
        proportional = refs.references_for_run(
            SimulationConfig(days=5, adaptive_thermogenesis_model_id="proportional"),
            tracked_body_composition=False,
            tracked_glycogen=False,
        )
        assert not any("Fothergill" in c for c in base)
        assert any("Fothergill" in c for c in proportional)

    def test_no_duplicates(self) -> None:
        result = refs.references_for_run(
            SimulationConfig(days=5, adaptive_thermogenesis_model_id="threshold"),
            tracked_body_composition=True,
            tracked_glycogen=True,
        )
        assert len(result) == len(set(result))
