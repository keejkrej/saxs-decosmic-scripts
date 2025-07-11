"""Utility functions to enforce a consistent Matplotlib style across all plot scripts."""

from typing import Mapping
import matplotlib as mpl

def apply_style(
    font_family: str = "Times New Roman",
    base_font_size: int = 10,
    title_font_size: int = 12,
    dpi: int = 300,
    use_latex: bool = True,
    **extra_rc: Mapping[str, object],
) -> None:
    """Apply a global Matplotlib style optimized for publication.

    Parameters
    ----------
    font_family
        Preferred font family (default: "serif" for LaTeX compatibility).
    base_font_size
        Base font size for labels, ticks, and legend (default: 10).
    title_font_size
        Font size for axes titles (default: 12).
    dpi
        Resolution for saved figures (default: 300).
    use_latex
        Whether to enable LaTeX text rendering (default: True).
    **extra_rc
        Additional ``matplotlib.rcParams`` overrides.
    """
    rc: dict[str, object] = {
        "font.family": font_family,
        "font.size": base_font_size,
        "axes.titlesize": title_font_size,
        "axes.labelsize": base_font_size,
        "legend.fontsize": base_font_size * 0.9,
        "xtick.labelsize": base_font_size * 0.9,
        "ytick.labelsize": base_font_size * 0.9,
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "lines.linewidth": 1.5,
        "lines.markersize": 6,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "figure.figsize": (6, 4),  # Default figure size (width, height) in inches
    }

    if use_latex:
        rc.update({
            "text.usetex": True,
            "text.latex.preamble": r"\usepackage{amsmath}",
        })

    rc.update(extra_rc)
    mpl.rcParams.update(rc) 