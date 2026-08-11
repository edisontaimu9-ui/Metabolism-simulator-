# Scientific Model References

Running bibliography, keyed by model/module. Updated every phase as
models are implemented. Every equation in `metabosim.models.*` must cite
an entry here in its module docstring.

## Domain layer constants (`metabosim.domain.constants`) — Phase 3

- FAO. "Food energy -- methods of analysis and conversion factors."
  FAO Food and Nutrition Paper 77. Rome; 2003. (Atwater general energy
  factors: 4/4/9/2/7 kcal per gram of protein/carbohydrate/fat/fiber/
  alcohol.)
- Institute of Medicine (US). *Dietary Reference Intakes for Energy...*
  National Academies Press; 2005. (Cross-referenced for Atwater factor
  consistency.)
- Gallagher D, Heymsfield SB, Heo M, et al. "Healthy percentage body
  fat ranges: an approach for developing guidelines based on body mass
  index." *Am J Clin Nutr.* 2000;72(3):694-701. (Basis for the
  essential-fat lower bound used in body fat % validation.)

## BMR / RMR models (`models.bmr`) — Phase 4

- Mifflin MD, St Jeor ST, Hill LA, et al. "A new predictive equation for
  resting energy expenditure in healthy individuals." *Am J Clin Nutr.*
  1990;51(2):241-247.
- Harris JA, Benedict FG. *A Biometric Study of Basal Metabolism in Man.*
  Carnegie Institution of Washington; 1919. Revised: Roza AM, Shizgal HM.
  "The Harris Benedict equation reevaluated." *Am J Clin Nutr.* 1984;40(1).
- Katch VL, McArdle WD, Katch FI. *Exercise Physiology.* (Lean-mass-based
  BMR formulation.)
- Cunningham JJ. "A reanalysis of the factors influencing basal metabolic
  rate in normal adults." *Am J Clin Nutr.* 1980;33(11):2372-2374.

## Physical activity / TDEE multiplier scheme (`models.tdee`) — Phase 5

- Mahan LK, Raymond JL, eds. *Krause's Food & the Nutrition Care
  Process.* Elsevier. (Widely reproduced table of clinical activity
  factors used to scale BMR to TDEE: 1.2 / 1.375 / 1.55 / 1.725 / 1.9
  for sedentary / light / moderate / active / very active.)
- Institute of Medicine (US). *Dietary Reference Intakes for Energy...*
  National Academies Press; 2005. (Alternative four-tier PAL banding;
  noted as a documented limitation -- see
  ``metabosim.models.tdee.pal_multiplier`` module docstring -- and
  planned as an explicit alternative model once
  ``metabosim.models.activity`` (Phase 7) is built.)

## TDEE / Activity models (`models.tdee`, `models.activity`) — Phases 5, 7

- Institute of Medicine (US). *Dietary Reference Intakes for Energy,
  Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino
  Acids.* National Academies Press; 2005. (Four-tier PAL banding;
  ``metabosim.models.activity.iom_pal`` interpolates a fifth tier to
  match this project's ``ActivityLevel`` enum -- see that module's
  docstring for the exact interpolation and why it is NOT an official
  IOM table.)
- Ainsworth BE, Haskell WL, Herrmann SD, et al. "2011 Compendium of
  Physical Activities: a second update of codes and MET values."
  *Med Sci Sports Exerc.* 2011;43(8):1575-1581. (MET values for
  ``metabosim.models.activity.met_based.ActivityEntry``.)
- Jette M, Sidney K, Blumchen G. "Metabolic equivalents (METS) in
  exercise testing, exercise prescription, and evaluation of
  functional capacity." *Clin Cardiol.* 1990;13(8):555-565. (Basis for
  the 1 MET = 1 kcal/kg/hour convention used in
  ``metabosim.models.activity.met_based``.)

## Thermic Effect of Food (`models.tef`) — Phase 6

- Jequier E, Tappy L. "Regulation of body weight in humans."
  *Physiol Rev.* 1999;79(2):451-480. (Macronutrient-specific thermic
  cost ranges: protein 20-30%, carbohydrate 5-10%, fat 0-3%, alcohol
  10-30% of that macronutrient's own energy contribution. This
  project uses the midpoint of each range --
  ``metabosim.models.tef.macronutrient_specific``.)
- Institute of Medicine (US). *Dietary Reference Intakes for Energy...*
  National Academies Press; 2005. (Commonly-used ~10%-of-total-intake
  approximation, used when macronutrient breakdown is unavailable --
  ``metabosim.models.tef.fixed_percentage``.)

## Energy balance (`models.energy_balance`) — Phase 8

- Wishnofsky M. "Caloric equivalents of gained or lost weight."
  *Am J Clin Nutr.* 1958;6(5):542-546. (Origin of the 3500 kcal/lb
  rule -- implemented and explicitly critiqued, not recommended, in
  ``metabosim.models.energy_balance.static_rule``.)
- Hall KD, Sacks G, Chandramohan D, et al. "Quantification of the effect
  of energy imbalance on bodyweight." *Lancet.* 2011;378(9793):826-837.
- Hall KD, Chow CC. "Why is the 3500 kcal per pound weight loss rule
  wrong?" *Int J Obes.* 2013;37(12):1614-1615.
- Hall KD, Jordan PN. "Modeling weight-loss maintenance to help
  prevent body weight regain." *Am J Clin Nutr.* 2008;88(6):1495-1503.
  (Basis for the reduced-form model in
  ``metabosim.models.energy_balance.dynamic_quasi_exponential``.)
- Heymsfield SB, Gonzalez MCC, Shen W, Redman L, Thomas D. "Weight loss
  composition is one-fourth fat-free mass: a critical review and
  critique of this widely cited rule." *Obes Rev.* 2014;15(4):310-321.
  (Fat mass ~9500 kcal/kg, fat-free mass ~1020 kcal/kg, and the
  default 25% FFM / 75% fat weight-change composition used in
  ``metabosim.models.energy_balance.tissue_energy_density``.)
- Yoo S. "Dynamic Energy Balance and Obesity Prevention."
  *J Obes Metab Syndr.* 2018;27(4):203-212. (Illustrative published
  example -- a 100 kg sedentary male at a sustained -500 kcal/day
  deficit approaching a ~75 kg steady state -- used to back-derive the
  default expenditure-feedback slope in
  ``metabosim.models.energy_balance.dynamic_quasi_exponential``.)

## Body composition partitioning (`models.body_composition`) — Phase 10

- Forbes GB. "Lean body mass-body fat interrelationships in humans."
  *Nutr Rev.* 1987;45(9):225-231.
- Forbes GB. "Body fat content influences the body composition response
  to nutrition and exercise." *Ann N Y Acad Sci.* 2000;904:359-365.
- Hall KD. "Body fat and fat-free mass inter-relationships: Forbes's
  theory revisited." *Br J Nutr.* 2007;97(6):1059-1063. (Infinitesimal
  differential form used directly: dFFM/dBW = 10.4/(10.4+FM); also
  derives the exact macroscopic correction, not implemented in this
  project -- see ``metabosim.models.body_composition.forbes`` module
  docstring for why.)
- Thomas D, Das SK, Levine JA, et al. "New fat free mass - fat mass
  model for use in physiological energy balance equations."
  *Nutr Metab (Lond).* 2010;7:39. (Male-specific Forbes constant,
  C=13.8 kg, used as this project's male default; disclosed as
  resting on a smaller evidence base than Forbes' original
  female-derived constant.)

## Adaptive thermogenesis (`models.adaptive_thermogenesis`) — Phase 11

- Leibel RL, Rosenbaum M, Hirsch J. "Changes in energy expenditure
  resulting from altered body weight." *N Engl J Med.*
  1995;332(10):621-628. (Foundational demonstration that maintaining
  a 10%+ altered body weight produces compensatory expenditure
  changes beyond those predicted by body composition alone.)
- Goldsmith R, Joanisse DR, Gallagher D, Pavlovich K, Shamoon E,
  Leibel RL, Rosenbaum M. "Effects of experimental weight
  perturbation on skeletal muscle work efficiency, fuel utilization,
  and biochemistry in human subjects." *Am J Physiol Regul Integr
  Comp Physiol.* 2010;298(1):R79-88. (States the calibration figure
  used directly: ~15% below/above predicted expenditure per unit
  metabolic mass at a 10% experimental weight change, symmetric for
  loss and gain.)
- Rosenbaum M, Leibel RL. "Models of energy homeostasis in response
  to maintenance of reduced body weight." *Obesity (Silver Spring).*
  2016;24(8):1620-1629. (Source of the three-model framework --
  none / threshold / proportional -- implemented directly as three
  separate strategies in this package.)
- Fothergill E, Guo J, Howard L, et al. "Persistent metabolic
  adaptation 6 years after 'The Biggest Loser' competition."
  *Obesity.* 2016;24(8):1612-1619. (~500 kcal/day persistent
  adaptation in an extreme-weight-loss cohort; concludes adaptation
  is "a proportional, but incomplete, response" -- cited as
  qualitative support for the proportional model archetype, not as a
  calibration source for this project's default parameters, since
  the cohort's weight change magnitude is far outside Leibel's
  originally-tested range.)
- Martins C, Roekenes J, Salamati S, et al. "Metabolic adaptation is
  an illusion, only present when participants are in negative energy
  balance." *Am J Clin Nutr.* 2020. (Cited as a documented
  counter-perspective: much apparent adaptation observed acutely
  after weight loss may resolve once weight stabilizes, underscoring
  why this project treats the magnitude/dynamics of adaptation as
  unsettled and defaults to the "no adaptation" model -- see
  ``metabosim.models.adaptive_thermogenesis.base`` module docstring.)
- Keys A, Brožek J, Henschel A, Mickelsen O, Taylor HL. *The Biology of
  Human Starvation.* University of Minnesota Press; 1950. (Minnesota
  Starvation Experiment — Phase 17 validation dataset source.)

## Macronutrient / organ metabolism (`models.macronutrient`, `models.organ`) — Phases 12-13

- Chow CC, Hall KD. "The Dynamics of Human Body Weight Change."
  *PLoS Comput Biol.* 2008;4(3):e1000045. (Source of the glycogen
  hydration coefficient used directly: 2.7 g water per g glycogen;
  also the justification for why glycogen can be treated as
  quasi-equilibrium/constant on timescales beyond a few days -- the
  reduced-model approach this project's Phases 8-11 already
  correctly use. See ``metabosim.models.macronutrient.glycogen``
  module docstring.)
- Iyer S, et al. "Carbohydrate storage in cells: a laboratory
  activity for the assessment of glycogen stores in biological
  tissues." *Adv Physiol Educ.* 2024. (~100 g liver + ~400 g skeletal
  muscle glycogen for a 70 kg reference adult -- the storage-capacity
  figure used in this project's default.)
- Frayn KN. *Metabolic Regulation: A Human Perspective.* 3rd ed.
  Wiley-Blackwell; 2010.

## Validation datasets — Phase 17

- Digitized data from the sources above will be stored in
  `src/metabosim/validation/datasets/` with a citation and a description
  of extraction methodology alongside each dataset file.
