# Publications

This repository is framed around the FastBlade / LoadTide full-scale tidal blade fatigue-test campaign. The first two papers define the primary scope of the public code. The later papers are included as related FastBlade studies to show the broader experimental programme without over-claiming reproducibility.

## Primary publications supported by this repository scope

### 1. A Full-Scale Tidal Blade Fatigue Test using the FastBlade Facility

**Role in repository:** primary scope.

This paper is the main context for the static, fatigue, natural-frequency, displacement, strain, actuator-load, and root-bending-moment workflows. It includes the first full-scale fatigue test at FastBlade and the single-actuator configuration.

Relevant software themes:

- TDMS channel processing;
- static loading analysis;
- fatigue-cycle peak/trough analysis;
- natural-frequency tracking;
- load-displacement and strain-load relationships;
- actuator load and root bending moment calculations.

### 2. A full-scale composite tidal blade fatigue test using single and multiple actuators

**Role in repository:** primary scope.

This paper motivates the actuator-configuration layer in the repository. It compares single-actuator and three-actuator loading, including differences in bending moment, shear force, displacement, strain, and control noise.

Relevant software themes:

- single-vs-multi-actuator configuration;
- point-load root bending moment checks;
- static and fatigue comparisons across test campaigns;
- displacement and strain summary workflows;
- actuator-load data QA/QC.

## Related FastBlade studies

### 3. Clamping parameters in full-scale tidal turbine blade tests: A case study

**Role in repository:** related follow-on methodology.

This study extends the FastBlade experimental programme to saddle/load-introduction effects, clamping preload, DIC, and exclusion-zone interpretation. It is relevant to the interpretation of strain data near loading saddles, but this repository does not currently claim to reproduce the DIC or clamping-specific workflow.

### 4. Destructive testing and failure analysis of a full-scale composite tidal turbine blade

**Role in repository:** related later campaign.

This study extends the programme into failure-oriented testing, residual strength, crack/notch studies, seam failure, and post-damage natural-frequency reduction. It is listed for context only. The current public package focuses on the reusable TDMS/static/fatigue/natural-frequency layer, not the full destructive-test analysis.

## Recommended README claim

Use this language in public descriptions:

> Python workflows for processing and analysing FastBlade / LoadTide full-scale tidal blade test data, with primary focus on TDMS-based static, fatigue, natural-frequency, strain, displacement, actuator-load, and root-bending-moment analyses from the first fatigue and single-vs-multi-actuator studies. Related FastBlade clamping and destructive-testing studies are documented as broader experimental context.

Avoid this stronger claim unless raw data and paper-specific scripts are added:

> This repository fully reproduces all four papers.
