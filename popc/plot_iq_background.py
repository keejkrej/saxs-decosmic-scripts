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

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Data loading
def load_iq_result_bg(name: str) -> dict[str, pd.DataFrame]:
    """Load I(q) background CSVs for a given measurement."""
    return {variant: pd.read_csv(input_path / f"{name}_avg_{variant}.csv") for variant in VARIANTS}

# Plotting
def plot_iq_bg(iq_result: dict[str, pd.DataFrame], measurement: str, colors: list[str], ax: Axes) -> None:
    """Plot I(q) background for all variants and save to file."""
    for i, variant in enumerate(VARIANTS):
        ax.plot(
            iq_result[variant]['q'], iq_result[variant]['intensity'],
            label=f"{variant}, {measurement}", color=colors[i]
        )
    ax.set_xlabel('q [A$^{-1}$]')
    ax.set_ylabel('Intensity [a.u.]')

# Main script
popc_iq_result_decosmic = load_iq_result_bg("popc")
water_iq_result_decosmic = load_iq_result_bg("water")
final_iq_result_decosmic = load_iq_result_bg("final")
final_donut_std = final_iq_result_decosmic['donut']['intensity'].std()
final_streak_std = final_iq_result_decosmic['streak']['intensity'].std()

# Create subfolder for individual plots
iq_bg_output_path = output_path / "iq_background"
iq_bg_output_path.mkdir(parents=True, exist_ok=True)

# (a) POPC and water backgrounds
fig, ax = plt.subplots(figsize=(4, 4))
plot_iq_bg(popc_iq_result_decosmic, 'popc solution', ['red', 'blue'], ax)
plot_iq_bg(water_iq_result_decosmic, 'pure water', ['orange', 'violet'], ax)
ax.set_xlim(0.05, 0.5)
ax.set_ylim(0, 2e-3)
ax.set_yticks([0, 5e-4, 1e-3, 1.5e-3, 2e-3])
ax.legend(loc='upper right')
plt.tight_layout()
plt.savefig(iq_bg_output_path / "iq_background.pdf")
plt.close(fig)

# (b) Subtracted backgrounds
fig, ax = plt.subplots(figsize=(4, 4))
plot_iq_bg(final_iq_result_decosmic, 'popc subtracted', ['red', 'blue'], ax)
ax.set_xlim(0.05, 0.5)
ax.set_ylim(-5e-4, 5e-4)
ax.set_yticks([-5e-4, 0, 5e-4])
ax.legend([f'donut, std = {final_donut_std:.2e}', f'streak, std = {final_streak_std:.2e}'])
plt.tight_layout()
plt.savefig(iq_bg_output_path / "iq_background_subtracted.pdf")
plt.close(fig)
