"""
metabosim.models.disease.body_temperature
=============================================

Models the effect of elevated or reduced core body temperature
(fever / therapeutic or accidental hypothermia) on BMR.

    bmr_adjustment_fraction = KI_PER_CELSIUS * (body_temperature_c - 37.0)

Reference
---------
DuBois EF. *Fever and the Regulation of Body Temperature.*
Springfield, IL: Charles C Thomas; 1937. The original, still
canonically-cited source for the widely-used clinical rule of thumb
that metabolic rate rises approximately **13% for each 1 degree
Celsius** of fever above normal body temperature (37 degC) -- see e.g.
its restatement in nutrition/metabolism literature reviewing the
energy cost of infection. This figure remains the standard reference
value used across modern critical care and clinical nutrition
sources, which commonly cite a "10-13%" range with 13% as the
classic/upper figure attributed directly to DuBois.

Bidirectional: fever and hypothermia
-----------------------------------------
The same approximately-linear relationship between core temperature
and metabolic rate is reported in both directions: therapeutic or
accidental hypothermia is associated with a comparable ~5-13% per
degC *reduction* in metabolic rate (used clinically, for example, to
reduce oxygen demand during induced hypothermia for brain ischemia).
This module applies the same coefficient symmetrically in both
directions as a documented simplification -- the cited literature
describes comparable-magnitude effects in both directions without
asserting the coefficient is identical to more than one significant
figure in each direction.

Known limitation
------------------
Real fever/hypermetabolic response also depends on the underlying
cause (e.g. sepsis independently drives hypermetabolism beyond what
temperature elevation alone would predict -- see
``metabosim.models.disease`` module docstring's notes on
comorbidities) and on individual variation; this module captures only
the temperature-mediated component via the single DuBois coefficient,
not a full critical-illness metabolic model.
"""

from __future__ import annotations

from metabosim.domain.person import Person
from metabosim.models.disease.base import DiseaseModifier

#: Fractional BMR change per degree Celsius of core temperature
#: deviation from normal. See module docstring for the citation
#: (DuBois, 1937).
KI_PER_CELSIUS: float = 0.13

#: Reference normal core body temperature, in degrees Celsius.
NORMAL_BODY_TEMPERATURE_C: float = 37.0


class BodyTemperatureModifier(DiseaseModifier):
    """Adjusts BMR based on core body temperature deviation from
    normal (37 degC), in either direction. See module docstring for
    the model and its citation.

    Parameters
    ----------
    body_temperature_c:
        The subject's core body temperature, in degrees Celsius. Must
        be within a physiologically survivable range (20-45 degC);
        values outside that range raise ``ValueError``.
    ki_per_celsius:
        The fractional BMR change per degree Celsius, applied
        symmetrically for elevation and reduction. Defaults to 0.13
        (DuBois, 1937).
    """

    def __init__(
        self,
        body_temperature_c: float,
        ki_per_celsius: float = KI_PER_CELSIUS,
    ) -> None:
        if not 20.0 <= body_temperature_c <= 45.0:
            raise ValueError(
                "body_temperature_c must be within the physiologically "
                f"survivable range [20, 45] degC; received {body_temperature_c!r}."
            )
        self.body_temperature_c = body_temperature_c
        self.ki_per_celsius = ki_per_celsius
        delta = body_temperature_c - NORMAL_BODY_TEMPERATURE_C
        direction = "fever" if delta > 0 else "hypothermia" if delta < 0 else "normal"
        self.name = f"Body Temperature ({body_temperature_c:.1f}\u00b0C, {direction})"

    def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
        if base_bmr_kcal <= 0.0:
            raise ValueError(
                f"base_bmr_kcal must be positive; received {base_bmr_kcal!r}."
            )
        delta_c = self.body_temperature_c - NORMAL_BODY_TEMPERATURE_C
        return base_bmr_kcal * (1.0 + self.ki_per_celsius * delta_c)
