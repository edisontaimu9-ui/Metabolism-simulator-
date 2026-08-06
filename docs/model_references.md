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

## TDEE / Activity models (`models.tdee`, `models.activity`) — Phases 5, 7

- Institute of Medicine (US). *Dietary Reference Intakes for Energy,
  Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino
  Acids.* National Academies Press; 2005. (PAL categories, TEF baselines.)
- Ainsworth BE, et al. "2011 Compendium of Physical Activities: a second
  update of codes and MET values." *Med Sci Sports Exerc.* 2011.

## Thermic Effect of Food (`models.tef`) — Phase 6

- Jequier E, Tappy L. "Regulation of body weight in humans."
  *Physiol Rev.* 1999;79(2):451-480.

## Energy balance (`models.energy_balance`) — Phase 8

- Hall KD, Sacks G, Chandramohan D, et al. "Quantification of the effect
  of energy imbalance on bodyweight." *Lancet.* 2011;378(9793):826-837.
- Hall KD, Chow CC. "Why is the 3500 kcal per pound weight loss rule
  wrong?" *Int J Obes.* 2013;37(12):1614-1615.

## Body composition partitioning (`models.body_composition`) — Phase 10

- Forbes GB. "Lean body mass-body fat interrelationships in humans."
  *Nutr Rev.* 1987;45(9):225-231.
- Forbes GB. "Body fat content influences the body composition response
  to nutrition and exercise." *Ann N Y Acad Sci.* 2000;904:359-365.

## Adaptive thermogenesis (`models.adaptive_thermogenesis`) — Phase 11

- Leibel RL, Rosenbaum M, Hirsch J. "Changes in energy expenditure
  resulting from altered body weight." *N Engl J Med.* 1995;332(10):621-628.
- Fothergill E, Guo J, Howard L, et al. "Persistent metabolic adaptation
  6 years after 'The Biggest Loser' competition." *Obesity.* 2016;24(8).
- Keys A, Brožek J, Henschel A, Mickelsen O, Taylor HL. *The Biology of
  Human Starvation.* University of Minnesota Press; 1950. (Minnesota
  Starvation Experiment — Phase 17 validation dataset source.)

## Macronutrient / organ metabolism (`models.macronutrient`, `models.organ`) — Phases 12-13

- Frayn KN. *Metabolic Regulation: A Human Perspective.* 3rd ed.
  Wiley-Blackwell; 2010.

## Validation datasets — Phase 17

- Digitized data from the sources above will be stored in
  `src/metabosim/validation/datasets/` with a citation and a description
  of extraction methodology alongside each dataset file.
