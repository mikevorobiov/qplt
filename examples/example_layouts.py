"""Layout-themed gallery for qplt.

Four panels showing layout patterns that don't appear in the other
example scripts -- an inset zoom, a twin-axis plot, a polar plot, and a
grouped bar chart.

Run with:  python examples/example_layouts.py
Writes gallery_layouts.png / .pdf next to this script.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

rng = np.random.default_rng(21)

qplt.set_style("nature")
palette = qplt.get_palette()

fig, axes = plt.subplots(2, 2, figsize=qplt.figsize("double", aspect=0.72))

# --- Panel a: inset zoom ---------------------------------------------------
ax = axes[0, 0]
t = np.linspace(0, 20, 2000)
y = np.sin(t) + 0.15 * np.sin(11 * t)
ax.plot(t, y, color=palette[0], linewidth=0.8)
ax.set_xlabel("Time (a.u.)")
ax.set_ylabel("Signal")

ax_inset = ax.inset_axes([0.55, 0.55, 0.4, 0.4])
mask = (t > 8) & (t < 9.5)
ax_inset.plot(t[mask], y[mask], color=palette[0], linewidth=0.8)
ax_inset.set_xticks([])
ax_inset.set_yticks([])
for spine in ax_inset.spines.values():
    spine.set_linewidth(0.6)
ax.indicate_inset_zoom(ax_inset, edgecolor="black", linewidth=0.5)
qplt.panel_label(ax, "a")

# --- Panel b: twin y-axis ---------------------------------------------------
ax = axes[0, 1]
T = np.linspace(4, 300, 150)
resistivity = 0.02 + 1.2e-5 * T**2
magnetization = np.exp(-T / 60)

l1, = ax.plot(T, resistivity, color=palette[0], linewidth=1.2)
ax.set_xlabel("Temperature (K)")
ax.set_ylabel(r"Resistivity $\rho$ (m$\Omega\,$cm)", color=palette[0])
ax.tick_params(axis="y", colors=palette[0])
ax.spines["left"].set_color(palette[0])

ax2 = ax.twinx()
l2, = ax2.plot(T, magnetization, color=palette[1], linewidth=1.2, linestyle="--")
ax2.set_ylabel("Magnetization (a.u.)", color=palette[1])
ax2.tick_params(axis="y", colors=palette[1])
ax2.spines["right"].set_color(palette[1])
ax2.spines["left"].set_visible(False)
ax2.grid(False)
qplt.panel_label(ax, "b")

# --- Panel c: polar plot -----------------------------------------------
axes[1, 0].remove()
ax = fig.add_subplot(2, 2, 3, projection="polar")
theta = np.linspace(0, 2 * np.pi, 200)
r1 = 1 + 0.3 * np.cos(2 * theta)
r2 = 0.8 + 0.15 * np.cos(4 * theta + 0.4)
ax.plot(theta, r1, color=palette[2], linewidth=1.2, label="mode 1")
ax.plot(theta, r2, color=palette[4], linewidth=1.2, label="mode 2")
ax.set_rticks([0.5, 1.0, 1.5])
ax.set_rlabel_position(112.5)  # halfway between the 90 deg and 135 deg spokes
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=6)
qplt.panel_label(ax, "c", offset=(-0.05, 0.08))

# --- Panel d: grouped bar chart -------------------------------------------
ax = axes[1, 1]
materials = ["Cu", "Ag", "Au", "Pt"]
metrics = ["Conductivity", "Hardness", "Cost"]
n_groups, n_bars = len(materials), len(metrics)
x = np.arange(n_groups)
width = 0.8 / n_bars
values = rng.uniform(0.3, 1.0, size=(n_bars, n_groups))
for i, metric in enumerate(metrics):
    ax.bar(
        x + (i - (n_bars - 1) / 2) * width, values[i], width=width,
        color=palette[i], label=metric,
    )
ax.set_xticks(x)
ax.set_xticklabels(materials)
ax.set_ylabel("Normalized value")
ax.legend(loc="upper right", fontsize=6)
qplt.panel_label(ax, "d")

out_base = os.path.join(os.path.dirname(__file__), "gallery_layouts")
paths = qplt.savefig(fig, out_base, formats=("png", "pdf"))
print("Wrote:", *paths, sep="\n  ")
