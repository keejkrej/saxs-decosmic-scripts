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
VARIANTS = ["avg_direct", "avg_half_clean", "avg_clean"]
TITLES = [
    '(a) POPC Direct',
    '(b) POPC Half Clean',
    '(c) POPC Clean'
]
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

def plot_avg(ax: Axes, image: np.ndarray, title: str) -> None:
    ax.imshow(image, cmap=CMAP, vmin=VMIN, vmax=VMAX)
    ax.set_title(title)
    ax.axis("off")

# Plotting
fig, axes = plt.subplots(1, 3, figsize=(10, 4))
for i in range(3):
    plot_avg(axes[i], images[VARIANTS[i]], TITLES[i])

plt.tight_layout()
plt.savefig(output_path / "popc_avg.pdf")
plt.close()
