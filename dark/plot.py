from pathlib import Path
import matplotlib.pyplot as plt
import tifffile
from plot_style import apply_style

apply_style()

# Constants
FIG_SIZE = (12, 8)
V_MIN = [0, 0, 0, 0, 0]
V_MAX = [0.02, 5, 5, 1, 1]
PROCESSED_DIR = "processed"
SAVE_DIR = "plot"
CMAP = "hot"

# Resolve paths
processed_path = Path(PROCESSED_DIR).resolve()
save_path = Path(SAVE_DIR).resolve()
save_path.mkdir(parents=True, exist_ok=True)

# Load images and masks
img_avg = tifffile.imread(processed_path / "dark_avg.tif")
img_donut = tifffile.imread(processed_path / "donut.tif")
img_streak = tifffile.imread(processed_path / "streak.tif")
mask_donut = tifffile.imread(processed_path / "donut_mask.tif").astype(bool)
mask_streak = tifffile.imread(processed_path / "streak_mask.tif").astype(bool)

# Create individual plots for each image/mask

# Dark Average plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(img_avg, cmap=CMAP, vmin=V_MIN[0], vmax=V_MAX[0])
ax.axis('off')
fig.tight_layout()
fig.savefig(save_path / "dark_average.pdf")
plt.close(fig)

# Donut plot
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(img_donut, cmap=CMAP, vmin=V_MIN[1], vmax=V_MAX[1])
ax.axis('off')
fig.tight_layout()
fig.savefig(save_path / "donut.pdf")
plt.close(fig)

# Streak plot
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(img_streak, cmap=CMAP, vmin=V_MIN[2], vmax=V_MAX[2])
ax.axis('off')
fig.tight_layout()
fig.savefig(save_path / "streak.pdf")
plt.close(fig)

# Donut Mask plot
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(mask_donut, cmap=CMAP, vmin=V_MIN[3], vmax=V_MAX[3])
ax.axis('off')
fig.tight_layout()
fig.savefig(save_path / "donut_mask.pdf")
plt.close(fig)

# Streak Mask plot
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(mask_streak, cmap=CMAP, vmin=V_MIN[4], vmax=V_MAX[4])
ax.axis('off')
fig.tight_layout()
fig.savefig(save_path / "streak_mask.pdf")
plt.close(fig) 