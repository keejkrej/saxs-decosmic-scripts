import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from plot_style import apply_style

apply_style()

INPUT_DIR = "iq"
OUTPUT_DIR = "plot"

MEASUREMENTS = ["20", "40", "60", "80", "100"]
VARIANTS = ["avg_clean", "superavg"]
MARKERS = ['o', 's', '^', 'D', 'v']
COLORS = ['red', 'blue', 'black', 'green', 'purple']

input_path = Path(INPUT_DIR).resolve()

def load_iq_result_avg(measurement: str) -> dict[str, pd.DataFrame]:
    iq_result: dict[str, pd.DataFrame] = {}
    for variant in VARIANTS:
        iq_result[variant] = pd.read_csv(input_path / f"{measurement}_{variant}.csv")
    return iq_result

def plot_iq(ax, iq_result, scale: list[float] | None = None):
    if scale is None:
        scale = [1.] * len(MEASUREMENTS)
    for i, (measurement, marker, color) in enumerate(zip(MEASUREMENTS, MARKERS, COLORS)):
        df = iq_result[i]
        ax.scatter(df['q'], df['intensity'] * scale[i], marker=marker, label=f'{measurement}%', alpha=0.8, s=20, color=color, facecolors='none')

iq_result_avg: dict[str, dict[str, pd.DataFrame]] = {}

for measurement in MEASUREMENTS:
    iq_result_avg[measurement] = load_iq_result_avg(measurement)

output_path = Path(OUTPUT_DIR).resolve()
Path(output_path).mkdir(parents=True, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

plot_iq(ax1, [iq_result_avg[measurement][VARIANTS[0]] for measurement in MEASUREMENTS])
ax1.set_xlabel('q [A$^{-1}$]')
ax1.set_ylabel('Intensity [a.u.]')
ax1.set_xlim(0.05, 0.5)
ax1.set_ylim(2e-3, 1.2e-2)
ax1.set_yscale('log')
ax1.legend(loc='lower left')
ax1.set_title('Decosmic')

plot_iq(ax2, [iq_result_avg[measurement][VARIANTS[1]] for measurement in MEASUREMENTS])
ax2.set_xlabel('q [A$^{-1}$]')
ax2.set_ylabel('Intensity [a.u.]')
ax2.set_xlim(0.05, 0.5)
ax2.set_ylim(2e-3, 1.2e-2)
ax2.set_yscale('log')
ax2.legend(loc='lower left')
ax2.set_title('Superavg')

plt.tight_layout()
plt.savefig(output_path / "iq_robust.pdf")
plt.close(fig)