"""
metabosim.visualization
===========================

Matplotlib plotting of simulation time series and model comparisons.
Consumes ``metabosim.simulation`` output (via ``metabosim.analysis``)
and ``metabosim.models.*`` outputs directly; produces figures only --
no scientific modeling or calculation logic lives here, per
``docs/architecture.md``.

  - ``trajectory``  -- ``plot_weight_trajectory``,
    ``plot_body_composition_trajectory``, ``plot_glycogen_trajectory``.
  - ``energy``       -- ``plot_energy_intake_vs_expenditure``,
    ``plot_energy_balance`` (with optional moving-average overlay).
  - ``comparison``   -- ``plot_organ_bmr_breakdown`` (Phase 13),
    ``plot_bmr_model_comparison`` (every registered BMR equation for
    one subject, side by side).

Every function follows the same ``ax: Axes | None = None`` signature
convention: pass an existing ``Axes`` to compose multiple plots into
one figure (e.g. via ``matplotlib.pyplot.subplots``), or omit it to
get a fresh figure. No function calls ``plt.show()`` -- callers save,
display, or embed the returned axes' figure themselves. See
``metabosim.visualization.trajectory`` module docstring for the full
convention.

Example
-------
>>> import matplotlib
>>> matplotlib.use("Agg")  # headless backend, no display required
>>> from metabosim.domain import MacronutrientGrams, Person, Sex
>>> from metabosim.simulation import DailyPlan, SimulationConfig, Simulator
>>> from metabosim.visualization import plot_weight_trajectory
>>> person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
>>> macros = MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
>>> plan = DailyPlan(macros=macros)
>>> states = Simulator(person, SimulationConfig(days=10), plan).run()
>>> ax = plot_weight_trajectory(states)
>>> ax.get_title()
'Body Weight Over Time'
"""

from metabosim.visualization.comparison import (
    plot_bmr_model_comparison,
    plot_organ_bmr_breakdown,
)
from metabosim.visualization.energy import (
    plot_energy_balance,
    plot_energy_intake_vs_expenditure,
)
from metabosim.visualization.trajectory import (
    plot_body_composition_trajectory,
    plot_glycogen_trajectory,
    plot_weight_trajectory,
)

__all__ = [
    "plot_bmr_model_comparison",
    "plot_body_composition_trajectory",
    "plot_energy_balance",
    "plot_energy_intake_vs_expenditure",
    "plot_glycogen_trajectory",
    "plot_organ_bmr_breakdown",
    "plot_weight_trajectory",
]
