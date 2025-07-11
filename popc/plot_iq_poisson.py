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
def plot_iq(ax: Axes, iq_result_1: pd.DataFrame, iq_result_2: pd.DataFrame) -> None:
    """Plot two I(q) curves on the same axis."""
    ax.plot(iq_result_1['q'], iq_result_1['intensity'], label="mean", color=COLORS[0])
    ax.plot(iq_result_2['q'], iq_result_2['intensity'], label="variance", color=COLORS[1])
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')
    ax.set_yscale('log')

# Main script
popc_iq_result_avg = load_iq_result("popc", "avg")
popc_iq_result_var = load_iq_result("popc", "var")
water_iq_result_avg = load_iq_result("water", "avg")
water_iq_result_var = load_iq_result("water", "var")
final_iq_result_avg = load_iq_result("final", "avg")
final_iq_result_var = load_iq_result("final", "var")

fig, axes = plt.subplots(1, 3, figsize=(10, 4))
axes = axes.flatten()

for i in range(3):
    plot_iq(axes[i], popc_iq_result_avg[VARIANTS[i]], popc_iq_result_var[VARIANTS[i]])
    axes[i].set_title(TITLES[i])
    axes[i].legend(loc='upper right')

axes[0].set_xlim(0.05, 0.5)
axes[0].set_ylim(3e-3, 5e-2)
axes[1].set_xlim(0.05, 0.5)
axes[1].set_ylim(4e-3, 1.2e-2)
axes[2].set_xlim(0.05, 0.5)
axes[2].set_ylim(3e-3, 1e-2)

plt.tight_layout()
plt.savefig(output_path / "iq_poisson.pdf")
plt.close(fig)
