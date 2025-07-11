from pathlib import Path
import fabio
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "."
OUTPUT_DIR = "plot"
MEASUREMENT = "popc"
VARIANTS = ["avg_donut", "avg_streak"]
TITLES = [
    '(a) POPC Donut',
    '(b) POPC Streak'
]
VMIN = 0
VMAX = 1e-2
CMAP = "hot"

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load images
images = {}
for variant in VARIANTS:
    file_path = input_path / MEASUREMENT / "processed" / f"{MEASUREMENT}_{variant}.tif"
    images[variant] = fabio.open(str(file_path)).data

# Plotting
def plot_avg_background(ax: Axes, image: np.ndarray, title: str) -> None:
    ax.imshow(image, cmap=CMAP, vmin=VMIN, vmax=VMAX)
    ax.set_title(title)
    ax.axis("off")

fig, axes = plt.subplots(1, 2, figsize=(6, 4))
for i in range(2):
    plot_avg_background(axes[i], images[VARIANTS[i]], TITLES[i])

plt.tight_layout()
plt.savefig(output_path / "popc_avg_background.pdf")
plt.close() 