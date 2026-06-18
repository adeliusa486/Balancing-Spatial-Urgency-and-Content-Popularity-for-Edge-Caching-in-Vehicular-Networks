#!/usr/bin/env python
"""
scripts/run_multiseed.py

Run the benchmark across multiple random seeds and report mean ± std
for each policy. Produces Table 1 / Table 2 data for the paper.

Usage
-----
    python scripts/run_multiseed.py
    python scripts/run_multiseed.py --zipf-alpha 0.5 --output experiments/results/alpha05
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trajectorycache.evaluation.benchmark import run_benchmark, DEFAULT_POLICIES
from trajectorycache.simulation.runner import SimulationConfig
from trajectorycache.utils.config import load_config
from trajectorycache.utils.logging import setup_logging

# The 10 seeds reported in the paper (§4.4)
PAPER_SEEDS = [84810, 15592, 4278, 98196, 37048, 33098, 30256, 19289, 97530, 14434]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-seed TrajectoryCache benchmark")
    p.add_argument("--config", type=Path, default=Path("configs/simulation.yaml"))
    p.add_argument("--output", type=Path, default=Path("experiments/results"))
    p.add_argument("--zipf-alpha", type=float, default=None)
    p.add_argument("--seeds", type=int, nargs="+", default=PAPER_SEEDS)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(level="WARNING")

    cfg = load_config(args.config)
    if args.zipf_alpha is not None:
        cfg.zipf_alpha = args.zipf_alpha

    print(f"\n{'='*70}")
    print(f"Multi-seed benchmark | alpha={cfg.zipf_alpha} | seeds={args.seeds}")
    print(f"{'='*70}\n")

    # Accumulate per-seed miss rates for each policy
    # We use the class names as they come out of the metrics
    class_names = {"trajectory": "TrajectoryCache", "lfu": "LFU", "lru": "LRU", "random": "Random", "fifo": "FIFO"}
    all_miss: dict[str, list[float]] = {class_names[name]: [] for name, _ in DEFAULT_POLICIES}

    for i, seed in enumerate(args.seeds):
        cfg.seed = seed
        print(f"Seed {i+1}/{len(args.seeds)}: {seed}", end="  ", flush=True)
        results = run_benchmark(config=cfg, verbose=args.verbose, output_dir=None)
        for name, metrics in results.items():
            if name in all_miss:
                all_miss[name].append(metrics.miss_rate * 100.0)
        # Print quick summary for this seed
        tc_miss = results["TrajectoryCache"].miss_rate * 100.0 if "TrajectoryCache" in results else 0.0
        lfu_miss = results["LFU"].miss_rate * 100.0 if "LFU" in results else 0.0
        print(f"TC={tc_miss:.2f}%  LFU={lfu_miss:.2f}%")

    # Final table
    print(f"\n{'='*70}")
    print(f"RESULTS: alpha={cfg.zipf_alpha}  (mean ± std over {len(args.seeds)} seeds)")
    print(f"{'='*70}")
    print(f"{'Policy':<18} {'Mean Miss%':>11} {'Std Miss%':>10} {'Min':>8} {'Max':>8}")
    print("-" * 60)

    summary = {}
    for short_name, _ in DEFAULT_POLICIES:
        name = class_names[short_name]
        vals = np.array(all_miss[name])
        mean_v = float(np.mean(vals))
        std_v  = float(np.std(vals))
        min_v  = float(np.min(vals))
        max_v  = float(np.max(vals))
        display = "TrajectoryCache" if name == "trajectory" else name.upper()
        print(f"{display:<18} {mean_v:>10.2f}%  {std_v:>8.2f}%  {min_v:>7.2f}%  {max_v:>7.2f}%")
        summary[name] = {
            "miss_rate_mean": round(mean_v, 4),
            "miss_rate_std":  round(std_v, 4),
            "miss_rate_min":  round(min_v, 4),
            "miss_rate_max":  round(max_v, 4),
            "per_seed":       [round(v, 4) for v in all_miss[name]],
            "seeds":          list(args.seeds),
        }
    print(f"{'='*70}\n")

    # Save
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    fname = out / f"multiseed_alpha{cfg.zipf_alpha:.1f}.json"
    with open(fname, "w") as f:
        json.dump({"zipf_alpha": cfg.zipf_alpha, "seeds": list(args.seeds), "results": summary}, f, indent=2)
    print(f"Saved to {fname}")


if __name__ == "__main__":
    main()
