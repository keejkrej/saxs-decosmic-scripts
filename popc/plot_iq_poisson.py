import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
import pandas as pd
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "iq"
OUTPUT_DIR = "plot"
VARIANTS = ['direct', 'half_clean', 'clean']
COLORS = ['red', 'blue']
TITLES = [
    '(a) POPC Direct',
    '(b) POPC Half Clean',
    '(c) POPC Clean'
]

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_iq_result(name: str, prefix: str) -> dict[str, pd.DataFrame]:
    """Load I(q) CSVs for a given measurement and prefix (avg/var)."""
    return {variant: pd.read_csv(input_path / f"{name}_{prefix}_{variant}.csv") for variant in VARIANTS}

# Plotting
def plot_iq(iq_result_1: pd.DataFrame, iq_result_2: pd.DataFrame, title: str, output_file: str, xlim: tuple = None, ylim: tuple = None) -> None:
    """Plot two I(q) curves and save to file."""
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.plot(iq_result_1['q'], iq_result_1['intensity'], label="mean", color=COLORS[0])
    ax.plot(iq_result_2['q'], iq_result_2['intensity'], label="variance", color=COLORS[1])
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')
    ax.set_yscale('log')
    ax.set_title(title)
    ax.legend(loc='upper right')
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Main script
popc_iq_result_avg = load_iq_result("popc", "avg")
popc_iq_result_var = load_iq_result("popc", "var")
water_iq_result_avg = load_iq_result("water", "avg")
water_iq_result_var = load_iq_result("water", "var")
final_iq_result_avg = load_iq_result("final", "avg")
final_iq_result_var = load_iq_result("final", "var")

# Create subfolder for individual plots
iq_poisson_output_path = output_path / "iq_poisson"
iq_poisson_output_path.mkdir(parents=True, exist_ok=True)

# Plot each variant separately
xlims = [(0.05, 0.5), (0.05, 0.5), (0.05, 0.5)]
ylims = [(3e-3, 5e-2), (4e-3, 1.2e-2), (3e-3, 1e-2)]

for i in range(3):
    filename = f"popc_iq_poisson_{VARIANTS[i]}.pdf"
    plot_iq(popc_iq_result_avg[VARIANTS[i]], popc_iq_result_var[VARIANTS[i]], 
            TITLES[i], iq_poisson_output_path / filename, xlims[i], ylims[i])
