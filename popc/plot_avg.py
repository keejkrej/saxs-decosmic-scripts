from pathlib import Path
import fabio
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "."
OUTPUT_DIR = "plot"
MEASUREMENT = "popc"
VARIANTS = ["avg_direct", "avg_half_clean", "avg_clean"]
VMIN = 0
VMAX = 2e-2
CMAP = "hot"

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load images
images = {}
for variant in VARIANTS:
    file_path = input_path / MEASUREMENT / "processed" / f"{MEASUREMENT}_{variant}.tif"
    images[variant] = fabio.open(str(file_path)).data

def plot_avg(image: np.ndarray, output_file: str) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(image, cmap=CMAP, vmin=VMIN, vmax=VMAX)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Create subfolder for individual plots
avg_output_path = output_path / "avg"
avg_output_path.mkdir(parents=True, exist_ok=True)

# Plotting
for i in range(3):
    filename = f"popc_{VARIANTS[i]}.pdf"
    plot_avg(images[VARIANTS[i]], avg_output_path / filename)
