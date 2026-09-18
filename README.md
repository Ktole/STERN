# STEN-RP Reproducibility Repository (v0.1.0)

Research code and data layout for the Stochastic Temporary Endogenous Network Routing Problem (STEN-RP).

## Contents
- `src/benchmark_generator.py`: seeded synthetic benchmark generator.
- `src/scenario_generator.py`: seeded scenario generator for travel factors, activation success, and temporary lifetimes.
- `src/milp_model.py`: SciPy/HiGHS MILP reference model for a scenario-realized time-expanded STEN-RP instance.
- `src/saa_simopt.py`: replicated SAA simulation--optimization driver with common random numbers and independent validation/test samples.
- `src/run_all.py`: end-to-end reproducibility entry point.
- `analysis/analyze_results.py`: summary statistics and confidence intervals.
- `data/benchmarks/`, `data/scenarios/`: generated inputs.
- `outputs/`: raw run-level outputs and summaries.
- `config/experiment.json`: experiment configuration and seeds.
- `CITATION.cff`, `LICENSE`, `requirements.txt`, `VERSION`.

## Run
```bash
python src/run_all.py
python analysis/analyze_results.py
```

The package is versioned locally as v0.1.0. A persistent identifier (e.g. DOI) cannot be created inside this offline package; after uploading the repository to a preservation service such as Zenodo, record the assigned identifier in `CITATION.cff` and the manuscript.

## Scope
This is a transparent executable research prototype. The MILP implements the core time-expanded routing/action/temporary-availability logic for realized scenarios. The SAA driver uses replicated samples and independent validation/testing. Before publication, align any additional manuscript-specific resource, nonanticipativity, or penalty constraints exactly with the final mathematical formulation and archive the final frozen release.
