"""
metabosim.reports.document
=============================

A small, format-neutral document model (sections of paragraphs,
bullet lists, tables, and figures) plus ``build_document``, which
turns a ``ReportData`` into one.

Why an intermediate model
---------------------------------------------------------------------
Markdown and HTML reports must say exactly the same thing. Building
the content once as data, then rendering it twice
(``metabosim.reports.render``), means the two formats cannot drift
apart, and the content logic is testable without parsing either
format. All text here is plain text; the renderers escape it.

Contains no scientific modeling; every number shown was computed by an
earlier phase.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from metabosim.models.adaptive_thermogenesis.registry import (
    get_model as get_adaptive_model,
)
from metabosim.models.bmr.registry import get_model as get_bmr_model
from metabosim.models.body_composition.registry import (
    get_model as get_body_composition_model,
)
from metabosim.models.energy_balance.registry import (
    get_model as get_energy_balance_model,
)
from metabosim.models.tef.registry import get_model as get_tef_model
from metabosim.reports.data import ReportData
from metabosim.reports.references import references_for_run

#: Default cap on rows in the daily results table; longer runs are
#: sampled at a regular interval (the last day is always included).
DEFAULT_MAX_DAILY_ROWS: int = 31


@dataclass(frozen=True)
class Paragraph:
    text: str


@dataclass(frozen=True)
class BulletList:
    items: tuple[str, ...]


@dataclass(frozen=True)
class Table:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class FigureBlock:
    """A PNG figure. ``key`` is a short, filename-safe identifier."""

    key: str
    caption: str
    png: bytes


Block = Paragraph | BulletList | Table | FigureBlock


@dataclass(frozen=True)
class Section:
    heading: str
    blocks: tuple[Block, ...]


@dataclass(frozen=True)
class Document:
    title: str
    sections: tuple[Section, ...]


def _f(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def _signed(value: float, digits: int = 1) -> str:
    return f"{value:+.{digits}f}"


def _subject_section(data: ReportData) -> Section:
    person = data.person
    rows: list[tuple[str, str]] = []
    if person.name:
        rows.append(("Name", person.name))
    rows.extend(
        [
            ("Sex", person.sex.value),
            ("Age", f"{_f(person.age_years)} years"),
            ("Height", f"{_f(person.height_cm)} cm"),
            ("Starting weight", f"{_f(person.weight_kg)} kg"),
            ("BMI (screening heuristic only)", _f(person.bmi)),
            (
                "Body fat",
                (
                    f"{_f(person.body_fat_percent)} %"
                    if person.body_fat_percent is not None
                    else "Not provided"
                ),
            ),
            ("Simulated days", str(data.config.days)),
        ]
    )
    if data.config.start_date is not None:
        rows.append(("Start date", data.config.start_date.isoformat()))
    return Section(
        "Subject",
        (Table(("Property", "Value"), tuple(rows)),),
    )


def _models_section(data: ReportData) -> Section:
    config = data.config
    tracked_comp = data.summary.tracked_body_composition
    body_comp_value = (
        f"{get_body_composition_model(config.body_composition_model_id).name} "
        f"({config.body_composition_model_id})"
        if tracked_comp
        else "Not active (body fat percentage was not provided)"
    )
    glycogen_value = (
        f"Tracked (starting store {_f(data.initial_glycogen_g or 0.0, 0)} g)"
        if data.summary.tracked_glycogen
        else "Not tracked"
    )
    rows = (
        (
            "BMR",
            f"{get_bmr_model(config.bmr_model_id).name} ({config.bmr_model_id})",
        ),
        (
            "Thermic effect of food",
            f"{get_tef_model(config.tef_model_id).name} ({config.tef_model_id})",
        ),
        (
            "Energy balance",
            f"{get_energy_balance_model(config.energy_balance_model_id).name} "
            f"({config.energy_balance_model_id})",
        ),
        ("Body composition", body_comp_value),
        (
            "Adaptive thermogenesis",
            f"{get_adaptive_model(config.adaptive_thermogenesis_model_id).name} "
            f"({config.adaptive_thermogenesis_model_id})",
        ),
        ("Physical activity", "MET-based, from the logged daily activity entries"),
        ("Glycogen", glycogen_value),
    )
    return Section("Models used", (Table(("Component", "Model"), rows),))


def _plan_section(data: ReportData) -> Section:
    plans = data.daily_plans
    blocks: list[Block] = []
    if data.plan_is_uniform:
        plan = plans[0]
        macros = plan.macros
        blocks.append(Paragraph("The same plan was applied on every simulated day."))
        blocks.append(
            Table(
                ("Item", "Per day"),
                (
                    ("Energy intake", f"{_f(macros.energy_kcal, 0)} kcal"),
                    ("Protein", f"{_f(macros.protein_g, 0)} g"),
                    ("Carbohydrate", f"{_f(macros.carbohydrate_g, 0)} g"),
                    ("Fat", f"{_f(macros.fat_g, 0)} g"),
                    ("Fiber", f"{_f(macros.fiber_g, 0)} g"),
                    ("Alcohol", f"{_f(macros.alcohol_g, 0)} g"),
                ),
            )
        )
        if plan.activity_entries:
            blocks.append(
                Table(
                    ("Logged activity", "MET", "Hours"),
                    tuple(
                        (
                            entry.label or "Unlabeled",
                            _f(entry.met),
                            _f(entry.duration_hours, 2),
                        )
                        for entry in plan.activity_entries
                    ),
                )
            )
        else:
            blocks.append(Paragraph("No physical activity was logged."))
    else:
        intakes = [plan.macros.energy_kcal for plan in plans]
        blocks.append(
            Paragraph(
                "The plan varied from day to day. Daily energy intake ranged "
                f"from {_f(min(intakes), 0)} to {_f(max(intakes), 0)} kcal "
                f"(mean {_f(sum(intakes) / len(intakes), 0)} kcal). Per-day "
                "intake is shown in the daily results table."
            )
        )
    return Section("Diet and activity", tuple(blocks))


def _results_section(data: ReportData) -> Section:
    s = data.summary
    states = data.states
    rows: list[tuple[str, str]] = [
        ("Days simulated", str(s.days_simulated)),
        ("Starting weight", f"{_f(s.starting_weight_kg, 2)} kg"),
        ("Ending weight", f"{_f(s.ending_weight_kg, 2)} kg"),
        ("Total weight change", f"{_signed(s.total_weight_change_kg, 2)} kg"),
        (
            "Average rate of change",
            f"{_signed(s.average_daily_rate_kg * 7, 2)} kg/week",
        ),
        (
            "Average daily energy balance",
            f"{_signed(s.average_daily_energy_balance_kcal, 0)} kcal/day",
        ),
    ]
    first, last = states[0], states[-1]
    if s.tracked_body_composition:
        assert first.fat_mass_kg is not None and last.fat_mass_kg is not None
        assert first.lean_mass_kg is not None and last.lean_mass_kg is not None
        rows.append(
            (
                "Fat mass",
                f"{_f(first.fat_mass_kg, 2)} to {_f(last.fat_mass_kg, 2)} kg "
                f"({_signed(last.fat_mass_kg - first.fat_mass_kg, 2)} kg)",
            )
        )
        rows.append(
            (
                "Lean mass",
                f"{_f(first.lean_mass_kg, 2)} to {_f(last.lean_mass_kg, 2)} kg "
                f"({_signed(last.lean_mass_kg - first.lean_mass_kg, 2)} kg)",
            )
        )
    if s.tracked_glycogen:
        assert first.glycogen_g is not None and last.glycogen_g is not None
        rows.append(
            (
                "Glycogen",
                f"{_f(first.glycogen_g, 0)} to {_f(last.glycogen_g, 0)} g",
            )
        )
    if first.bmr_kcal is not None and last.bmr_kcal is not None:
        rows.append(
            (
                "BMR (first day to final state)",
                f"{_f(first.bmr_kcal, 0)} to {_f(last.bmr_kcal, 0)} kcal/day",
            )
        )
    if first.tdee_kcal is not None and last.tdee_kcal is not None:
        rows.append(
            (
                "TDEE (first day to final state)",
                f"{_f(first.tdee_kcal, 0)} to {_f(last.tdee_kcal, 0)} kcal/day",
            )
        )
    return Section("Key results", (Table(("Measure", "Value"), tuple(rows)),))


def _daily_rows_indices(n_states: int, max_rows: int) -> list[int]:
    """Indices to show: every state if it fits, else a regular sample
    that always includes the first and last state."""
    if n_states <= max_rows:
        return list(range(n_states))
    step = math.ceil((n_states - 1) / (max_rows - 1))
    indices = list(range(0, n_states, step))
    if indices[-1] != n_states - 1:
        indices.append(n_states - 1)
    return indices


def _daily_section(data: ReportData, max_rows: int) -> Section:
    s = data.summary
    headers = [
        "Day",
        "Weight (kg)",
        "Intake (kcal)",
        "Expenditure (kcal)",
        "Balance (kcal)",
    ]
    if s.tracked_body_composition:
        headers += ["Fat (kg)", "Lean (kg)"]
    if s.tracked_glycogen:
        headers.append("Glycogen (g)")

    indices = _daily_rows_indices(len(data.states), max_rows)
    rows: list[tuple[str, ...]] = []
    for i in indices:
        st = data.states[i]
        row = [
            str(st.day_index),
            _f(st.weight_kg, 2),
            _f(st.energy_intake_kcal, 0),
            _f(st.energy_expenditure_kcal, 0),
            _signed(st.energy_balance_kcal, 0),
        ]
        if s.tracked_body_composition:
            row += [_f(st.fat_mass_kg or 0.0, 2), _f(st.lean_mass_kg or 0.0, 2)]
        if s.tracked_glycogen:
            row.append(_f(st.glycogen_g or 0.0, 0))
        rows.append(tuple(row))

    blocks: list[Block] = []
    if len(indices) < len(data.states):
        blocks.append(
            Paragraph(
                f"Showing {len(indices)} of {len(data.states)} rows, sampled "
                "at a regular interval (first and final states always shown)."
            )
        )
    blocks.append(Table(tuple(headers), tuple(rows)))
    blocks.append(
        Paragraph(
            "Each row's weight is the weight at the start of that day; its "
            "energy figures describe what happens during that day. The final "
            "row is a snapshot of where things stand after the last "
            "simulated day."
        )
    )
    return Section("Daily results", tuple(blocks))


def _limitations_section(data: ReportData) -> Section:
    items = [
        "These are model-based estimates for a hypothetical or simplified "
        "subject, not predictions for any individual and not clinical advice.",
        "Results depend on the chosen models and the plan supplied. Different "
        "published equations disagree with each other, as the BMR comparison "
        "figure shows.",
        "Physical activity energy comes only from the logged activity "
        "entries. Anything not logged is treated as no activity beyond BMR.",
    ]
    if data.config.adaptive_thermogenesis_model_id == "none":
        items.append(
            "No metabolic adaptation beyond the daily BMR recompute was "
            "modeled, because the size and timing of adaptive thermogenesis "
            "are less settled in the literature than other components."
        )
    else:
        items.append(
            "Adaptive thermogenesis was modeled with a documented but "
            "contested set of parameters; treat its effect as uncertain."
        )
    if data.summary.tracked_glycogen:
        items.append(
            "Short-term weight changes in the first days can reflect "
            "glycogen and associated water rather than fat or structural "
            "tissue."
        )
    return Section("Interpretation and limitations", (BulletList(tuple(items)),))


def build_document(
    data: ReportData,
    figures: list[FigureBlock] | None = None,
    max_daily_rows: int = DEFAULT_MAX_DAILY_ROWS,
) -> Document:
    """Build the format-neutral report document.

    Parameters
    ----------
    data:
        The run's ``ReportData``.
    figures:
        Pre-rendered figures (see ``metabosim.reports.figures``), or
        ``None`` / empty to omit the figures section.
    max_daily_rows:
        Cap on rows in the daily results table. Must be >= 2.

    Raises
    ------
    ValueError
        If ``max_daily_rows`` is less than 2.
    """
    if max_daily_rows < 2:
        raise ValueError("max_daily_rows must be at least 2.")

    sections: list[Section] = [
        _subject_section(data),
        _models_section(data),
        _plan_section(data),
        _results_section(data),
    ]
    if figures:
        sections.append(
            Section(
                "Figures",
                tuple(figures),
            )
        )
    sections.append(_daily_section(data, max_daily_rows))
    sections.append(_limitations_section(data))

    citations = references_for_run(
        data.config,
        tracked_body_composition=data.summary.tracked_body_composition,
        tracked_glycogen=data.summary.tracked_glycogen,
    )
    sections.append(Section("References", (BulletList(tuple(citations)),)))
    return Document(title=data.title, sections=tuple(sections))
