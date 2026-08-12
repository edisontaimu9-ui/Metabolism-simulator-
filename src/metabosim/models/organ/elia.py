"""
metabosim.models.organ.elia
==============================

Decomposes whole-body Basal/Resting Metabolic Rate into per-organ and
per-tissue contributions, using Elia's specific metabolic rates
applied to reference organ masses and this project's already-tracked
fat mass / lean mass.

Why no registry (same reasoning as Phase 12's glycogen module)
---------------------------------------------------------------------
Elia's specific metabolic rates (Ki values, in kcal/kg/day) for each
organ and tissue are a cited, empirically-derived dataset -- not a
competing scientific hypothesis with named alternatives, unlike BMR
equations or adaptive thermogenesis archetypes elsewhere in this
project. There is exactly one widely-used table here, so a Strategy
pattern with a registry would be architectural overkill, matching the
precedent set in ``metabosim.models.macronutrient.glycogen``.

Reference: specific metabolic rates (Ki)
-------------------------------------------
Elia M. "Organ and tissue contribution to metabolic rate." In:
Kinney JM, Tucker HN, eds. *Energy Metabolism: Tissue Determinants and
Cellular Corollaries.* Raven Press; 1992:61-80. Values confirmed
directly (multiple independent secondary sources quote the same
figures verbatim) as, in kcal/kg/day: liver 200, brain 240, heart 440,
kidneys 440, skeletal muscle 13, adipose tissue 4.5, residual mass 12.

Age adjustment: Wang Z, Ying Z, Bosy-Westphal A, et al. "Specific
metabolic rates of major organs and tissues across adulthood:
evaluation by mechanistic model of resting energy expenditure."
*Am J Clin Nutr.* 2010;92(6):1369-1377. Found Elia's values
overestimate by ~3% in adults over 50, reporting age-adjusted values
for that group: liver 194, brain 233, heart/kidneys 426, skeletal
muscle 12.6, adipose tissue 4.4, residual 11.6. This module uses the
age-adjusted set automatically when ``age_years > 50``.

Reference: organ masses
--------------------------
This project does not track individual organ masses (no MRI or
imaging data), so brain, liver, heart, and kidney masses are taken as
fixed population-reference constants -- the standard practice in this
literature when applying Elia's Ki values without individual imaging
(contrast with Wang et al.'s own MRI-based *validation* studies,
which is a different use case from the default, no-imaging-required
estimate this module provides). Values from peer-reviewed forensic
autopsy studies:

Molina DK, DiMaio VJ. "Normal organ weights in men: part II -- the
brain, lungs, liver, spleen, and kidneys." *Am J Forensic Med Pathol.*
2012;33(4):368-372. Mean brain 1407 g, mean liver 1561 g, combined
kidney mass (right 129 g + left 137 g) 266 g.

Molina DK, DiMaio VJ. "Normal organ weights in men: part I -- the
heart." *Am J Forensic Med Pathol.* 2012;33(4):362-367. Heart mass
range 250-350 g; this module uses 300 g as a representative midpoint.

These are adult male autopsy data; companion studies exist for women
(Molina DK, et al. "Normal Organ Weights in Women." *Am J Forensic
Med Pathol.* 2015, Parts I-II) with somewhat lower values for most
organs. Sex-specific reference masses are a documented possible
refinement, not implemented here -- this module uses one sex-
unadjusted set of reference masses for both sexes, disclosed as an
approximation.

The residual-lean simplification
------------------------------------
Elia's skeletal muscle (13 kcal/kg/day) and residual mass
(12 kcal/kg/day) rates are very close to each other. Since this
project does not track skeletal muscle mass separately from other
lean tissue (only total lean mass, via
``metabosim.models.body_composition``), this module combines them
into one "residual lean" bucket using their simple average as a
blended rate -- the small gap between the two source rates means this
simplification has minimal impact on the total.

Cross-validation with Phase 4's BMR equations
---------------------------------------------------------------------
This organ-based estimate is an independent, bottom-up calculation of
the same physical quantity Phase 4's regression equations
(Mifflin-St Jeor, Harris-Benedict, etc.) estimate top-down. The two
methods are expected to agree only approximately (they are built from
entirely different data and assumptions) -- see
``metabosim.models.bmr.elia_organ_based`` for how this module is
exposed as a selectable BMR strategy alongside those equations, and
``docs/phase_notes/phase_13.md`` for a worked comparison.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

#: Reference organ masses, in kg, for an adult (sex-unadjusted -- see
#: module docstring). Molina & DiMaio, 2012 (two-part study).
REFERENCE_BRAIN_KG: float = 1.407
REFERENCE_LIVER_KG: float = 1.561
REFERENCE_HEART_KG: float = 0.300
REFERENCE_KIDNEYS_KG: float = 0.266

#: Elia (1992) specific metabolic rates, in kcal/kg/day, for young/
#: middle-aged adults. See module docstring for the full citation.
KI_BRAIN: float = 240.0
KI_LIVER: float = 200.0
KI_HEART: float = 440.0
KI_KIDNEYS: float = 440.0
KI_SKELETAL_MUSCLE: float = 13.0
KI_ADIPOSE: float = 4.5
KI_RESIDUAL: float = 12.0

#: Blended "residual lean" rate (skeletal muscle + residual mass
#: averaged), used because this project does not track skeletal
#: muscle mass separately. See module docstring.
KI_RESIDUAL_LEAN: float = (KI_SKELETAL_MUSCLE + KI_RESIDUAL) / 2.0

#: Age-adjusted Ki values for adults over 50 (Wang et al., 2010). See
#: module docstring.
KI_BRAIN_OVER_50: float = 233.0
KI_LIVER_OVER_50: float = 194.0
KI_HEART_OVER_50: float = 426.0
KI_KIDNEYS_OVER_50: float = 426.0
KI_SKELETAL_MUSCLE_OVER_50: float = 12.6
KI_ADIPOSE_OVER_50: float = 4.4
KI_RESIDUAL_OVER_50: float = 11.6
KI_RESIDUAL_LEAN_OVER_50: float = (
    KI_SKELETAL_MUSCLE_OVER_50 + KI_RESIDUAL_OVER_50
) / 2.0

#: Age threshold, in years, at which the age-adjusted Ki set is used.
AGE_ADJUSTMENT_THRESHOLD_YEARS: float = 50.0

#: Total reference mass of the four fixed organs, in kg -- the
#: minimum lean mass this module can decompose.
_REFERENCE_FIXED_ORGAN_MASS_KG: float = (
    REFERENCE_BRAIN_KG + REFERENCE_LIVER_KG + REFERENCE_HEART_KG + REFERENCE_KIDNEYS_KG
)


class OrganBMRBreakdown(BaseModel):
    """A whole-body BMR estimate decomposed into per-organ/tissue
    contributions. See module docstring for the underlying model.

    ``brain_kg`` / ``liver_kg`` / ``heart_kg`` / ``kidneys_kg`` are
    fixed reference masses (identical across calls, not
    subject-specific); ``residual_lean_kg`` and ``adipose_kg`` are
    subject-specific, derived from the caller's actual lean and fat
    mass.
    """

    model_config = ConfigDict(frozen=True)

    brain_kg: float
    brain_kcal: float
    liver_kg: float
    liver_kcal: float
    heart_kg: float
    heart_kcal: float
    kidneys_kg: float
    kidneys_kcal: float
    residual_lean_kg: float
    residual_lean_kcal: float
    adipose_kg: float
    adipose_kcal: float
    total_kcal: float


def calculate_organ_bmr_breakdown_kcal(
    fat_mass_kg: float,
    lean_mass_kg: float,
    age_years: float | None = None,
) -> OrganBMRBreakdown:
    """Decompose a whole-body BMR estimate into per-organ/tissue
    contributions, given fat mass and lean mass.

    Parameters
    ----------
    fat_mass_kg:
        The subject's fat mass, in kg. Must be non-negative.
    lean_mass_kg:
        The subject's lean (fat-free) mass, in kg. Must be at least
        the combined reference mass of the four fixed organs
        (~3.53 kg) -- see module docstring; smaller values are
        physiologically implausible for an adult and raise
        ``ValueError``.
    age_years:
        The subject's age, if known. When greater than
        ``AGE_ADJUSTMENT_THRESHOLD_YEARS`` (50), the age-adjusted Ki
        values (Wang et al., 2010) are used instead of Elia's
        original defaults. ``None`` (default) uses Elia's defaults.

    Returns
    -------
    OrganBMRBreakdown
        The full per-organ/tissue breakdown and total.

    Raises
    ------
    ValueError
        If ``fat_mass_kg`` is negative, or if ``lean_mass_kg`` is
        smaller than the combined reference mass of the four fixed
        organs.
    """
    if fat_mass_kg < 0.0:
        raise ValueError(f"fat_mass_kg must be non-negative; received {fat_mass_kg!r}.")
    if lean_mass_kg < _REFERENCE_FIXED_ORGAN_MASS_KG:
        raise ValueError(
            f"lean_mass_kg ({lean_mass_kg!r}) is smaller than the combined "
            f"reference mass of brain+liver+heart+kidneys "
            f"({_REFERENCE_FIXED_ORGAN_MASS_KG:.3f} kg) -- implausible for "
            "an adult. This model does not support subjects smaller than "
            "the reference organ masses it assumes."
        )

    use_age_adjusted = (
        age_years is not None and age_years > AGE_ADJUSTMENT_THRESHOLD_YEARS
    )
    ki_brain = KI_BRAIN_OVER_50 if use_age_adjusted else KI_BRAIN
    ki_liver = KI_LIVER_OVER_50 if use_age_adjusted else KI_LIVER
    ki_heart = KI_HEART_OVER_50 if use_age_adjusted else KI_HEART
    ki_kidneys = KI_KIDNEYS_OVER_50 if use_age_adjusted else KI_KIDNEYS
    ki_adipose = KI_ADIPOSE_OVER_50 if use_age_adjusted else KI_ADIPOSE
    ki_residual_lean = (
        KI_RESIDUAL_LEAN_OVER_50 if use_age_adjusted else KI_RESIDUAL_LEAN
    )

    residual_lean_kg = lean_mass_kg - _REFERENCE_FIXED_ORGAN_MASS_KG

    brain_kcal = REFERENCE_BRAIN_KG * ki_brain
    liver_kcal = REFERENCE_LIVER_KG * ki_liver
    heart_kcal = REFERENCE_HEART_KG * ki_heart
    kidneys_kcal = REFERENCE_KIDNEYS_KG * ki_kidneys
    residual_lean_kcal = residual_lean_kg * ki_residual_lean
    adipose_kcal = fat_mass_kg * ki_adipose

    total_kcal = (
        brain_kcal
        + liver_kcal
        + heart_kcal
        + kidneys_kcal
        + residual_lean_kcal
        + adipose_kcal
    )

    return OrganBMRBreakdown(
        brain_kg=REFERENCE_BRAIN_KG,
        brain_kcal=brain_kcal,
        liver_kg=REFERENCE_LIVER_KG,
        liver_kcal=liver_kcal,
        heart_kg=REFERENCE_HEART_KG,
        heart_kcal=heart_kcal,
        kidneys_kg=REFERENCE_KIDNEYS_KG,
        kidneys_kcal=kidneys_kcal,
        residual_lean_kg=residual_lean_kg,
        residual_lean_kcal=residual_lean_kcal,
        adipose_kg=fat_mass_kg,
        adipose_kcal=adipose_kcal,
        total_kcal=total_kcal,
    )
