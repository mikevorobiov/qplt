"""Daily/exploratory-style demo for qplt.

Unlike the other example scripts, this one is not aiming for a
publication figure -- it's the "pull up today's run and sanity-check
the fit" style: a boxed axes with inward/minor ticks and Computer
Modern math (so it still reads like physics, not a dashboard), just
bigger and with a light dotted grid for reading values off quickly. The
sidebar holds the fit parameters, not a notes-app paragraph.

Run with:  python examples/example_daily.py
Writes daily_example.png / .pdf next to this script.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

qplt.set_style("daily")

rng = np.random.default_rng(5)
palette = qplt.get_palette()

fig, ax, side = qplt.daily_figure()


def lorentzian(f, f0, fwhm, amp, offset):
    return offset + amp / (1 + ((f - f0) / (fwhm / 2)) ** 2)


# --- Today's resonance sweep, with a quick fit -----------------------------
freq = np.linspace(4.90, 5.10, 61)  # GHz
true_params = dict(f0=5.004, fwhm=0.012, amp=1.0, offset=0.02)
noise_sigma = 0.015
signal = lorentzian(freq, **true_params) + rng.normal(0, noise_sigma, size=freq.size)

ax.errorbar(
    freq, signal, yerr=noise_sigma, fmt="o", color=palette[0],
    markersize=4, capsize=3, elinewidth=1.0, label="data",
)

# quick least-squares fit (no scipy dependency -- linearize a fine grid
# search, which is all a "daily" sanity check needs)
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
fine = np.linspace(freq.min(), freq.max(), 400)
ax.plot(
    fine, lorentzian(fine, f0_fit, fwhm_fit, true_params["amp"], true_params["offset"]),
    color=palette[1], linewidth=1.8, label="fit",
)

ax.set_xlabel("Frequency (GHz)")
ax.set_ylabel(r"$S_{21}$ (a.u.)")
ax.set_title("Resonator sweep, run 214")
ax.legend(loc="upper right")

Q = f0_fit / fwhm_fit
qplt.sidebar_stats(
    side,
    {
        "f_0 (GHz)": f"{f0_fit:.4f}",
        "FWHM (MHz)": fwhm_fit * 1e3,
        "Q": Q,
        "chi2/dof": chi2 / dof,
        "N points": freq.size,
    },
    title="Fit",
)
qplt.sidebar_text(
    side,
    "Consistent with run 213 (Q ~ 420). Re-check after the next cooldown.",
    title="Notes",
    y=0.45,
)

out_base = os.path.join(os.path.dirname(__file__), "daily_example")
paths = qplt.savefig(fig, out_base, formats=("png", "pdf"))
print("Wrote:", *paths, sep="\n  ")
