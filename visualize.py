import csv
from pathlib import Path

import matplotlib.pyplot as plt


data_path = Path("heat_output.csv")
image_path = Path("heatmap.png")

with data_path.open("r", newline="") as csv_file:
    temperatures = [
        [float(value) for value in row]
        for row in csv.reader(csv_file)
        if row
    ]

if not temperatures:
    raise ValueError(f"No temperature data found in {data_path}")

row_width = len(temperatures[0])
if any(len(row) != row_width for row in temperatures):
    raise ValueError("The CSV rows do not all have the same number of values")

minimum_temperature = min(min(row) for row in temperatures)
maximum_temperature = max(max(row) for row in temperatures)

figure, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
axes[0].imshow(
    temperatures,
    cmap="inferno",
    origin="lower",
    interpolation="nearest",
    vmin=minimum_temperature,
    vmax=maximum_temperature,
)
axes[0].set_title("Full 1000 × 1000 Grid")
axes[0].set_xlabel("Grid column")
axes[0].set_ylabel("Grid row")

center_row = len(temperatures) // 2
center_col = row_width // 2
zoom_radius = 60
zoomed_temperatures = [
    row[max(0, center_col - zoom_radius):center_col + zoom_radius]
    for row in temperatures[
        max(0, center_row - zoom_radius):center_row + zoom_radius
    ]
]

zoom_heatmap = axes[1].imshow(
    zoomed_temperatures,
    cmap="inferno",
    origin="lower",
    interpolation="nearest",
    vmin=minimum_temperature,
    vmax=maximum_temperature,
    extent=(center_col - zoom_radius, center_col + zoom_radius,
            center_row - zoom_radius, center_row + zoom_radius),
)
axes[1].set_title("Center Region (120 × 120 Cells)")
axes[1].set_xlabel("Grid column")
axes[1].set_ylabel("Grid row")

figure.colorbar(zoom_heatmap, ax=axes, label="Temperature (degrees)")
figure.suptitle("Heat Diffusion After 100 Time Steps")
figure.savefig(image_path, dpi=160)

print(f"Saved heatmap to {image_path.resolve()}")
