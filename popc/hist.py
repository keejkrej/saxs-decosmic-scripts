from pathlib import Path
import numpy as np
import fabio
from saxs_decosmic.core.series_processor import SeriesResult
import pandas as pd

# === Constants ===
INPUT_DIR = "."
OUTPUT_DIR = "hist"
MEASUREMENTS = ["popc", "water", "empty"]
VARIANTS = [
    "avg_direct", "avg_half_clean", "avg_clean",
    "var_direct", "var_half_clean", "var_clean"
]

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# === Mask ===
mask = fabio.open(input_path / "mask.edf").data.astype(bool)

# === Data Loading ===
processed_results: dict[str, SeriesResult] = {}
for measurement in MEASUREMENTS:
    processed_results[measurement] = SeriesResult()
    processed_results[measurement].load(str(input_path / measurement / "processed"), measurement)

# === Histogram Calculation ===
def get_hist(
    processed_result: SeriesResult,
    mask: np.ndarray,
    step_size: float = 0.001
) -> dict[str, pd.DataFrame]:
    """Calculate histogram for each variant of a measurement using a fixed step size."""
    hist_result: dict[str, pd.DataFrame] = {}
    for variant in VARIANTS:
        image = getattr(processed_result, variant)
        masked_data = image[mask]
        data_min = np.min(masked_data)
        data_max = np.max(masked_data)
        bins = np.arange(data_min, data_max + step_size, step_size)
        hist, bin_edges = np.histogram(masked_data, bins=bins)
        hist_result[variant] = pd.DataFrame({
            'hist': hist,
            'bins': bin_edges[:-1]
        })
    return hist_result

# Calculate histograms for all measurements
hist_results: dict[str, dict[str, pd.DataFrame]] = {}
for measurement in MEASUREMENTS:
    hist_results[measurement] = get_hist(processed_results[measurement], mask)

# === Output ===
for variant in VARIANTS:
    for measurement in MEASUREMENTS:
        hist_results[measurement][variant].to_csv(output_path / f"{measurement}_{variant}.csv", index=False)