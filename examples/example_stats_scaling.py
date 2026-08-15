"""Statistics- and scaling-themed gallery for qplt.

Four panels: a histogram with a KDE overlay, a log-log data-collapse
plot (many light background curves + one highlighted master curve), a
large rasterized scatter cloud, and an annotated correlation matrix
using the diverging colormap.

Run with:  python examples/example_stats_scaling.py
Writes gallery_stats_scaling.png / .pdf next to this script.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qplt  # noqa: E402

qplt.set_style("nature")

rng = np.random.default_rng(11)
palette = qplt.get_palette()
palette_muted = qplt.get_palette(muted=True)

fig, axes = plt.subplots(2, 2, figsize=qplt.figsize("double", aspect=0.72))

# --- Panel a: histogram + KDE --------------------------------------------
ax = axes[0, 0]
samples = rng.normal(0, 1, size=2000)
ax.hist(
    samples, bins=32, density=True, color=palette_muted[0],
    edgecolor="white", linewidth=0.3,
)
xs = np.linspace(-4, 4, 300)
# simple Gaussian KDE (avoids a scipy dependency)
bandwidth = 1.06 * samples.std() * samples.size ** (-1 / 5)
kde = np.mean(
    np.exp(-0.5 * ((xs[:, None] - samples[None, :]) / bandwidth) ** 2), axis=1
) / (bandwidth * np.sqrt(2 * np.pi))
ax.plot(xs, kde, color=palette[0], linewidth=1.3)
ax.set_xlabel(r"Order parameter $\psi$")
ax.set_ylabel("Probability density")
qplt.panel_label(ax, "a")

# --- Panel b: log-log scaling collapse -----------------------------------
ax = axes[0, 1]
x = np.logspace(-1, 2, 60)
n_runs = 14
for i in range(n_runs):
    noise_amp = rng.uniform(0.03, 0.09)
    y = x**-1.5 * (1 + noise_amp * rng.standard_normal(x.size))
    ax.loglog(x, y, color=palette_muted[3], linewidth=0.6, alpha=0.7)
master = x**-1.5
ax.loglog(x, master, color=palette[1], linewidth=1.6, label=r"$\sim x^{-3/2}$")
ax.set_xlabel(r"Rescaled size $L/\xi$")
ax.set_ylabel(r"Rescaled susceptibility $\chi$")
ax.legend(loc="lower left")
qplt.panel_label(ax, "b")

# --- Panel c: dense scatter cloud, rasterized ----------------------------
ax = axes[1, 0]
n_pts = 6000
cluster_a = rng.normal(loc=(-1.2, -0.6), scale=0.5, size=(n_pts // 2, 2))
cluster_b = rng.normal(loc=(1.0, 0.8), scale=0.7, size=(n_pts // 2, 2))
pts = np.vstack([cluster_a, cluster_b])
colors = np.array([palette[0]] * len(cluster_a) + [palette[1]] * len(cluster_b))
sc = ax.scatter(
    pts[:, 0], pts[:, 1], c=colors, s=3, linewidths=0, alpha=0.5,
)
qplt.rasterize(sc)
ax.set_xlabel(r"$x_1$")
ax.set_ylabel(r"$x_2$")
qplt.panel_label(ax, "c")

# --- Panel d: annotated correlation matrix (diverging colormap) ---------
ax = axes[1, 1]
labels = ["A", "B", "C", "D", "E"]
n = len(labels)
base = rng.normal(0, 1, size=(n, 200))
corr = np.corrcoef(base)
im = ax.imshow(corr, cmap="qplt:diverging", vmin=-1, vmax=1)
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.tick_params(which="both", length=0)
for i in range(n):
    for j in range(n):
        value = corr[i, j]
        text_color = "white" if abs(value) > 0.6 else "black"
        ax.text(
            j, i, f"{value:.2f}", ha="center", va="center",
            fontsize=5.5, color=text_color,
        )
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("Correlation")
qplt.panel_label(ax, "d")

out_base = os.path.join(os.path.dirname(__file__), "gallery_stats_scaling")
paths = qplt.savefig(fig, out_base, formats=("png", "pdf"))
print("Wrote:", *paths, sep="\n  ")
