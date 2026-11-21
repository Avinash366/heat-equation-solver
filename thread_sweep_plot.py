"""Plot speedup vs. thread count from benchmarks_<t>threads.csv files.

Run after the thread sweep:
    python thread_sweep_plot.py
Saves thread_scaling.png and thread_scaling.csv, and prints a summary table.
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

THREADS = [1, 2, 4, 8]
VERSIONS = {
    "heat_openmp": ("OpenMP", "#9CC1E8"),
    "heat_threads": ("C++ threads", "#2F6DB5"),
    "heat_optimized": ("Flat-array OpenMP", "#D9622B"),
}
here = Path(__file__).parent

# times[(version, grid)][threads] = average ms
times = {}
for t in THREADS:
    path = here / f"benchmarks_{t}threads.csv"
    if not path.exists():
        raise SystemExit(f"Missing {path.name}: run the thread sweep first.")
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            times.setdefault((row["version"], int(row["grid_size"])), {})[t] = float(row["average_ms"])

grids = sorted({g for _, g in times})
# Sequential baseline: average of its runs across all four sweeps.
baseline = {g: sum(times[("heat_sequential", g)].values()) / len(THREADS) for g in grids}

fig, axes = plt.subplots(1, len(grids), figsize=(15, 4.8), sharey=True)
rows = []
for ax, g in zip(axes, grids):
    for version, (label, color) in VERSIONS.items():
        speedups = [baseline[g] / times[(version, g)][t] for t in THREADS]
        ax.plot(THREADS, speedups, marker="o", linewidth=2.5, color=color, label=label)
        for t, s in zip(THREADS, speedups):
            rows.append({"grid_size": g, "version": label, "threads": t,
                         "average_ms": times[(version, g)][t], "speedup": round(s, 2)})
    ax.plot(THREADS, THREADS, linestyle=":", color="#9AA1AD", label="Ideal (linear)")
    ax.axhline(1.0, linestyle="--", color="#1B2333", linewidth=1)
    ax.set_title(f"{g} × {g}")
    ax.set_xlabel("Threads")
    ax.set_xticks(THREADS)
    ax.set_ylim(0, 8.5)
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Speedup over sequential")
axes[-1].legend(loc="upper left")
fig.suptitle("Speedup vs. Thread Count (Release build, 100 steps)")
fig.tight_layout()
fig.savefig(here / "thread_scaling.png", dpi=150)

with open(here / "thread_scaling.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"{'grid':>6} {'version':<18}" + "".join(f"{t:>8}T" for t in THREADS))
for g in grids:
    for version, (label, _) in VERSIONS.items():
        line = "".join(f"{baseline[g] / times[(version, g)][t]:>8.2f}x" for t in THREADS)
        print(f"{g:>6} {label:<18}{line}")
print("Saved thread_scaling.png and thread_scaling.csv")
