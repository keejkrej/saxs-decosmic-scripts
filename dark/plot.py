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

# Create subplots with a larger first subplot
fig = plt.figure(figsize=FIG_SIZE)
gs = fig.add_gridspec(2, 3, width_ratios=[2, 1, 1], height_ratios=[1, 1])

# Larger subplot for dark average (combines axes[0] and axes[3])
ax0 = fig.add_subplot(gs[0:2, 0])
ax0.imshow(img_avg, cmap=CMAP, vmin=V_MIN[0], vmax=V_MAX[0])
ax0.set_title("a) Dark Average")
ax0.axis('off')

# Other subplots
ax1 = fig.add_subplot(gs[0, 1])
ax1.imshow(img_donut, cmap=CMAP, vmin=V_MIN[1], vmax=V_MAX[1])
ax1.set_title("b) Donut")
ax1.axis('off')

ax2 = fig.add_subplot(gs[0, 2])
ax2.imshow(img_streak, cmap=CMAP, vmin=V_MIN[2], vmax=V_MAX[2])
ax2.set_title("c) Streak")
ax2.axis('off')

ax4 = fig.add_subplot(gs[1, 1])
ax4.imshow(mask_donut, cmap=CMAP, vmin=V_MIN[3], vmax=V_MAX[3])
ax4.set_title("d) Donut Mask")
ax4.axis('off')

ax5 = fig.add_subplot(gs[1, 2])
ax5.imshow(mask_streak, cmap=CMAP, vmin=V_MIN[4], vmax=V_MAX[4])
ax5.set_title("e) Streak Mask")
ax5.axis('off')

# Adjust layout and save
fig.tight_layout()
fig.savefig(save_path / "dark.pdf")
plt.close(fig) 