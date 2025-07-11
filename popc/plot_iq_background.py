import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
import pandas as pd
from plot_style import apply_style

apply_style()

# Constants
INPUT_DIR = "iq"
OUTPUT_DIR = "plot"
VARIANTS = ['donut', 'streak']
TITLES = [
    '(a) Solution and solvent',
    '(b) Subtracted'
]

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_iq_result_bg(name: str) -> dict[str, pd.DataFrame]:
    """Load I(q) background CSVs for a given measurement."""
    return {variant: pd.read_csv(input_path / f"{name}_avg_{variant}.csv") for variant in VARIANTS}

# Plotting
def plot_iq_bg(ax: Axes, iq_result: dict[str, pd.DataFrame], measurement: str, colors: list[str], title: str) -> None:
    """Plot I(q) background for all variants on the given axis."""
    for i, variant in enumerate(VARIANTS):
        ax.plot(
            iq_result[variant]['q'], iq_result[variant]['intensity'],
            label=f"{variant}, {measurement}", color=colors[i]
        )
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')
    ax.set_title(title)

# Main script
popc_iq_result_decosmic = load_iq_result_bg("popc")
water_iq_result_decosmic = load_iq_result_bg("water")
final_iq_result_decosmic = load_iq_result_bg("final")
final_donut_std = final_iq_result_decosmic['donut']['intensity'].std()
final_streak_std = final_iq_result_decosmic['streak']['intensity'].std()

# (a) and (b) as subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# (a) POPC and water backgrounds
plot_iq_bg(axes[0], popc_iq_result_decosmic, 'popc solution', ['red', 'blue'], TITLES[0])
plot_iq_bg(axes[0], water_iq_result_decosmic, 'pure water', ['orange', 'violet'], TITLES[0])
axes[0].set_xlim(0.05, 0.5)
axes[0].set_ylim(0, 2e-3)
axes[0].set_yticks([0, 5e-4, 1e-3, 1.5e-3, 2e-3])
axes[0].legend(loc='upper right')

# (b) Subtracted backgrounds
plot_iq_bg(axes[1], final_iq_result_decosmic, 'popc subtracted', ['red', 'blue'], TITLES[1])
axes[1].set_xlim(0.05, 0.5)
axes[1].set_ylim(-5e-4, 5e-4)
axes[1].set_yticks([-5e-4, 0, 5e-4])
axes[1].legend(loc='upper right')
axes[1].legend([f'donut, std = {final_donut_std:.2e}', f'streak, std = {final_streak_std:.2e}'])

plt.tight_layout()
plt.savefig(output_path / "iq_background.pdf")
plt.close(fig)
