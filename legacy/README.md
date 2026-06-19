# Legacy Scripts

These files are retained for historical reference only.
They are NOT part of the canonical experimental pipeline.

## Why retained
- `simpy_simulation.py` / `sumo_cache_sim.py`: early prototypes with incorrect TC
  parameters (GRZ_RADIUS=150, T_PREDICT=3.0). These were NOT used to generate
  any result in the submitted paper.
- `run_alpha_*.py` / `run_journal_eval.py`: intermediate experiment runners
  superseded by `scripts/run_multiseed.py`.
- `matlab_simulation.m`: exploratory MATLAB prototype; not connected to paper results.
- `run_sweeps.py`: superseded by `scripts/run_wsweep.py`.

## Canonical pipeline
All paper results are reproducible exclusively via:
  scripts/run_multiseed.py
  scripts/run_wsweep.py
  scripts/run_density_sweep.py
  scripts/compute_stats.py
