from pathlib import Path
import numpy as np
import pyFAI
import fabio
from saxs_decosmic.core.series_processor import SeriesResult
import pandas as pd
from dataclasses import dataclass

INPUT_DIR = "."
OUTPUT_DIR = "iq"
UNIT = "q_A^-1"
BINNING = 100
MEASUREMENTS = ["20", "40", "60", "80", "100"]
VARIANTS = ["avg_clean", "superavg"]

@dataclass
class SeriesResultPlus(SeriesResult):
    superavg: np.ndarray | None = None

input_path = Path(INPUT_DIR).resolve()
mask = fabio.open(input_path / "mask.edf").data
calib = input_path / "calib.poni"
ai = pyFAI.load(str(calib))

processed_results: dict[str, SeriesResultPlus] = {}
for measurement in MEASUREMENTS:
    processed_results[measurement] = SeriesResultPlus()
    processed_results[measurement].load(str(input_path / measurement / "processed"), measurement)

# integrate iq for each measurement and variant
def integrate_iq(processed_result: SeriesResult, mask: np.ndarray, unit: str, n_points: int) -> dict[str, pd.DataFrame]:
    q: dict[str, np.ndarray] = {}
    intensity: dict[str, np.ndarray] = {}
    sigma: dict[str, np.ndarray] = {}
    iq_result: dict[str, pd.DataFrame] = {}
    for variant in VARIANTS:
        image = getattr(processed_result, variant)
        q[variant], intensity[variant], sigma[variant] = ai.integrate1d(image, n_points, mask=mask, unit=unit, error_model="azimuthal")
        iq_result[variant] = pd.DataFrame({
            'q': q[variant],
            'intensity': intensity[variant],
            'sigma': sigma[variant],
        })
    return iq_result

iq_results: dict[str, dict[str, pd.DataFrame]] = {}
for measurement in MEASUREMENTS:
    iq_results[measurement] = integrate_iq(processed_results[measurement], mask, UNIT, BINNING)

output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

for variant in VARIANTS:
    for measurement in MEASUREMENTS:
        iq_results[measurement][variant].to_csv(output_path / f"{measurement}_{variant}.csv", index=False)