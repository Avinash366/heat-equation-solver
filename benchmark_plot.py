import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


with Path("release_benchmarks.csv").open("r", newline="") as csv_file:
    rows = list(csv.DictReader(csv_file))

grid_sizes = sorted({int(row["grid_size"]) for row in rows})
versions = [
    ("heat_sequential", "Sequential", "#4C78A8"),
    ("heat_openmp", "OpenMP", "#72B7B2"),
    ("heat_threads", "C++ threads", "#ECA82C"),
    ("heat_optimized", "Flat-array OpenMP", "#F58518"),
]
values = {
    (int(row["grid_size"]), row["version"]): float(row["average_ms"])
    for row in rows
}
missing = [
    (grid, key)
    for grid in grid_sizes
    for key, _, _ in versions
    if (grid, key) not in values
]
if missing:
    raise ValueError(f"Benchmark data is incomplete: {missing}")

positions = np.arange(len(grid_sizes))
bar_width = 0.19
figure, axis = plt.subplots(figsize=(11, 6), constrained_layout=True)
for index, (key, label, color) in enumerate(versions):
    offset = (index - (len(versions) - 1) / 2) * bar_width
    measurements = [values[(grid, key)] for grid in grid_sizes]
    bars = axis.bar(positions + offset, measurements, bar_width, label=label, color=color)
    axis.bar_label(bars, fmt="%.1f", padding=2, fontsize=8, rotation=90)

axis.set_title("Release Runtime by Grid Size (100 time steps)")
axis.set_xlabel("Grid size")
axis.set_ylabel("Average runtime (milliseconds; 3 runs)")
axis.set_xticks(positions, [f"{grid} × {grid}" for grid in grid_sizes])
axis.grid(axis="y", alpha=0.25)
axis.set_axisbelow(True)
axis.legend(frameon=False, ncols=2)
figure.savefig("benchmark_comparison.png", dpi=180)
