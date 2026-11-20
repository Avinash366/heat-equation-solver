import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


data_path = Path("release_benchmarks.csv")
with data_path.open("r", newline="") as csv_file:
    rows = list(csv.DictReader(csv_file))

grid_size = 1000
selected = [row for row in rows if int(row["grid_size"]) == grid_size]
labels = {
    "heat_sequential": "Sequential",
    "heat_openmp": "OpenMP (8 threads)",
    "heat_threads": "C++ threads (8)",
    "heat_optimized": "Flat-array OpenMP (8)",
}
order = list(labels)
selected_by_version = {row["version"]: row for row in selected}
missing = [version for version in order if version not in selected_by_version]
if missing:
    raise ValueError(f"Missing benchmark results for: {', '.join(missing)}")

averages_ms = [float(selected_by_version[version]["average_ms"]) for version in order]
colors = ["#4C78A8", "#72B7B2", "#ECA82C", "#F58518"]
figure, axis = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
positions = np.arange(len(order))
bars = axis.bar(positions, averages_ms, color=colors)
axis.bar_label(bars, labels=[f"{value:.2f} ms" for value in averages_ms], padding=5)
axis.set_title("Release Runtime Comparison (1000 × 1000, 100 steps)")
axis.set_ylabel("Average runtime (milliseconds; 3 runs)")
axis.set_xticks(positions, [labels[version] for version in order])
axis.set_ylim(0, max(averages_ms) * 1.25)
axis.grid(axis="y", alpha=0.25)
axis.set_axisbelow(True)
axis.text(
    0.99,
    0.98,
    "Times measured on this Windows computer",
    transform=axis.transAxes,
    ha="right",
    va="top",
    fontsize=9,
)
figure.savefig("release_benchmark_comparison.png", dpi=180)
