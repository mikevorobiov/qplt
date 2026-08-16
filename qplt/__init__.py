"""qplt: matplotlib styling, colorschemes, and fonts for
Nature Physics-style figures.

Quick start
-----------
>>> import qplt
>>> qplt.set_style()               # apply globally, like plt.style.use
>>> import matplotlib.pyplot as plt
>>> fig, ax = plt.subplots(figsize=qplt.figsize("single"))
>>> ax.plot(x, y, color=qplt.colors.PALETTE[0])
>>> qplt.panel_label(ax, "a")
>>> qplt.savefig(fig, "figure1")   # writes figure1.pdf and figure1.png

Or use it as a context manager to scope the style to one figure:

>>> with qplt.style():
...     fig, ax = plt.subplots()
...     ax.plot(x, y)

``"nature"`` matches the Nature-journal house style (Arial/sans-serif).
If your target venue typesets in LaTeX by default instead (Physical
Review/APS, AIP, arXiv, a thesis), use ``"nature-cm"`` for the same
layout with serif body text and Computer Modern math:

>>> qplt.set_style("nature-cm")

For day-to-day exploratory plotting (not a publication figure), use the
larger, screen-first ``"daily"`` style -- still a boxed axes with
inward/minor ticks and Computer Modern math, just bigger and with a
faint dotted grid instead of print-tuned minimalism. Reserve a sidebar
next to the plot for fit parameters or notes with :func:`daily_figure`:

>>> qplt.set_style("daily")
>>> fig, ax, side = qplt.daily_figure()
>>> ax.errorbar(x, y, yerr=yerr, fmt="o")
>>> qplt.sidebar_stats(side, {"chi2/dof": 1.08, "T_c (K)": "92.3(4)"},
...     title="Fit")
>>> qplt.stamp(fig)  # small provenance timestamp in the corner

For a fit against data, :func:`residual_figure` gives you a main panel
plus a shorter residuals panel below it, sharing the x-axis -- works
the same way under either style (add a sidebar for fit stats under
``"daily"``, skip it under ``"nature"`` for a publication panel):

>>> qplt.set_style("nature")
>>> fig, ax, ax_res, _ = qplt.residual_figure()
>>> ax.plot(x, data, "o"); ax.plot(x, fit)
>>> ax_res.plot(x, data - fit, "o")
>>> ax_res.set_xlabel("x"); ax_res.set_ylabel("Resid.")
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt

from . import colors, fonts
from .colors import PALETTE, PALETTE_MUTED, QUALITATIVE, get_palette
from .utils import (
    COLUMN_WIDTH_MM,
    daily_figure,
    figsize,
    label_panels,
    panel_label,
    rasterize,
    residual_figure,
    savefig,
    sidebar_stats,
    sidebar_text,
    stamp,
)

__version__ = "0.8.0"
__all__ = [
    "set_style",
    "style",
    "reset",
    "figsize",
    "panel_label",
    "label_panels",
    "rasterize",
    "savefig",
    "daily_figure",
    "residual_figure",
    "sidebar_text",
    "sidebar_stats",
    "stamp",
    "colors",
    "fonts",
    "PALETTE",
    "PALETTE_MUTED",
    "QUALITATIVE",
    "get_palette",
    "COLUMN_WIDTH_MM",
    "available_styles",
]

_STYLES_DIR = Path(__file__).parent / "styles"

_STYLE_FILES = {
    "nature": _STYLES_DIR / "nature.mplstyle",
    "nature-cm": _STYLES_DIR / "nature-cm.mplstyle",
    "daily": _STYLES_DIR / "daily.mplstyle",
}

_setup_done = False


def _ensure_setup():
    """Register bundled fonts and colormaps exactly once, lazily -- this
    has to happen before a style sheet that references e.g.
    ``image.cmap: qplt:ice`` or ``font.sans-serif: Liberation Sans`` is
    applied, or those names won't resolve.
    """
    global _setup_done
    if _setup_done:
        return
    fonts.register_fonts()
    colors.register_colormaps()
    _setup_done = True


def available_styles() -> list[str]:
    """Names accepted by :func:`set_style`."""
    return list(_STYLE_FILES)


def set_style(style_name: str = "nature") -> None:
    """Apply a qplt style sheet globally (equivalent to
    ``plt.style.use(...)``, but also registers the bundled fonts and
    colormaps first so they resolve correctly).

    Parameters
    ----------
    style_name:
        One of :func:`available_styles`:

        - ``"nature"`` -- Nature-journal house style: sans-serif
          (Arial/Helvetica-metric-compatible).
        - ``"nature-cm"`` -- identical layout, but serif body text +
          Computer Modern math, for venues that typeset in LaTeX by
          default (Physical Review/APS, AIP, arXiv, theses) rather than
          Nature's specific house style.
        - ``"daily"`` -- larger, screen-first exploratory style, also
          serif/Computer Modern -- see :func:`daily_figure`.

        Or a path to a custom ``.mplstyle`` file.
    """
    _ensure_setup()
    path = _STYLE_FILES.get(style_name, style_name)
    plt.style.use(str(path))


@contextmanager
def style(style_name: str = "nature"):
    """Context-manager form of :func:`set_style`, scoped to the ``with``
    block (uses :func:`matplotlib.pyplot.style.context` under the hood).
    """
    _ensure_setup()
    path = _STYLE_FILES.get(style_name, style_name)
    with plt.style.context(str(path)):
        yield


def reset() -> None:
    """Restore matplotlib's default rcParams."""
    plt.rcdefaults()
