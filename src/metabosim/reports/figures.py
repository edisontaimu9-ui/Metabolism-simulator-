"""
metabosim.reports.figures
============================

Renders the ``metabosim.visualization`` plots for one run to in-memory
PNG bytes, for embedding in a report.

Figures are drawn on ``matplotlib.figure.Figure`` objects created
directly (not via ``pyplot``), so rendering needs no display, touches
no global pyplot state, and leaks no figures. The plotting functions
are reused unchanged through their ``ax`` argument; nothing here
re-implements any plotting.
"""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from metabosim.reports.data import ReportData
from metabosim.reports.document import FigureBlock
from metabosim.visualization import (
    plot_bmr_model_comparison,
    plot_body_composition_trajectory,
    plot_energy_balance,
    plot_energy_intake_vs_expenditure,
    plot_glycogen_trajectory,
    plot_weight_trajectory,
)

_FIGURE_SIZE_INCHES: tuple[float, float] = (7.0, 3.8)
_DPI: int = 110


def _render_png(draw: Callable[[Axes], object]) -> bytes:
    """Draw onto a fresh ``Figure`` and return it as PNG bytes."""
    fig = Figure(figsize=_FIGURE_SIZE_INCHES, dpi=_DPI)
    ax = fig.subplots()
    draw(ax)
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    return buffer.getvalue()


def render_figures(data: ReportData) -> list[FigureBlock]:
    """Render every figure that applies to this run.

    Always included: weight trajectory, energy intake vs. expenditure,
    daily energy balance, and the BMR model comparison for the
    subject's starting profile. Body composition and glycogen figures
    are included only if that tracking was active.
    """
    states = data.states
    figures: list[FigureBlock] = [
        FigureBlock(
            key="weight",
            caption="Body weight over the simulated period.",
            png=_render_png(lambda ax: plot_weight_trajectory(states, ax=ax)),
        ),
        FigureBlock(
            key="energy",
            caption="Daily energy intake versus expenditure.",
            png=_render_png(
                lambda ax: plot_energy_intake_vs_expenditure(states, ax=ax)
            ),
        ),
        FigureBlock(
            key="balance",
            caption="Daily energy balance (intake minus expenditure).",
            png=_render_png(lambda ax: plot_energy_balance(states, ax=ax)),
        ),
    ]
    if data.summary.tracked_body_composition:
        figures.append(
            FigureBlock(
                key="composition",
                caption="Fat mass and lean mass over the simulated period.",
                png=_render_png(
                    lambda ax: plot_body_composition_trajectory(states, ax=ax)
                ),
            )
        )
    if data.summary.tracked_glycogen:
        figures.append(
            FigureBlock(
                key="glycogen",
                caption="Body glycogen store over the simulated period.",
                png=_render_png(lambda ax: plot_glycogen_trajectory(states, ax=ax)),
            )
        )
    figures.append(
        FigureBlock(
            key="bmr-comparison",
            caption=(
                "Resting energy expenditure estimates from every available "
                "BMR equation, for the subject's starting profile. "
                "Equations that need body fat percentage are omitted when "
                "it was not provided."
            ),
            png=_render_png(lambda ax: plot_bmr_model_comparison(data.person, ax=ax)),
        )
    )
    return figures
