"""residual_figure() demo for qplt: the same layout for a publication
panel and for a daily quick-look.

Run with:  python examples/example_residuals.py
Writes residuals_publication.png/.pdf and residuals_daily.png/.pdf next
to this script.
"""

from __future__ import annotations

import datetime
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

rng = np.random.default_rng(9)


def lorentzian(f, f0, fwhm, amp, offset):
    return offset + amp / (1 + ((f - f0) / (fwhm / 2)) ** 2)


freq = np.linspace(4.90, 5.10, 61)
true_params = dict(f0=5.004, fwhm=0.012, amp=1.0, offset=0.02)
noise_sigma = 0.015
signal = lorentzian(freq, **true_params) + rng.normal(0, noise_sigma, size=freq.size)

# quick grid-search fit, same approach as example_daily.py -- no scipy
# dependency needed for a sanity-check fit
f0_grid = np.linspace(4.99, 5.02, 61)
fwhm_grid = np.linspace(0.006, 0.02, 29)
best = None
for f0 in f0_grid:
    for fwhm in fwhm_grid:
        model = lorentzian(freq, f0, fwhm, true_params["amp"], true_params["offset"])
        chi2 = np.sum(((signal - model) / noise_sigma) ** 2)
        if best is None or chi2 < best[0]:
            best = (chi2, f0, fwhm)
chi2, f0_fit, fwhm_fit = best
dof = freq.size - 2
fit = lorentzian(freq, f0_fit, fwhm_fit, true_params["amp"], true_params["offset"])
fine = np.linspace(freq.min(), freq.max(), 400)
fit_fine = lorentzian(fine, f0_fit, fwhm_fit, true_params["amp"], true_params["offset"])
residuals = (signal - fit) / noise_sigma  # normalized residuals

# ===========================================================================
# Publication panel: nature style, no sidebar
# ===========================================================================
qplt.set_style("nature")
palette = qplt.get_palette()

fig, ax, ax_res, _ = qplt.residual_figure(figsize=qplt.figsize("single", aspect=0.9))

ax.errorbar(
    freq, signal, yerr=noise_sigma, fmt="o", color=palette[0],
    markersize=3, capsize=2, elinewidth=0.7, label="data",
)
ax.plot(fine, fit_fine, color=palette[1], linewidth=1.2, label="fit")
ax.set_ylabel(r"$S_{21}$ (a.u.)")
ax.legend(loc="upper right")

ax_res.axhspan(-1, 1, color=palette[0], alpha=0.12, linewidth=0)  # +/- 1 sigma band
ax_res.plot(freq, residuals, "o", color=palette[0], markersize=2.5)
ax_res.set_ylabel(r"$(\mathrm{data-fit})/\sigma$", fontsize=9)
ax_res.set_xlabel("Frequency (GHz)")

qplt.savefig(fig, os.path.join(os.path.dirname(__file__), "residuals_publication"))
print("Wrote residuals_publication.png / .pdf")

# ===========================================================================
# Daily quick-look: same fit, "daily" style, with a fit-stats sidebar
# ===========================================================================
qplt.set_style("daily")
palette = qplt.get_palette()

fig, ax, ax_res, side = qplt.residual_figure(sidebar_width=0.26)

ax.errorbar(
    freq, signal, yerr=noise_sigma, fmt="o", color=palette[0],
    markersize=4, capsize=3, elinewidth=1.0, label="data",
)
ax.plot(fine, fit_fine, color=palette[1], linewidth=1.8, label="fit")
ax.set_ylabel(r"$S_{21}$ (a.u.)")
ax.set_title("Resonator sweep, run 214")
ax.legend(loc="upper right")

ax_res.plot(freq, residuals, "o", color=palette[0], markersize=3.5)
ax_res.set_ylabel(r"$(\Delta)/\sigma$")
ax_res.set_xlabel("Frequency (GHz)")

Q = f0_fit / fwhm_fit
qplt.sidebar_stats(
    side,
    {
        "f_0 (GHz)": f"{f0_fit:.4f}",
        "FWHM (MHz)": fwhm_fit * 1e3,
        "Q": Q,
        "chi2/dof": chi2 / dof,
    },
    title="Fit",
)

# provenance stamp -- only on the daily quick-look, not the publication
# panel above.
qplt.stamp(fig, when=datetime.datetime(2026, 8, 15, 14, 32))

qplt.savefig(fig, os.path.join(os.path.dirname(__file__), "residuals_daily"))
print("Wrote residuals_daily.png / .pdf")
