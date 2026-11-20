import matplotlib.pyplot as plt
import numpy as np


implementations = [
    "Sequential",
    "OpenMP",
    "C++ Threads",
    "Cache-aware\nOpenMP",
]
measurements_ms = [
    [99.86, 112.47, 106.07],
    [66.46, 73.31, 70.91],
    [157.95, 139.00, 140.38],
    [70.76, 60.40, 65.17],
]

averages_ms = [sum(values) / len(values) for values in measurements_ms]
standard_deviations_ms = [
    float(np.std(values, ddof=1)) for values in measurements_ms
]

figure, axis = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
positions = np.arange(len(implementations))
bars = axis.bar(
    positions,
    averages_ms,
    yerr=standard_deviations_ms,
    capsize=6,
    color=["#4C78A8", "#72B7B2", "#ECA82C", "#F58518"],
)

axis.bar_label(bars, labels=[f"{value:.1f} ms" for value in averages_ms], padding=5)
axis.set_title("Release Runtime Comparison (1000 × 1000, 100 steps)")
axis.set_ylabel("Average runtime (milliseconds; 3 runs)")
axis.set_xticks(positions, implementations)
axis.set_ylim(0, 190)
axis.grid(axis="y", alpha=0.25)
axis.set_axisbelow(True)
axis.text(
    0.99,
    0.98,
    "Error bars show ±1 sample standard deviation",
    transform=axis.transAxes,
    ha="right",
    va="top",
    fontsize=9,
)

figure.savefig("release_benchmark_comparison.png", dpi=180)
