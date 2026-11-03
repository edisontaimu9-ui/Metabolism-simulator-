"""
metabosim.cli.main
=====================

Command-line interface, installed as the ``metabosim`` command (and
runnable as ``python -m metabosim``). Built on the standard library
only, so it adds no dependency.

Commands
---------------------------------------------------------------------
``models``
    List the registered model IDs for each selectable component.
``simulate``
    Run a simulation for one subject and a constant daily plan, print a
    short summary, and optionally write Markdown and/or HTML reports.
``validate``
    Run the built-in validation checks and print each result. Exits
    with status 1 if any check fails.

``app`` returns the process exit status (0 on success, 2 for invalid
arguments, 1 for a failed validation), so it works both as a console
script entry point and as a plain function in tests.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from metabosim import __version__
from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.models.adaptive_thermogenesis import registry as adaptive_registry
from metabosim.models.bmr import registry as bmr_registry
from metabosim.models.body_composition import registry as body_registry
from metabosim.models.energy_balance import registry as balance_registry
from metabosim.models.tef import registry as tef_registry
from metabosim.reports import (
    build_report_data,
    save_html_report,
    save_markdown_report,
)
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator
from metabosim.validation import run_yoo_2018_check

_MODEL_REGISTRIES = {
    "bmr": bmr_registry,
    "tef": tef_registry,
    "energy-balance": balance_registry,
    "body-composition": body_registry,
    "adaptive-thermogenesis": adaptive_registry,
}


def _parse_activity(text: str) -> ActivityEntry:
    """Parse ``MET:HOURS`` (for example ``6:1.5``) into an entry."""
    try:
        met_text, hours_text = text.split(":")
        return ActivityEntry(met=float(met_text), duration_hours=float(hours_text))
    except (ValueError, ValidationError) as exc:
        raise argparse.ArgumentTypeError(
            f"activity must look like MET:HOURS with positive numbers, got {text!r}"
        ) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metabosim",
        description="Human metabolism and energy expenditure simulation engine.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("models", help="list registered model IDs")
    sub.add_parser("validate", help="run the built-in validation checks")

    sim = sub.add_parser("simulate", help="simulate one subject and write reports")
    sim.add_argument("--sex", required=True, choices=[s.value for s in Sex])
    sim.add_argument("--age", required=True, type=float, help="years")
    sim.add_argument("--height", required=True, type=float, help="cm")
    sim.add_argument("--weight", required=True, type=float, help="kg")
    sim.add_argument("--body-fat", type=float, help="percent; enables body composition")
    sim.add_argument("--name", help="optional subject name for the report")
    sim.add_argument("--protein", required=True, type=float, help="g/day")
    sim.add_argument("--carbs", required=True, type=float, help="g/day")
    sim.add_argument("--fat", required=True, type=float, help="g/day")
    sim.add_argument("--fiber", type=float, default=0.0, help="g/day")
    sim.add_argument("--alcohol", type=float, default=0.0, help="g/day")
    sim.add_argument(
        "--activity",
        action="append",
        type=_parse_activity,
        default=[],
        metavar="MET:HOURS",
        help="logged daily activity; repeat for several entries",
    )
    sim.add_argument("--days", required=True, type=int)
    sim.add_argument("--bmr", help="BMR model ID (see 'models')")
    sim.add_argument("--tef", help="TEF model ID")
    sim.add_argument("--energy-balance", help="energy balance model ID")
    sim.add_argument("--adaptive", help="adaptive thermogenesis model ID")
    sim.add_argument("--glycogen", type=float, help="starting glycogen store, g")
    sim.add_argument("--out", type=Path, help="report path without extension")
    sim.add_argument(
        "--format", choices=["md", "html", "both"], default="both", dest="fmt"
    )
    return parser


def _cmd_models() -> int:
    for label, registry in _MODEL_REGISTRIES.items():
        print(f"{label}: {', '.join(registry.list_models())}")
    return 0


def _cmd_validate() -> int:
    results = run_yoo_2018_check()
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"[{status}] {result.name}: observed {result.observed:.2f}, "
            f"expected {result.expected:.2f} (tolerance {result.tolerance}, "
            f"{result.unit})"
        )
    print(
        "Note: the Yoo (2018) check is a plausibility check built on assumed "
        "inputs, not a precise fit."
    )
    return 0 if all(r.passed for r in results) else 1


def _cmd_simulate(args: argparse.Namespace) -> int:
    person = Person(
        name=args.name,
        sex=Sex(args.sex),
        age_years=args.age,
        height_cm=args.height,
        weight_kg=args.weight,
        body_fat_percent=args.body_fat,
    )
    plan = DailyPlan(
        macros=MacronutrientGrams(
            protein_g=args.protein,
            carbohydrate_g=args.carbs,
            fat_g=args.fat,
            fiber_g=args.fiber,
            alcohol_g=args.alcohol,
        ),
        activity_entries=args.activity,
    )
    overrides = {
        key: value
        for key, value in {
            "bmr_model_id": args.bmr,
            "tef_model_id": args.tef,
            "energy_balance_model_id": args.energy_balance,
            "adaptive_thermogenesis_model_id": args.adaptive,
        }.items()
        if value is not None
    }
    config = SimulationConfig(days=args.days, **overrides)
    simulator = Simulator(person, config, plan, initial_glycogen_g=args.glycogen)
    data = build_report_data(simulator, simulator.run())

    s = data.summary
    print(
        f"{s.days_simulated} days: {s.starting_weight_kg:.2f} kg to "
        f"{s.ending_weight_kg:.2f} kg ({s.total_weight_change_kg:+.2f} kg), "
        f"average energy balance {s.average_daily_energy_balance_kcal:+.0f} kcal/day"
    )
    if args.out is not None:
        if args.fmt in ("md", "both"):
            print("Wrote", save_markdown_report(data, args.out.with_suffix(".md")))
        if args.fmt in ("html", "both"):
            print("Wrote", save_html_report(data, args.out.with_suffix(".html")))
    return 0


def app(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return the exit status."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits on --help, --version, errors
        return exc.code if isinstance(exc.code, int) else 2
    try:
        if args.command == "models":
            return _cmd_models()
        if args.command == "validate":
            return _cmd_validate()
        return _cmd_simulate(args)
    except (ValueError, KeyError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
