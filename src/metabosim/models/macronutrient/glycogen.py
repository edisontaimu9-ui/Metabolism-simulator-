"""
metabosim.models.macronutrient.glycogen
==========================================

Models short-term glycogen (and its associated water) dynamics: the
transient body-mass fluctuation, on the order of a few days, that
occurs when carbohydrate intake changes -- the well-known "water
weight" effect of starting or stopping a low-carbohydrate diet.

Why this is a mass-balance identity, not a competing hypothesis
(and why there is no registry here, unlike every other model family
in this project)
---------------------------------------------------------------------
Chow CC, Hall KD. "The Dynamics of Human Body Weight Change."
*PLoS Comput Biol.* 2008;4(3):e1000045. Two facts from this paper
ground this module directly:

1. Glycogen is stored with a fixed hydration coefficient: each gram
   of glycogen is associated with ``h_G = 2.7`` grams of water (their
   Equation 6 and its surrounding derivation). This is a physical/
   chemical property of glycogen granules, not a scientific theory
   with plausible alternatives -- unlike, say, competing BMR
   equations or adaptive thermogenesis archetypes, there is no
   "alternative hydration coefficient hypothesis" worth representing
   as a separate strategy. Accordingly, this module has no registry:
   a Strategy pattern would be architectural overkill for a physical
   constant.
2. On timescales longer than "a few days," carbohydrate balance is
   maintained at quasi-equilibrium (``dG/dt approx 0``) because
   glycogen's storage capacity is so small relative to fat and
   protein stores. This is the paper's own justification for why
   reduced models (which ignore glycogen entirely, treating all
   weight change as fat + lean mass) are valid for anything beyond a
   short transient window -- **exactly the reduced-model approach
   this project's Phases 8-11 already correctly use.** This module
   fills in precisely the short transient gap the reduced models
   deliberately skip, and hands off to the existing fat/lean
   machinery once glycogen re-equilibrates -- see the "Where this
   fits" section below and ``metabosim.simulation.stepper`` for the
   wiring.

Storage capacity
-------------------
Total-body glycogen storage capacity (liver + skeletal muscle) is
commonly cited at approximately 500 g for a ~70 kg reference adult
(~100 g liver, ~400 g muscle, in the postabsorptive state):
Iyer S, et al. "Carbohydrate storage in cells: a laboratory activity
for the assessment of glycogen stores in biological tissues."
*Adv Physiol Educ.* 2024 (states ~100 g liver / ~400 g skeletal
muscle for a 70 kg reference person); consistent with the review at
Physiopedia, "Glycogen" (~500 g skeletal muscle + liver combined).
This module scales that reference capacity linearly with body weight
as a documented simplification -- true capacity scales more closely
with muscle mass specifically than with total body weight, which this
project does not track as a separate compartment.

Estimating carbohydrate oxidation (the genuinely simplified part)
---------------------------------------------------------------------
Glycogen change follows directly from carbohydrate mass balance:

    dG/dt = carbohydrate_intake_g/day - carbohydrate_oxidized_g/day

Carbohydrate intake is known exactly (from
``metabosim.domain.diet.MacronutrientGrams``). Carbohydrate
*oxidation* is not directly modeled in this project (that would
require a respiratory-quotient / indirect-calorimetry submodel, or
Hall's full mechanistic macronutrient partitioning -- out of scope
here). This module estimates it as an exponential moving average of
recent carbohydrate intake, representing the idea that oxidation
adapts toward whatever intake level the body has recently equilibrated
to. This estimation method -- unlike the hydration coefficient and
storage capacity above -- is a pragmatic simplification, disclosed as
such, not an independently validated parameter.

Where this fits relative to Phases 8-11
---------------------------------------------------------------------
``metabosim.simulation.stepper`` uses this module's output as an
*additional, additive* term layered on top of the existing Forbes-
partitioned fat/lean trajectory (Phase 10), attributed entirely to
lean mass (since glycogen + its water are part of lean mass by the
Chow & Hall convention cited above -- see
``metabosim.domain.simulation_state.SimulationState`` field
docstrings). Because the underlying reduced fat/lean model already
assumes glycogen is at quasi-equilibrium, and this module's own
transient decays back to zero once intake stabilizes (the EMA
reference catches up to actual intake), the two layers do not double-
count: the transient handles the "first few days" Chow & Hall
describe, and the existing machinery handles everything after.
"""

from __future__ import annotations

#: Grams of water bound per gram of stored glycogen. See module
#: docstring for the citation (Chow & Hall, 2008).
GLYCOGEN_WATER_RATIO: float = 2.7

#: Reference body weight, in kg, for the reference glycogen capacity
#: below. See module docstring for the citation.
REFERENCE_WEIGHT_KG: float = 70.0

#: Reference total-body glycogen storage capacity, in grams, for a
#: subject at ``REFERENCE_WEIGHT_KG``. See module docstring.
REFERENCE_MAX_GLYCOGEN_G: float = 500.0

#: Default time constant, in days, for the exponential moving average
#: used to estimate carbohydrate oxidation from recent intake. Chosen
#: to match Chow & Hall's qualitative description of glycogen
#: transients lasting "a few days" -- a reasonable default, not an
#: independently fitted parameter. See module docstring.
DEFAULT_OXIDATION_TIME_CONSTANT_DAYS: float = 3.0


def max_glycogen_g(weight_kg: float) -> float:
    """Total-body glycogen storage capacity, in grams, for a subject
    of the given weight.

    Scales the reference capacity (500 g at 70 kg) linearly with body
    weight -- a documented simplification; true capacity tracks
    muscle mass more closely than total weight. See module docstring.

    Parameters
    ----------
    weight_kg:
        The subject's current body weight. Must be positive.
    """
    if weight_kg <= 0.0:
        raise ValueError(f"weight_kg must be positive; received {weight_kg!r}.")
    return REFERENCE_MAX_GLYCOGEN_G * (weight_kg / REFERENCE_WEIGHT_KG)


def glycogen_and_water_kg(glycogen_g: float) -> float:
    """Total mass, in kilograms, of a glycogen store *and* its bound
    water: ``glycogen_g * (1 + GLYCOGEN_WATER_RATIO) / 1000``.

    Parameters
    ----------
    glycogen_g:
        An absolute glycogen store level, in grams. Must be
        non-negative.
    """
    if glycogen_g < 0.0:
        raise ValueError(f"glycogen_g must be non-negative; received {glycogen_g!r}.")
    return glycogen_g * (1.0 + GLYCOGEN_WATER_RATIO) / 1000.0


def step_glycogen_g(
    current_glycogen_g: float,
    carbohydrate_intake_g: float,
    reference_carbohydrate_intake_g: float,
    weight_kg: float,
) -> float:
    """Advance the glycogen store by one day, via carbohydrate mass
    balance, clamped to storage capacity.

    Parameters
    ----------
    current_glycogen_g:
        The glycogen store at the start of the day. Must be
        non-negative.
    carbohydrate_intake_g:
        Today's actual carbohydrate intake, in grams (typically
        ``MacronutrientGrams.carbohydrate_g``; fiber is excluded, as
        it is not glycogenic).
    reference_carbohydrate_intake_g:
        The estimated carbohydrate oxidation rate for today, in
        grams -- see :func:`step_reference_carbohydrate_intake_g` for
        how this is maintained day to day. Must be non-negative.
    weight_kg:
        The subject's current body weight, used to compute storage
        capacity via :func:`max_glycogen_g`.

    Returns
    -------
    float
        The new glycogen store, clamped to
        ``[0, max_glycogen_g(weight_kg)]``.
    """
    if current_glycogen_g < 0.0:
        raise ValueError(
            f"current_glycogen_g must be non-negative; received {current_glycogen_g!r}."
        )
    carbohydrate_balance_g = carbohydrate_intake_g - reference_carbohydrate_intake_g
    unclamped_g = current_glycogen_g + carbohydrate_balance_g
    return max(0.0, min(max_glycogen_g(weight_kg), unclamped_g))


def step_reference_carbohydrate_intake_g(
    current_reference_g: float,
    todays_intake_g: float,
    time_constant_days: float = DEFAULT_OXIDATION_TIME_CONSTANT_DAYS,
) -> float:
    """Advance the exponential-moving-average estimate of carbohydrate
    oxidation by one day.

    Parameters
    ----------
    current_reference_g:
        Yesterday's reference (estimated oxidation) level, in grams.
    todays_intake_g:
        Today's actual carbohydrate intake, in grams.
    time_constant_days:
        The EMA time constant, in days. Must be positive. See module
        docstring for why the default is a reasonable choice, not an
        independently fitted parameter.

    Returns
    -------
    float
        The updated reference level, in grams.
    """
    if time_constant_days <= 0.0:
        raise ValueError(
            f"time_constant_days must be positive; received {time_constant_days!r}."
        )
    alpha = 1.0 / time_constant_days
    return current_reference_g + alpha * (todays_intake_g - current_reference_g)
