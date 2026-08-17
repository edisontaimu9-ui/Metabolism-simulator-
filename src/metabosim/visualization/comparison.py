"""
metabosim.visualization.comparison
======================================

Matplotlib plotting for cross-model comparisons: the Phase 13 organ
BMR breakdown, and a side-by-side comparison of every registered BMR
equation's estimate for a given subject. See
``metabosim.visualization.trajectory`` module docstring for the
shared ``ax=None`` composability convention used throughout this
package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from metabosim.domain.person import Person
from metabosim.models.bmr.registry import get_model, list_models
from metabosim.models.organ.elia import OrganBMRBreakdown

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def plot_organ_bmr_breakdown(
    breakdown: OrganBMRBreakdown,
    ax: Axes | None = None,
) -> Axes:
    """Plot a horizontal bar chart of an organ-level BMR breakdown
    (see ``metabosim.models.organ.elia``), one bar per organ/tissue,
    ordered from largest to smallest contribution.

    Parameters
    ----------
    breakdown:
        The result of
        ``metabosim.models.organ.elia.calculate_organ_bmr_breakdown_kcal``.
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.

    Returns
    -------
    Axes
        The axes the chart was drawn on.
    """
    if ax is None:
        _, ax = plt.subplots()

    components = [
        ("Brain", breakdown.brain_kcal),
        ("Liver", breakdown.liver_kcal),
        ("Heart", breakdown.heart_kcal),
        ("Kidneys", breakdown.kidneys_kcal),
        ("Residual lean", breakdown.residual_lean_kcal),
        ("Adipose", breakdown.adipose_kcal),
    ]
    components.sort(key=lambda pair: pair[1], reverse=True)
    labels = [pair[0] for pair in components]
    values = [pair[1] for pair in components]

    ax.barh(labels, values, color="tab:blue")
    ax.invert_yaxis()  # largest contribution at the top
    ax.set_xlabel("Contribution to BMR (kcal/day)")
    ax.set_title(f"Organ BMR Breakdown (Total: {breakdown.total_kcal:.0f} kcal/day)")
    return ax


def plot_bmr_model_comparison(
    person: Person,
    ax: Axes | None = None,
) -> Axes:
    """Plot a horizontal bar chart comparing every registered BMR
    model's estimate for ``person``, ordered from highest to lowest.

    Models that require ``person.body_fat_percent`` (Katch-McArdle,
    Cunningham, Elia organ-based) are silently skipped if it isn't
    set, rather than raising -- this is a comparison/showcase view,
    not a strict computation, so partial results are more useful than
    an outright failure.

    Parameters
    ----------
    person:
        The subject to compute and compare every registered BMR
        model's estimate for.
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.

    Returns
    -------
    Axes
        The axes the chart was drawn on.

    Raises
    ------
    ValueError
        If no registered BMR model could be evaluated for ``person``
        (e.g. an empty registry, which should not occur in practice).
    """
    if ax is None:
        _, ax = plt.subplots()

    results: list[tuple[str, float]] = []
    for model_id in list_models():
        model = get_model(model_id)
        try:
            bmr_kcal = model.calculate(person)
        except ValueError:
            continue  # requires body_fat_percent, which isn't set
        results.append((model.name, bmr_kcal))

    if not results:
        raise ValueError(
            "No registered BMR model could be evaluated for this person -- "
            "this should not happen with the built-in registry unless it "
            "has been modified."
        )

    results.sort(key=lambda pair: pair[1], reverse=True)
    labels = [pair[0] for pair in results]
    values = [pair[1] for pair in results]

    ax.barh(labels, values, color="tab:orange")
    ax.invert_yaxis()
    ax.set_xlabel("BMR (kcal/day)")
    ax.set_title("BMR Model Comparison")
    return ax
