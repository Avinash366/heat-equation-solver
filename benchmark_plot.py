import matplotlib.pyplot as plt
import numpy as np


grid_sizes = ["500 × 500", "1000 × 1000", "1500 × 1500"]
original_openmp_ms = [153.15, 618.65, 1388.46]
cpp_threads_ms = [367.89, 624.93, 1528.57]
cache_aware_openmp_ms = [95.65, 327.50, 712.69]

positions = np.arange(len(grid_sizes))
bar_width = 0.25

figure, axis = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
original_bars = axis.bar(
    positions - bar_width,
    original_openmp_ms,
    bar_width,
    label="Original OpenMP",
    color="#4C78A8",
)
threads_bars = axis.bar(
    positions,
    cpp_threads_ms,
    bar_width,
    label="C++ Threads",
    color="#72B7B2",
)
optimized_bars = axis.bar(
    positions + bar_width,
    cache_aware_openmp_ms,
    bar_width,
    label="Cache-aware OpenMP",
    color="#F58518",
)

axis.bar_label(original_bars, fmt="%.0f ms", padding=3, fontsize=9)
axis.bar_label(threads_bars, fmt="%.0f ms", padding=3, fontsize=9)
axis.bar_label(optimized_bars, fmt="%.0f ms", padding=3, fontsize=9)

axis.set_title("Runtime by Grid Size (8 threads, 100 time steps)")
axis.set_xlabel("Grid size")
axis.set_ylabel("Average runtime (milliseconds; 3 runs)")
axis.set_xticks(positions, grid_sizes)
axis.set_ylim(0, max(original_openmp_ms) * 1.2)
axis.grid(axis="y", alpha=0.25)
axis.set_axisbelow(True)
axis.legend(frameon=False)

figure.savefig("benchmark_comparison.png", dpi=180)
