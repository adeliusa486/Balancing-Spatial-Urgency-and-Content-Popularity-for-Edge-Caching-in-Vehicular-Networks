#!/usr/bin/env python
"""
scripts/compute_stats.py
Compute Wilcoxon signed-rank test between TC and LFU per-seed miss rates,
and print ablation table (W=0 proxy, W=0.2, W=1.0) from wsweep data.
"""
import json
import sys
from pathlib import Path
from scipy import stats
import numpy as np

# ---- Load per-seed data ----
alpha08 = json.loads(Path("experiments/results/alpha08/multiseed_alpha0.8.json").read_text())
wsweep  = json.loads(Path("experiments/results/wsweep/wsweep_results.json").read_text())

tc_seeds  = alpha08["results"]["TrajectoryCache"]["per_seed"]
lfu_seeds = alpha08["results"]["LFU"]["per_seed"]

# ---- Wilcoxon signed-rank test ----
stat, p = stats.wilcoxon(tc_seeds, lfu_seeds, alternative="less")
print(f"\n=== Wilcoxon signed-rank test: TC < LFU (alpha=0.8) ===")
print(f"  n = {len(tc_seeds)}")
print(f"  TC  mean={np.mean(tc_seeds):.4f}%  std={np.std(tc_seeds):.4f}%")
print(f"  LFU mean={np.mean(lfu_seeds):.4f}%  std={np.std(lfu_seeds):.4f}%")
print(f"  statistic = {stat:.3f}, p-value = {p:.4f}")
if p < 0.05:
    print("  => SIGNIFICANT (p < 0.05): TC has significantly lower miss rate than LFU")
else:
    print("  => Not significant at p=0.05")

# ---- Ablation table from wsweep ----
print(f"\n=== Ablation: W sweep (LFU mean={wsweep['lfu_mean']:.2f}%) ===")
print(f"{'W':>6}  {'TC mean%':>10}  {'TC std%':>8}  {'vs LFU':>8}")
print("-" * 42)
for w_str, vals in wsweep["w_sweep"].items():
    margin = vals["mean"] - wsweep["lfu_mean"]
    print(f"  {float(w_str):.1f}    {vals['mean']:>8.2f}%    {vals['std']:>6.2f}%   {margin:>+7.2f}%")
