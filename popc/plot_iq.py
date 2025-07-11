import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
import pandas as pd
import numpy as np
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "iq"
OUTPUT_DIR = "plot"
VARIANTS = ['direct', 'half_clean', 'clean']
SCALES = [1e4, 1e2, 1.]
MARKERS = ['o', 's', '^']
COLORS = ['red', 'blue', 'black']

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_iq_result_avg(name: str) -> dict[str, pd.DataFrame]:
    """Load I(q) average CSVs for a given measurement."""
    return {variant: pd.read_csv(input_path / f"{name}_avg_{variant}.csv") for variant in VARIANTS}

def load_iq_fit(name: str) -> pd.DataFrame:
    """Load I(q) fit CSV for subtracted clean variant."""
    return np.loadtxt(input_path / f"fit.txt", skiprows=1)

# Plotting
def plot_iq_errbar(ax: Axes, iq_result: dict[str, pd.DataFrame], scale: list[float] | None = None) -> None:
    """Plot I(q) with error bars for all variants on the given axis."""
    if scale is None:
        scale = [1.] * len(VARIANTS)
    for i, (label, marker, color) in enumerate(zip(VARIANTS, MARKERS, COLORS)):
        df = iq_result[label]
        yerr = df['sigma'] if 'sigma' in df else None
        ax.errorbar(
            df['q'], df['intensity'] * scale[i], yerr=yerr * scale[i] if yerr is not None else None,
            fmt=marker, label=label.replace('_', ' '), alpha=0.8, markersize=6, capsize=2, color=color,
            uplims=False, lolims=True, linestyle='none', markerfacecolor='none'
        )
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')
    ax.set_yscale('log')

def plot_iq_scatter(ax: Axes, iq_result: dict[str, pd.DataFrame], scale: list[float] | None = None) -> None:
    """Scatter plot I(q) for all variants on the given axis (no error bars)."""
    if scale is None:
        scale = [1.] * len(VARIANTS)
    for i, (label, marker, color) in enumerate(zip(VARIANTS, MARKERS, COLORS)):
        df = iq_result[label]
        ax.scatter(
            df['q'], df['intensity'] * scale[i],
            marker=marker, label=label.replace('_', ' '), alpha=0.8, s=30, color=color, facecolors='none'
        )
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')
    ax.set_yscale('log')

# Main script
popc_iq_result_avg = load_iq_result_avg("popc")
water_iq_result_avg = load_iq_result_avg("water")
empty_iq_result_avg = load_iq_result_avg("empty")
final_iq_result_avg = load_iq_result_avg("final")
final_iq_fit = load_iq_fit("final")

# POPC solution
fig, ax = plt.subplots(figsize=(6, 4))
plot_iq_scatter(ax, popc_iq_result_avg)
ax.set_xlim(0.05, 0.5)
ax.set_ylim(3.0e-3, 1.2e-2)
ax.set_title('POPC solution')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig(output_path / "iq_popc_solution.pdf")
plt.close(fig)

# Pure water
fig, ax = plt.subplots(figsize=(6, 4))
plot_iq_scatter(ax, water_iq_result_avg)
ax.set_xlim(0.05, 0.5)
ax.set_ylim(3.0e-3, 1.2e-2)
ax.set_title('Pure water')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig(output_path / "iq_pure_water.pdf")
plt.close(fig)

# Empty cell
fig, ax = plt.subplots(figsize=(6, 4))
plot_iq_scatter(ax, empty_iq_result_avg)
ax.set_xlim(0.05, 0.5)
ax.set_ylim(1e-3, 1e-2)
ax.set_title('Empty cell')
ax.axhline(y=3.0e-3, color='red', linestyle='--', label='3.0e-3')
ax.axhline(y=2.5e-3, color='blue', linestyle='--', label='2.5e-3')
ax.axhline(y=1.4e-3, color='black', linestyle='--', label='1.4e-3')
ax.legend(loc='upper right', ncol=2)

plt.tight_layout()
plt.savefig(output_path / "iq_empty_cell.pdf")
plt.close(fig)

# POPC subtracted
fig, ax = plt.subplots(figsize=(6, 4))
plot_iq_errbar(ax, final_iq_result_avg, SCALES)
ax.plot(final_iq_fit[:, 0], final_iq_fit[:, 1], color='black', label='Fit')
ax.set_xlim(0.05, 0.5)
ax.set_ylim(1e-7, 1e3)
ax.set_title('POPC subtracted')
ax.axhline(y=1.0e-4, color='black', linestyle='--', label='1.0e-4')
ax.axhline(y=1.0e-5, color='black', linestyle='-.', label='1.0e-5')
ax.legend(loc='upper right', ncol=2)

plt.tight_layout()
plt.savefig(output_path / "iq_popc_subtracted.pdf")
plt.close(fig)
