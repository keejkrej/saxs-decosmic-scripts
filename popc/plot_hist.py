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
TITLES = [
    '(a) POPC Mean Direct', '(b) POPC Mean Half Clean', '(c) POPC Mean Clean',
    '(d) POPC Variance Direct', '(e) POPC Variance Half Clean', '(f) POPC Variance Clean'
]
COLORS = ['blue', 'red', 'green', 'blue', 'red', 'green']
XMIN = -0.01
XMAX = 0.05

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_hist_result(name: str, variant: str) -> pd.DataFrame:
    """Load histogram CSV for a given measurement and variant."""
    return pd.read_csv(input_path / f"{name}_{variant}.csv")

# Plotting
def plot_hist(hist_data: pd.DataFrame, color: str, title: str, output_file: str) -> None:
    """Plot histogram as a bar plot and save to file."""
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(hist_data['bins']) > 1:
        width = hist_data['bins'][1] - hist_data['bins'][0]
    else:
        width = 0.001  # fallback width
    ax.bar(
        hist_data['bins'], hist_data['hist'], width=width,
        color=color, align='edge', edgecolor='black', alpha=0.8
    )
    ax.set_xlabel('Intensity [a.u.]')
    ax.set_ylabel('Count')
    ax.set_yscale('log')
    ax.set_title(title)
    ax.set_xlim(XMIN, XMAX)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Main script
popc_hist_results = {variant: load_hist_result("popc", variant) for variant in VARIANTS}

# Create subfolder for individual plots
hist_output_path = output_path / "hist"
hist_output_path.mkdir(parents=True, exist_ok=True)

for i in range(6):
    filename = f"hist_{VARIANTS[i]}.pdf"
    plot_hist(popc_hist_results[VARIANTS[i]], COLORS[i], TITLES[i], hist_output_path / filename)