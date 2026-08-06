"""
metabosim.domain.constants
===========================

Centralized numeric constants used by the domain layer for validation
and simple, universally-accepted derived quantities (e.g. macronutrient
energy density).

Design rule (see docs/architecture.md, coding standards): **no magic
numbers** anywhere else in the codebase. Every physiological constant
lives here, with a citation, and is imported by name.

This module intentionally contains only values that are:
  1. Physiologically-plausible *range bounds* used for input validation
     (not scientific "models" -- just sanity limits), or
  2. Universally-accepted conversion factors (Atwater general factors)
     that are not competing/interchangeable models themselves.

Anything that IS a competing scientific model (BMR equations, PAL
factors, etc.) belongs in ``metabosim.models.*``, not here.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Physiological plausibility bounds (for Pydantic field validation).
#
# These are deliberately generous "sanity" bounds -- wide enough to admit
# genuine clinical edge cases (e.g. neonates, bariatric patients) while
# rejecting obvious data-entry errors (negative weight, height in meters
# entered as centimeters, etc.). They are NOT clinical cutoffs.
# ---------------------------------------------------------------------------

#: Minimum plausible human age, in years. Zero admits neonates.
MIN_AGE_YEARS: float = 0.0

#: Maximum plausible human age, in years. Generous upper bound for
#: documented human longevity (oldest verified lifespan ~122 years;
#: Guinness World Records / Jeanne Calment, 1997).
MAX_AGE_YEARS: float = 130.0

#: Minimum plausible standing/recumbent height, in centimeters.
#: Admits premature neonates (~25 cm crown-heel length).
MIN_HEIGHT_CM: float = 25.0

#: Maximum plausible height, in centimeters. Tallest verified human
#: height on record: Robert Wadlow, 272 cm (Guinness World Records).
MAX_HEIGHT_CM: float = 275.0

#: Minimum plausible body weight, in kilograms. Admits extremely
#: low-birth-weight neonates.
MIN_WEIGHT_KG: float = 0.3

#: Maximum plausible body weight, in kilograms. Generous upper bound
#: covering documented severe obesity cases in clinical literature.
MAX_WEIGHT_KG: float = 650.0

#: Minimum plausible body fat percentage. Essential fat minimum for
#: males is commonly cited around 2-5% (Gallagher et al., 2000,
#: "Healthy percentage body fat ranges", Am J Clin Nutr).
MIN_BODY_FAT_PERCENT: float = 1.0

#: Maximum plausible body fat percentage. Extreme clinical obesity
#: cases rarely documented above ~70%.
MAX_BODY_FAT_PERCENT: float = 75.0

# ---------------------------------------------------------------------------
# Atwater general energy factors (kcal per gram of macronutrient).
#
# Source: FAO (2003). "Food energy -- methods of analysis and conversion
# factors." FAO Food and Nutrition Paper 77, Rome. Also consistent with
# Institute of Medicine (2005), Dietary Reference Intakes for Energy,
# Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino
# Acids, National Academies Press.
#
# These are the *general* (not food-specific) Atwater factors. They are
# treated as a fixed, non-competing convention (unlike BMR/TDEE
# equations) because they are the near-universal basis for food energy
# labeling worldwide, so they live in the domain layer as a shared
# utility rather than in ``models/`` as a swappable strategy.
# ---------------------------------------------------------------------------

#: kcal per gram of protein.
ATWATER_KCAL_PER_G_PROTEIN: float = 4.0

#: kcal per gram of carbohydrate (available, i.e. excluding fiber).
ATWATER_KCAL_PER_G_CARBOHYDRATE: float = 4.0

#: kcal per gram of fat.
ATWATER_KCAL_PER_G_FAT: float = 9.0

#: kcal per gram of ethanol (alcohol).
ATWATER_KCAL_PER_G_ALCOHOL: float = 7.0

#: kcal per gram of dietary fiber. FAO (2003) recommends 2 kcal/g for
#: fiber under the general factor system (vs. 0 under stricter systems);
#: 2 kcal/g is used here as the documented default.
ATWATER_KCAL_PER_G_FIBER: float = 2.0

# ---------------------------------------------------------------------------
# Energy unit conversion.
# ---------------------------------------------------------------------------

#: Kilocalories per kilojoule (1 kcal = 4.184 kJ exactly, by definition
#: of the thermochemical calorie).
KCAL_TO_KJ: float = 4.184

# ---------------------------------------------------------------------------
# Mass unit conversion.
# ---------------------------------------------------------------------------

#: Kilograms per pound (exact, international avoirdupois pound).
KG_PER_LB: float = 0.45359237

#: Centimeters per inch (exact).
CM_PER_INCH: float = 2.54
