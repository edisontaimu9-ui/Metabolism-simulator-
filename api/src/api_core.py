"""Pure request handling for the metabosim API (no Cloudflare imports)."""
from __future__ import annotations

from pydantic import ValidationError

from metabosim.analysis.summary import summarize
from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator

MAX_DAYS = 730


def simulate(body: dict) -> dict:
    p = body["person"]
    m = body["macros"]
    days = int(body["days"])
    if not 1 <= days <= MAX_DAYS:
        raise ValueError(f"days must be between 1 and {MAX_DAYS}")

    person = Person(
        name=p.get("name"),
        sex=Sex(p["sex"]),
        age_years=p["age_years"],
        height_cm=p["height_cm"],
        weight_kg=p["weight_kg"],
        body_fat_percent=p.get("body_fat_percent"),
    )
    plan = DailyPlan(
        macros=MacronutrientGrams(
            protein_g=m["protein_g"],
            carbohydrate_g=m["carbohydrate_g"],
            fat_g=m["fat_g"],
            fiber_g=m.get("fiber_g", 0.0),
            alcohol_g=m.get("alcohol_g", 0.0),
        ),
        activity_entries=[
            ActivityEntry(met=a["met"], duration_hours=a["hours"])
            for a in body.get("activities", [])
        ],
    )
    overrides = {
        k: body[j]
        for k, j in {
            "bmr_model_id": "bmr",
            "tef_model_id": "tef",
            "energy_balance_model_id": "energy_balance",
            "adaptive_thermogenesis_model_id": "adaptive",
        }.items()
        if body.get(j)
    }
    sim = Simulator(
        person,
        SimulationConfig(days=days, **overrides),
        plan,
        initial_glycogen_g=body.get("glycogen_g"),
    )
    states = sim.run()
    return {
        "summary": summarize(states).model_dump(mode="json"),
        "weight_kg": [round(s.weight_kg, 3) for s in states],
    }


def handle(method: str, path: str, body: dict | None) -> tuple[int, dict]:
    try:
        if path == "/" and method == "GET":
            return 200, {"service": "metabosim-api", "endpoints": ["POST /simulate"]}
        if path == "/simulate" and method == "POST":
            return 200, simulate(body or {})
        return 404, {"error": "not found"}
    except (KeyError, ValueError, TypeError, ValidationError) as exc:
        return 400, {"error": str(exc)}
