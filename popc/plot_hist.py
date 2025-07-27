import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
import pandas as pd
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "hist"
OUTPUT_DIR = "plot"
VARIANTS = [
    'avg_direct', 'avg_half_clean', 'avg_clean',
    'var_direct', 'var_half_clean', 'var_clean'
]
COLORS = ['blue', 'blue', 'blue', 'red', 'red', 'red']
XMIN = 0
XMAX = 0.05

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_hist_result(name: str, variant: str) -> pd.DataFrame:
    """Load histogram CSV for a given measurement and variant."""
    return pd.read_csv(input_path / f"{name}_{variant}.csv")

# Plotting
def plot_hist(hist_data: pd.DataFrame, color: str, ax: Axes, label: str) -> None:
    """Plot histogram as a bar plot."""
    width = hist_data['bins'][1] - hist_data['bins'][0]
    ax.bar(
        hist_data['bins'], hist_data['hist'], width=width,
        color=color, align='edge', edgecolor='black', alpha=0.5, label=label
    )
    ax.set_xlabel('Intensity [a.u.]')
    ax.set_ylabel('Count')
    ax.set_yscale('log')
    ax.legend(loc='upper right')
    ax.set_xlim(XMIN, XMAX)

# Main script
popc_hist_results = {variant: load_hist_result("popc", variant) for variant in VARIANTS}

# Create subfolder for individual plots
hist_output_path = output_path / "hist"
hist_output_path.mkdir(parents=True, exist_ok=True)

# Create three plots: ad, be, cf - each with mean and variance variants
fig, axes = plt.subplots(2, 1, figsize=(4, 4))
plot_hist(popc_hist_results[VARIANTS[0]], COLORS[0], axes[0], "mean")
plot_hist(popc_hist_results[VARIANTS[3]], COLORS[3], axes[1], "variance")
fig.tight_layout()
fig.savefig(hist_output_path / "hist_popc_direct.pdf")
plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(4, 4))
plot_hist(popc_hist_results[VARIANTS[1]], COLORS[1], axes[0], "mean")
plot_hist(popc_hist_results[VARIANTS[4]], COLORS[4], axes[1], "variance")
fig.tight_layout()
fig.savefig(hist_output_path / "hist_popc_half_clean.pdf")
plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(4, 4))
plot_hist(popc_hist_results[VARIANTS[2]], COLORS[2], axes[0], "mean")
plot_hist(popc_hist_results[VARIANTS[5]], COLORS[5], axes[1], "variance")
fig.tight_layout()
fig.savefig(hist_output_path / "hist_popc_clean.pdf")
plt.close(fig)