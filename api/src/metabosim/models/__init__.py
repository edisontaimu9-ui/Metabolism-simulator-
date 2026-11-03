"""
metabosim.models
=================

Container package for all scientific model strategy families:

- ``bmr``                     Basal/Resting Metabolic Rate equations
- ``tef``                     Thermic Effect of Food models
- ``activity``                Physical activity energy expenditure models
- ``tdee``                    Total Daily Energy Expenditure composition models
- ``energy_balance``          Energy surplus/deficit -> mass change models
- ``body_composition``        Fat mass / fat-free mass partitioning models
- ``adaptive_thermogenesis``  Metabolic adaptation beyond mass-predicted BMR
- ``macronutrient``           Glycogen, water, and substrate oxidation models
- ``organ``                   Organ-level metabolic contribution models
- ``disease``                 Disease-specific modifiers (decorators)

Every subpackage exposes its models behind a common interface
(an ``abc.ABC`` or ``typing.Protocol``) plus a registry, so that the
simulation engine in ``metabosim.simulation`` can select models by
name at runtime without hardcoding any particular equation.
"""
