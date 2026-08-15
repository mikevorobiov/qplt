"""Spectroscopy-themed gallery for qplt.

Four panels common in condensed-matter / optics papers: a fitted
spectrum with its residuals underneath, a 2D pump-probe-style heatmap,
and an order-parameter-vs-temperature curve with an uncertainty band and
a marked critical point.

Run with:  python examples/example_spectroscopy.py
Writes gallery_spectroscopy.png / .pdf next to this script.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

qplt.set_style("nature")

rng = np.random.default_rng(3)
palette = qplt.get_palette()

fig, axes = plt.subplots(2, 2, figsize=qplt.figsize("double", aspect=0.72))


def lorentzian(x, x0, gamma, amp):
    return amp * (gamma**2) / ((x - x0) ** 2 + gamma**2)


# --- Panel a: fitted spectrum with residuals (stacked sub-panels) --------
ax = axes[0, 0]
divider_frac = 0.28  # fraction of the panel height given to the residual strip
pos = ax.get_position()
ax.set_visible(False)
ax_main = fig.add_axes(
    [pos.x0, pos.y0 + pos.height * divider_frac, pos.width, pos.height * (1 - divider_frac)]
)
ax_res = fig.add_axes(
    [pos.x0, pos.y0, pos.width, pos.height * divider_frac], sharex=ax_main
)

energy = np.linspace(1.0, 3.0, 300)
true_spectrum = (
    lorentzian(energy, 1.55, 0.05, 1.0)
    + lorentzian(energy, 2.05, 0.08, 0.6)
    + lorentzian(energy, 2.55, 0.04, 0.35)
)
noisy = true_spectrum + rng.normal(0, 0.02, size=energy.size)

ax_main.plot(
    energy, noisy, "o", color=palette[7], markersize=2.2, markeredgewidth=0,
    alpha=0.6, label="data",
)
ax_main.plot(energy, true_spectrum, color=palette[0], linewidth=1.2, label="fit")
ax_main.set_ylabel("Intensity (a.u.)")
ax_main.legend(loc="upper right")
plt.setp(ax_main.get_xticklabels(), visible=False)
ax_main.tick_params(axis="x", which="both", length=0)

residual = noisy - true_spectrum
ax_res.axhline(0, color="black", linewidth=0.5)
ax_res.plot(energy, residual, color=palette[5], linewidth=0.6)
ax_res.set_ylabel("Resid.", fontsize=6)
ax_res.set_xlabel("Photon energy (eV)")
ax_res.set_ylim(-0.08, 0.08)

qplt.panel_label(ax_main, "a")

# --- Panel b: 2D pump-probe map (sequential colormap, rasterized) --------
ax = axes[0, 1]
delay = np.linspace(-1, 5, 220)
probe_e = np.linspace(1.0, 3.0, 220)
D, E = np.meshgrid(delay, probe_e)
signal = (
    np.exp(-((E - 1.9) ** 2) / (2 * 0.12**2))
    * np.exp(-np.clip(D, 0, None) / 1.3)
    * (D > -0.2)
)
signal += 0.03 * rng.standard_normal(signal.shape)

im = qplt.rasterize(
    ax.pcolormesh(D, E, signal, cmap="qplt:ember", shading="auto")
)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label(r"$\Delta R/R$ (a.u.)")
ax.set_xlabel("Pump-probe delay (ps)")
ax.set_ylabel("Probe energy (eV)")
qplt.panel_label(ax, "b")

# --- Panel c: order parameter vs. temperature, with uncertainty band -----
ax = axes[1, 0]
Tc = 92.0
T = np.linspace(50, 130, 200)
order_param = np.where(T < Tc, np.clip(1 - T / Tc, 0, None) ** 0.35, 0.0)
band = 0.03 + 0.02 * (T > Tc)
ax.plot(T, order_param, color=palette[2], linewidth=1.2)
ax.fill_between(
    T, order_param - band, order_param + band, color=palette[2], alpha=0.2, linewidth=0
)
ax.axvline(Tc, color=palette[1], linestyle="--", linewidth=0.8)
ax.annotate(
    r"$T_c$", xy=(Tc, 0.9), xytext=(Tc + 8, 0.9),
    fontsize=7, color=palette[1], va="center",
    arrowprops=dict(arrowstyle="-", color=palette[1], linewidth=0.6),
)
ax.set_xlabel("Temperature (K)")
ax.set_ylabel("Order parameter")
ax.set_ylim(-0.05, 1.05)
qplt.panel_label(ax, "c")

# --- Panel d: peak position vs. control parameter, multiple datasets -----
ax = axes[1, 1]
markers = ["o", "s", "^"]
for i, (label, shift) in enumerate(
    [("sample A", 0.0), ("sample B", 0.05), ("sample C", -0.03)]
):
    xp = np.linspace(0, 1, 9)
    yp = 1.55 + shift + 0.15 * xp**1.5 + rng.normal(0, 0.01, size=xp.size)
    yerr = rng.uniform(0.008, 0.018, size=xp.size)
    ax.errorbar(
        xp, yp, yerr=yerr, fmt=markers[i], color=palette[i + 3],
        markersize=3.2, capsize=2, elinewidth=0.7, label=label,
    )
ax.set_xlabel("Doping level $x$")
ax.set_ylabel("Peak energy (eV)")
ax.legend(loc="upper left", fontsize=6)
qplt.panel_label(ax, "d")

out_base = os.path.join(os.path.dirname(__file__), "gallery_spectroscopy")
paths = qplt.savefig(fig, out_base, formats=("png", "pdf"))
print("Wrote:", *paths, sep="\n  ")
