from pathlib import Path
import numpy as np
import pyFAI
import fabio
from saxs_decosmic.core.series_processor import SeriesResult
import pandas as pd

# === Constants ===
INPUT_DIR = "."
OUTPUT_DIR = "iq"
UNIT = "q_A^-1"
BINNING = 100
MEASUREMENTS = ["popc", "water", "empty"]
VARIANTS = [
    "avg_direct", "avg_half_clean", "avg_clean",
    "var_direct", "var_half_clean", "var_clean",
    "avg_donut", "avg_streak"
]

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# === Mask and Calibration ===
mask = fabio.open(input_path / "mask.edf").data.astype(bool)
calib = input_path / "calib.poni"
ai = pyFAI.load(str(calib))

# === Data Loading ===
processed_results: dict[str, SeriesResult] = {}
for measurement in MEASUREMENTS:
    processed_results[measurement] = SeriesResult()
    processed_results[measurement].load(str(input_path / measurement / "processed"), measurement)

# === I(q) Integration ===
def integrate_iq(
    processed_result: SeriesResult,
    mask: np.ndarray,
    unit: str,
    n_points: int
) -> dict[str, pd.DataFrame]:
    """Integrate I(q) for each variant of a measurement."""
    iq_result: dict[str, pd.DataFrame] = {}
    for variant in VARIANTS:
        image = getattr(processed_result, variant)
        q, intensity, sigma = ai.integrate1d(image, n_points, mask=mask, unit=unit, error_model="azimuthal")
        iq_result[variant] = pd.DataFrame({
            'q': q,
            'intensity': intensity,
            'sigma': sigma,
        })
    return iq_result

# Integrate for all measurements
iq_results: dict[str, dict[str, pd.DataFrame]] = {}
for measurement in MEASUREMENTS:
    iq_results[measurement] = integrate_iq(processed_results[measurement], mask, UNIT, BINNING)

# Calculate subtracted (final) I(q)
final_iq_result: dict[str, pd.DataFrame] = {}
for variant in VARIANTS:
    final_q = iq_results[MEASUREMENTS[0]][variant]['q']
    final_intensity = iq_results[MEASUREMENTS[0]][variant]['intensity'] - iq_results[MEASUREMENTS[1]][variant]['intensity']
    final_sigma = np.sqrt(
        iq_results[MEASUREMENTS[0]][variant]['sigma']**2 +
        iq_results[MEASUREMENTS[1]][variant]['sigma']**2
    )
    # Only keep positive intensities for non-background variants
    if 'donut' not in variant and 'streak' not in variant:
        final_mask = final_intensity > 0
        final_q = final_q[final_mask]
        final_intensity = final_intensity[final_mask]
        final_sigma = final_sigma[final_mask]
    final_iq_result[variant] = pd.DataFrame({
        'q': final_q,
        'intensity': final_intensity,
        'sigma': final_sigma,
    })

# === Output ===
for variant in VARIANTS:
    for measurement in MEASUREMENTS:
        iq_results[measurement][variant].to_csv(output_path / f"{measurement}_{variant}.csv", index=False)
    final_iq_result[variant].to_csv(output_path / f"final_{variant}.csv", index=False)
