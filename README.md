# qplt

Matplotlib styling, colorschemes, and fonts for figures in the visual
language of Nature Physics: a full boxed axes with inward ticks, thin
uniform line weights, muted colorblind-conscious colors, and exact
print-column sizing. `"nature"` matches the actual Nature house style
(Arial/sans-serif); `"nature-cm"` is the same layout with serif body
text and Computer Modern math instead, for venues that typeset in LaTeX
by default (Physical Review/APS, AIP, arXiv, a thesis). Also includes a
bigger, screen-first `"daily"` style
for day-to-day exploratory plotting — sanity-checking a run, a fit, a
sweep — not for publication, but still built around how physicists
actually read a plot (boxed axes, inward/minor ticks, Computer Modern
math), with a sidebar next to the plot for fit parameters or notes.

This is an independent, original styling package inspired by common
journal figure conventions. It is not affiliated with or endorsed by
Springer Nature.

## Install

```bash
pip install -e .
```

(from inside this directory; no dependencies beyond `matplotlib` and
`numpy`.)

## Quick start

```python
import matplotlib.pyplot as plt
import qplt

qplt.set_style()  # or qplt.set_style("nature-cm") for a LaTeX-typeset venue

fig, ax = plt.subplots(figsize=qplt.figsize("single"))
x = range(10)
ax.plot(x, [v**2 for v in x], color=qplt.PALETTE[0])
ax.set_xlabel("x")
ax.set_ylabel("y")
qplt.panel_label(ax, "a")

qplt.savefig(fig, "figure1")  # writes figure1.pdf and figure1.png
```

Or scope the style to a single figure instead of setting it globally:

```python
with qplt.style():
    fig, ax = plt.subplots()
    ax.plot(x, y)
```

For a quick look at today's data — not a publication figure — use the
`"daily"` style: bigger, screen-oriented, a faint dotted grid, still a
boxed axes with inward/minor ticks and Computer Modern math (not a
sans-serif dashboard). `daily_figure()` gives you a sidebar next to the
plot for exactly the kind of thing worth keeping in view while you're
looking at the data — fit parameters, chi-squared, run metadata:

```python
qplt.set_style("daily")
fig, ax, side = qplt.daily_figure()

ax.errorbar(freq, signal, yerr=noise_sigma, fmt="o", label="data")
ax.plot(fine, fitted_curve, label="fit")
ax.set_xlabel("Frequency (GHz)")
ax.set_ylabel(r"$S_{21}$ (a.u.)")
ax.legend()

qplt.sidebar_stats(side, {
    "f_0 (GHz)": "5.0040",
    "Q": 435.1,
    "chi2/dof": 0.90,
}, title="Fit")
qplt.savefig(fig, "resonator_sweep")
```

For a fit against data — a spectrum, a calibration curve, a resonance
fit — `residual_figure()` gives you the standard "data + fit on top,
residuals below" layout, sharing the x-axis. It works the same way
under either style: skip the sidebar under `"nature"` for a publication
panel, or add one under `"daily"` for fit stats next to the whole stack:

```python
qplt.set_style("nature")  # or "daily" (optionally with sidebar_width=0.28)
fig, ax, ax_res, side = qplt.residual_figure()

ax.errorbar(freq, signal, yerr=noise_sigma, fmt="o", label="data")
ax.plot(fine, fitted_curve, label="fit")
ax.set_ylabel(r"$S_{21}$ (a.u.)")
ax.legend()

ax_res.plot(freq, (signal - fit) / noise_sigma, "o")
ax_res.set_ylabel(r"$(\mathrm{data-fit})/\sigma$")
ax_res.set_xlabel("Frequency (GHz)")  # only the bottom panel gets an x-label

qplt.savefig(fig, "resonator_sweep")
```

## Examples

Each script in `examples/` is self-contained (`python examples/<name>.py`)
and writes matching `.png` / `.pdf` output next to itself:

| Script | Panels |
| --- | --- |
| `example_plots.py` | damped oscillations, an errorbar fit, a 2D field (`qplt:ice`), a diverging-colormap bar chart |
| `example_spectroscopy.py` | a fitted spectrum with a residuals sub-panel, a rasterized pump-probe heatmap (`qplt:ember`), an order parameter with an uncertainty band and critical point, multi-sample errorbar series |
| `example_stats_scaling.py` | a histogram with a KDE overlay, a log-log data-collapse plot, a large rasterized scatter cloud (6000 points), an annotated correlation matrix (`qplt:diverging`) |
| `example_layouts.py` | an inset zoom, a twin-axis plot, a polar plot, a grouped bar chart |
| `example_daily.py` | a resonator sweep with a quick Lorentzian fit in the `"daily"` style, with a sidebar of fit parameters (`sidebar_stats`) and a short note |
| `example_residuals.py` | the same Lorentzian fit run through `residual_figure()` twice — once as a `"nature"` publication panel, once as a `"daily"` quick-look with a fit-stats sidebar |

Together they cover every colormap, all three style variants, and most
of the panel layouts (stacked sub-panels and residuals, inset axes,
twin axes, polar projection, grouped/diverging bars) you're likely to
need for a real figure.

## What's included

**Styles** (`qplt.set_style(name)`)
- `"nature"` — light background, boxed axes, inward ticks on all four
  sides, publication-sized type for a ~89mm single-column figure. Arial
  (Liberation Sans)/sans-serif, matching the actual Nature journal
  house style.
- `"nature-cm"` — pixel-identical layout to `"nature"` (same box, ticks,
  sizing, dpi, PDF font embedding), but serif body text and Computer
  Modern math (`mathtext.fontset: cm`) instead of Arial. Nature
  specifically wants sans-serif, but most physics venues that typeset
  in LaTeX by default — Physical Review/APS, AIP, arXiv preprints, a
  thesis — use Computer Modern instead; use this variant for those.
- `"daily"` — for exploratory/day-to-day use, not publication, but still
  built around how physicists read a plot rather than a business
  dashboard look: a full boxed axes with inward and minor ticks (read a
  value off any edge), a faint dotted "graph paper" grid instead of a
  filled dashboard grid, serif body text with Computer Modern math
  (`mathtext.fontset: cm`, matplotlib-bundled, no LaTeX install
  required) so equations look like the LaTeX you already read, a plain
  thin-border legend (no rounded corners/shadow), and a bigger default
  canvas. Pair with `daily_figure()` for a sidebar meant for fit
  parameters (`sidebar_stats`) or notes (`sidebar_text`). Same color
  cycle and colormaps as the other two styles, so switching styles never
  changes what a dataset looks like colorwise.

**Colors** (`qplt.colors`)
- `PALETTE` / `QUALITATIVE` — an 8-color qualitative palette for
  categorical series (also the default `axes.prop_cycle`).
- `PALETTE_MUTED` — a softer variant for dense scatter/fill.
- `qplt:ice`, `qplt:ember` — single-hue sequential colormaps
  (registered with matplotlib, so also usable as `cmap="qplt:ice"`
  or `plt.get_cmap("qplt:ice")`; `_r` reversed variants are
  registered too).
- `qplt:diverging` — a blue/white/vermillion diverging colormap
  (avoids red-green, which ~8% of men can't distinguish).

**Fonts** (`qplt.fonts`)
- Bundles Liberation Sans and Liberation Serif (SIL Open Font License
  1.1 — see `qplt/fontfiles/OFL.txt`), which are metric-compatible
  drop-in replacements for Arial and Times New Roman. Figures render
  identically whether or not the commercial fonts are installed, and
  text never reflows if a machine substitutes one for the other.
- `qplt.fonts.register_fonts()` is called automatically by
  `set_style()`; it also picks up real Arial/Helvetica/Times if your
  system has them (`preferred_sans_stack()` / `preferred_serif_stack()`).
- PDF/PS output embeds real, editable text (`pdf.fonttype: 42`), not
  outlined paths or bitmapped Type 3 fonts — required by most journal
  submission systems.

**Layout helpers** (`qplt.utils`, re-exported at top level)
- `figsize("single" | "1.5" | "double", aspect=..., height_mm=...)` —
  exact figure sizing in inches from Nature-family print column widths
  (89 / 120 / 183 mm).
- `panel_label(ax, "a")` / `label_panels(axes)` — bold lowercase panel
  labels positioned above the top-left corner of an axes.
- `savefig(fig, "name", formats=("pdf", "png"))` — save multiple
  formats at once at submission-quality (600 dpi) resolution.
- `rasterize(artist)` — mark a dense artist (`pcolormesh`, `contourf`,
  `pcolor`, a big `scatter`) to be embedded as a raster image instead of
  thousands of individual vector paths when saved to PDF/SVG/EPS. **Always
  wrap colormap/heatmap plots in this** — an unrasterized `pcolormesh`
  over a 200×200 grid alone produces a ~750 KB PDF that's slow to open
  and scroll in Preview/Acrobat/LaTeX; rasterized it's ~50–65 KB and
  opens instantly, with no visible quality loss at the default 600 dpi.
  Lines, text, and axis labels are unaffected and stay sharp vector
  output:
  ```python
  im = qplt.rasterize(ax.pcolormesh(x, y, z, cmap="qplt:ice"))
  ```
- `daily_figure(figsize=None, sidebar_width=0.28)` — build a figure with
  a main plot axes plus a blank, frameless sidebar axes to its right,
  sized for the `"daily"` style. Returns `(fig, ax, side_ax)`.
- `residual_figure(figsize=None, height_ratio=0.28, sidebar_width=0.0, zero_line=True)`
  — build a figure with a main plot on top and a shorter residuals panel
  below it, sharing the x-axis (only the residuals panel keeps its
  x-axis tick labels). Works under any active style — no sidebar for a
  `"nature"` publication panel, or `sidebar_width > 0` under `"daily"`
  for fit stats next to the whole stack. Draws a y=0 reference line in
  the residuals panel by default, and caps its y-tick count at 3 to
  keep the short panel uncluttered. Returns `(fig, ax, ax_resid,
  side_ax)`; `side_ax` is `None` unless `sidebar_width > 0`.
- `sidebar_stats(side_ax, stats, title=None, fmt="{:.4g}")` — write a
  monospace key/value block into a sidebar axes — fit parameters,
  chi-squared, run metadata — with values lined up in a column like a
  fit routine's printed output. Takes a dict or a list of `(label,
  value)` pairs; numbers are formatted with `fmt`, strings (e.g. an
  already-formatted uncertainty like `"92.3(4)"`) pass through as-is.
- `sidebar_text(side_ax, text, title=None, wrap_width=34)` — write a
  bold title plus word-wrapped body text into a sidebar axes, for
  free-form notes (paragraphs separated by `"\n\n"` wrap independently).
  Both sidebar helpers work on any blank axes, not just ones from
  `daily_figure()`.

## License

Package code: MIT (see `LICENSE`).
Bundled fonts: SIL Open Font License 1.1 (see `qplt/fontfiles/OFL.txt`).
