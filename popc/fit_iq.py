import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
from sasmodels.data import empty_data1D
from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment
from bumps.names import FitProblem, fit

# Constants
INPUT_DIR = "iq"
OUTPUT_DIR = "plot"
CSV_FILE = "final_avg_clean.csv"
OUTPUT_FILE = "fit_lamellar_hg.pdf"

# Fitting parameters
QMIN = 0.05
QMAX = 0.5
USE_SASVIEW_PRIORS = True
SASVIEW_P0 = [8.0349e-4, 9.1779e-6, 10.68, 13.54, 7.4189, 13.232, 10.561]
SASVIEW_BOUNDS = (
    [0.0, 0.0, 8.0, 10.0, 5.0, 10.0, 9.0],
    [1.0, 1e-3, 16.0, 18.0, 9.0, 16.0, 12.0],
)
FIX_SOLVENT_SLD = 10.56
SASMODELS_STEPS = 500

input_path = Path(INPUT_DIR).resolve()
output_path = Path(OUTPUT_DIR).resolve()
output_path.mkdir(parents=True, exist_ok=True)

# Load data
df = pd.read_csv(input_path / CSV_FILE)
q = df['q'].values
intensity = df['intensity'].values
sigma = df['sigma'].values


# Fitting
def fit_model(q: np.ndarray, intensity: np.ndarray, dy: np.ndarray) -> tuple[list[float], np.ndarray]:
    data = empty_data1D(q)
    data.y = intensity
    data.dy = dy

    kernel = load_model("lamellar_hg")
    base_p0 = SASVIEW_P0 if USE_SASVIEW_PRIORS else [1e-3, np.median(intensity[-10:]), 12.0, 12.0, 7.5, 13.0, 10.5]

    smodel = Model(
        kernel,
        scale=base_p0[0],
        background=base_p0[1],
        length_tail=base_p0[2],
        length_head=base_p0[3],
        sld=base_p0[4],
        sld_head=base_p0[5],
        sld_solvent=base_p0[6],
    )

    if USE_SASVIEW_PRIORS:
        lo, hi = SASVIEW_BOUNDS
        smodel.scale.range(max(lo[0], 0.0), hi[0])
        smodel.background.range(0.0, hi[1])
        smodel.length_tail.range(max(lo[2], 0.0), hi[2])
        smodel.length_head.range(max(lo[3], 0.0), hi[3])
        smodel.sld.range(lo[4], hi[4])
        smodel.sld_head.range(lo[5], hi[5])
        smodel.sld_solvent.range(lo[6], hi[6])

    smodel.sld_solvent.value = FIX_SOLVENT_SLD
    eps = 1e-12
    smodel.sld_solvent.range(FIX_SOLVENT_SLD - eps, FIX_SOLVENT_SLD + eps)

    experiment = Experiment(data=data, model=smodel)
    problem = FitProblem(experiment)
    result = fit(problem, method="amoeba", steps=SASMODELS_STEPS)
    print(result)

    popt = [
        smodel.scale.value,
        smodel.background.value,
        smodel.length_tail.value,
        smodel.length_head.value,
        smodel.sld.value,
        smodel.sld_head.value,
        smodel.sld_solvent.value,
    ]

    fit_I = experiment.theory()

    return popt, fit_I

def plot_fit(q: np.ndarray, intensity: np.ndarray, dy: np.ndarray, fit_I: np.ndarray) -> None:
    plt.figure(figsize=(6, 4))
    plt.errorbar(q, intensity, yerr=dy, fmt="o", ms=3, lw=0.5, label="data")
    idx = np.argsort(q)
    plt.plot(q[idx], fit_I[idx], "-", label="fit (lamellar_hg)")
    plt.xlabel("q (1/Å)")
    plt.ylabel("I(q) (a.u.)")
    plt.yscale("log")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path / OUTPUT_FILE)
    print(f"Saved plot to {output_path / OUTPUT_FILE}")

# Apply q-range mask
m = (q >= QMIN) & (q <= QMAX)
q, intensity, sigma = q[m], intensity[m], sigma[m]

# Prepare error bars
dy = np.where(sigma <= 0, np.median(sigma[sigma > 0]) * 0.1, sigma) if np.any(sigma > 0) else np.ones_like(intensity)

# Fit and plot
popt, fit_I = fit_model(q, intensity, dy)
plot_fit(q, intensity, dy, fit_I)

# Print results
names = ["scale", "background", "length_tail_A", "length_head_A", "sld_tail(1e-6/Å^2)", "sld_head(1e-6/Å^2)", "sld_solvent(1e-6/Å^2)"]
print("Fit results (lamellar_hg via sasmodels):")
for name, val in zip(names, popt):
    print(f"  {name:20s} = {val:.6g}")

dof = max(q.size - len(popt), 1)
chi2 = float(np.sum(((intensity - fit_I) / dy) ** 2))
rchi2 = chi2 / dof
print(f"  chi2 = {chi2:.3g}, dof = {dof}, reduced chi2 = {rchi2:.3g}")
