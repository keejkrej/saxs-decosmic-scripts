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
def plot_avg_background(image: np.ndarray, output_file: str) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(image, cmap=CMAP, vmin=VMIN, vmax=VMAX)

    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Create subfolder for individual plots
background_output_path = output_path / "avg_background"
background_output_path.mkdir(parents=True, exist_ok=True)

for i in range(2):
    filename = f"popc_{VARIANTS[i]}.pdf"
    plot_avg_background(images[VARIANTS[i]], background_output_path / filename) 