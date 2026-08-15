"""Demo gallery for qplt.

Run with:  python examples/example_plots.py
Writes gallery.png / gallery.pdf next to this script.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

qplt.set_style("nature")

rng = np.random.default_rng(7)
palette = qplt.get_palette()

fig, axes = plt.subplots(2, 2, figsize=qplt.figsize("double", aspect=0.72))

# --- Panel a: damped oscillations, several series -----------------------
ax = axes[0, 0]
t = np.linspace(0, 10, 400)
for i, gamma in enumerate([0.05, 0.15, 0.3]):
    y = np.exp(-gamma * t) * np.cos(2 * np.pi * 0.8 * t)
    ax.plot(t, y, color=palette[i], label=rf"$\gamma={gamma}$")
ax.set_xlabel("Time (a.u.)")
ax.set_ylabel("Amplitude")
ax.legend(loc="upper right")
ax.set_xlim(0, 10)

# --- Panel b: scatter with error bars ------------------------------------
ax = axes[0, 1]
x = np.linspace(0, 1, 12)
y = x**2 + rng.normal(0, 0.02, size=x.size)
yerr = rng.uniform(0.015, 0.035, size=x.size)
ax.errorbar(
    x, y, yerr=yerr, fmt="o", color=palette[1], ecolor=palette[1],
    markersize=3.5, capsize=2, elinewidth=0.7,
)
xx = np.linspace(0, 1, 100)
ax.plot(xx, xx**2, color=palette[5], linestyle="--", linewidth=1.0)
ax.set_xlabel(r"Control parameter $\lambda$")
ax.set_ylabel(r"Response $R$")

# --- Panel c: 2D field (sequential colormap) -----------------------------
ax = axes[1, 0]
xg, yg = np.meshgrid(np.linspace(-3, 3, 200), np.linspace(-3, 3, 200))
field = np.exp(-(xg**2 + yg**2) / 3) * np.cos(3 * xg) * np.sin(3 * yg)
im = qplt.rasterize(ax.pcolormesh(xg, yg, field, cmap="qplt:ice", shading="auto"))
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("Field intensity")
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_xticks([-3, 0, 3])
ax.set_yticks([-3, 0, 3])

# --- Panel d: diverging colormap, categorical bars -----------------------
ax = axes[1, 1]
categories = ["A", "B", "C", "D", "E", "F"]
values = rng.normal(0, 1, size=len(categories))
bar_colors = [
    qplt.colors.diverging(0.15) if v < 0 else qplt.colors.diverging(0.85)
    for v in values
]
ax.bar(categories, values, color=bar_colors, width=0.6)
ax.axhline(0, color="black", linewidth=0.6)
ax.set_ylabel(r"$\Delta$ (a.u.)")

for ax, label in zip(axes.flat, "abcd"):
    qplt.panel_label(ax, label)

out_base = os.path.join(os.path.dirname(__file__), "gallery")
paths = qplt.savefig(fig, out_base, formats=("png", "pdf"))
print("Wrote:", *paths, sep="\n  ")
