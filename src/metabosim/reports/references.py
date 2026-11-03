"""
metabosim.reports.references
================================

Maps each selectable model ID to the short-form citations that support
it, so a report can cite exactly the models a given run used (not the
whole bibliography).

Source of truth
---------------------------------------------------------------------
``docs/model_references.md`` remains the authoritative bibliography.
The strings here are short-form copies of entries in it, stored in the
package because ``docs/`` is not shipped with an installed wheel. A
unit test checks that every citation here still appears in that file
(when it is present), so the two cannot silently drift apart. Plain
text only: no Markdown formatting, because both report renderers
escape all text uniformly.
"""

from __future__ import annotations

from metabosim.simulation.config import SimulationConfig

_MIFFLIN = (
    'Mifflin MD, St Jeor ST, Hill LA, et al. "A new predictive equation '
    'for resting energy expenditure in healthy individuals." Am J Clin '
    "Nutr. 1990;51(2):241-247."
)
_HARRIS = (
    "Harris JA, Benedict FG. A Biometric Study of Basal Metabolism in "
    "Man. Carnegie Institution of Washington; 1919."
)
_ROZA = (
    'Roza AM, Shizgal HM. "The Harris Benedict equation reevaluated." '
    "Am J Clin Nutr. 1984;40(1)."
)
_KATCH = "Katch VL, McArdle WD, Katch FI. Exercise Physiology."
_CUNNINGHAM = (
    'Cunningham JJ. "A reanalysis of the factors influencing basal '
    'metabolic rate in normal adults." Am J Clin Nutr. 1980;33(11):'
    "2372-2374."
)
_ELIA = (
    'Elia M. "Organ and tissue contribution to metabolic rate." In: '
    "Kinney JM, Tucker HN, eds. Energy Metabolism: Tissue Determinants "
    "and Cellular Corollaries. Raven Press; 1992:61-80."
)
_WANG = (
    'Wang Z, Ying Z, Bosy-Westphal A, et al. "Specific metabolic rates '
    "of major organs and tissues across adulthood: evaluation by "
    'mechanistic model of resting energy expenditure." Am J Clin Nutr. '
    "2010;92(6):1369-1377."
)
_JEQUIER = (
    'Jequier E, Tappy L. "Regulation of body weight in humans." Physiol '
    "Rev. 1999;79(2):451-480."
)
_IOM = (
    "Institute of Medicine (US). Dietary Reference Intakes for Energy, "
    "Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and "
    "Amino Acids. National Academies Press; 2005."
)
_WISHNOFSKY = (
    'Wishnofsky M. "Caloric equivalents of gained or lost weight." Am J '
    "Clin Nutr. 1958;6(5):542-546."
)
_HALL_CHOW = (
    'Hall KD, Chow CC. "Why is the 3500 kcal per pound weight loss rule '
    'wrong?" Int J Obes. 2013;37(12):1614-1615.'
)
_HEYMSFIELD = (
    "Heymsfield SB, Gonzalez MCC, Shen W, Redman L, Thomas D. "
    '"Weight loss composition is one-fourth fat-free mass: a critical '
    'review and critique of this widely cited rule." Obes Rev. '
    "2014;15(4):310-321."
)
_HALL_JORDAN = (
    'Hall KD, Jordan PN. "Modeling weight-loss maintenance to help '
    'prevent body weight regain." Am J Clin Nutr. 2008;88(6):1495-1503.'
)
_YOO = (
    'Yoo S. "Dynamic Energy Balance and Obesity Prevention." J Obes '
    "Metab Syndr. 2018;27(4):203-212."
)
_FORBES = (
    'Forbes GB. "Lean body mass-body fat interrelationships in humans." '
    "Nutr Rev. 1987;45(9):225-231."
)
_HALL_FORBES = (
    'Hall KD. "Body fat and fat-free mass inter-relationships: '
    "Forbes's theory revisited.\" Br J Nutr. 2007;97(6):1059-1063."
)
_THOMAS = (
    'Thomas D, Das SK, Levine JA, et al. "New fat free mass - fat mass '
    'model for use in physiological energy balance equations." Nutr '
    "Metab (Lond). 2010;7:39."
)
_LEIBEL = (
    'Leibel RL, Rosenbaum M, Hirsch J. "Changes in energy expenditure '
    'resulting from altered body weight." N Engl J Med. '
    "1995;332(10):621-628."
)
_ROSENBAUM = (
    'Rosenbaum M, Leibel RL. "Models of energy homeostasis in response '
    'to maintenance of reduced body weight." Obesity (Silver Spring). '
    "2016;24(8):1620-1629."
)
_FOTHERGILL = (
    'Fothergill E, Guo J, Howard L, et al. "Persistent metabolic '
    "adaptation 6 years after 'The Biggest Loser' competition.\" "
    "Obesity. 2016;24(8):1612-1619."
)
_ATWATER = (
    'FAO. "Food energy -- methods of analysis and conversion factors." '
    "FAO Food and Nutrition Paper 77. Rome; 2003."
)
_AINSWORTH = (
    'Ainsworth BE, Haskell WL, Herrmann SD, et al. "2011 Compendium of '
    'Physical Activities: a second update of codes and MET values." '
    "Med Sci Sports Exerc. 2011;43(8):1575-1581."
)
_JETTE = (
    'Jette M, Sidney K, Blumchen G. "Metabolic equivalents (METS) in '
    "exercise testing, exercise prescription, and evaluation of "
    'functional capacity." Clin Cardiol. 1990;13(8):555-565.'
)
_CHOW_HALL = (
    'Chow CC, Hall KD. "The Dynamics of Human Body Weight Change." PLoS '
    "Comput Biol. 2008;4(3):e1000045."
)

BMR_REFERENCES: dict[str, tuple[str, ...]] = {
    "mifflin_st_jeor": (_MIFFLIN,),
    "harris_benedict": (_HARRIS, _ROZA),
    "katch_mcardle": (_KATCH,),
    "cunningham": (_CUNNINGHAM,),
    "elia_organ_based": (_ELIA, _WANG),
}

TEF_REFERENCES: dict[str, tuple[str, ...]] = {
    "macronutrient_specific": (_JEQUIER,),
    "fixed_percentage": (_IOM,),
}

ENERGY_BALANCE_REFERENCES: dict[str, tuple[str, ...]] = {
    "static_rule": (_WISHNOFSKY, _HALL_CHOW),
    "tissue_energy_density": (_HEYMSFIELD,),
    "dynamic_quasi_exponential": (_HALL_JORDAN, _YOO),
}

BODY_COMPOSITION_REFERENCES: dict[str, tuple[str, ...]] = {
    "forbes": (_FORBES, _HALL_FORBES, _THOMAS),
}

#: ``"none"`` deliberately has no citation: it models no adaptation.
ADAPTIVE_THERMOGENESIS_REFERENCES: dict[str, tuple[str, ...]] = {
    "none": (),
    "threshold": (_LEIBEL, _ROSENBAUM),
    "proportional": (_LEIBEL, _ROSENBAUM, _FOTHERGILL),
}

#: Always cited: every run uses Atwater energy factors and MET-based
#: activity energy.
ALWAYS_REFERENCES: tuple[str, ...] = (_ATWATER, _AINSWORTH, _JETTE)

#: Cited only when glycogen tracking was active.
GLYCOGEN_REFERENCES: tuple[str, ...] = (_CHOW_HALL,)


def references_for_run(
    config: SimulationConfig,
    *,
    tracked_body_composition: bool,
    tracked_glycogen: bool,
) -> list[str]:
    """Return the de-duplicated citations relevant to one run.

    Parameters
    ----------
    config:
        The run's configuration.
    tracked_body_composition:
        Whether body composition tracking was active. The body
        composition model is only cited if it actually ran.
    tracked_glycogen:
        Whether glycogen tracking was active.

    Raises
    ------
    KeyError
        If a configured model ID has no entry here (a newly
        registered model whose citations were not added).
    """
    groups: list[tuple[str, ...]] = [
        BMR_REFERENCES[config.bmr_model_id],
        TEF_REFERENCES[config.tef_model_id],
        ENERGY_BALANCE_REFERENCES[config.energy_balance_model_id],
        ADAPTIVE_THERMOGENESIS_REFERENCES[config.adaptive_thermogenesis_model_id],
        ALWAYS_REFERENCES,
    ]
    if tracked_body_composition:
        groups.append(BODY_COMPOSITION_REFERENCES[config.body_composition_model_id])
    if tracked_glycogen:
        groups.append(GLYCOGEN_REFERENCES)

    seen: set[str] = set()
    ordered: list[str] = []
    for group in groups:
        for citation in group:
            if citation not in seen:
                seen.add(citation)
                ordered.append(citation)
    return ordered
