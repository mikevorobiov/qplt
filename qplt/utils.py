"""Layout and figure-export helpers for qplt.

Mostly small conveniences around the two things that are fiddly to get
right by hand every time: sizing a figure to an exact print column width,
and adding the bold lowercase panel labels (a, b, c, ...) that multi-panel
journal figures use.
"""

from __future__ import annotations

import string
from typing import Iterable, Sequence

import matplotlib.pyplot as plt

MM_PER_INCH = 25.4

# Typical Nature-family print column widths, in millimetres. Individual
# journals vary by a mm or two -- treat these as good defaults, not a
# guarantee of an exact house spec.
COLUMN_WIDTH_MM = {
    "single": 89.0,   # one-column figure
    "1.5": 120.0,      # "1.5 column" figure, used by some Nature journals
    "double": 183.0,  # full double-column figure
}
MAX_HEIGHT_MM = 247.0  # approximate max figure height (single page)


def mm_to_in(mm: float) -> float:
    """Convert millimetres to inches."""
    return mm / MM_PER_INCH


def figsize(
    width: str | float = "single",
    aspect: float = 0.75,
    height_mm: float | None = None,
) -> tuple[float, float]:
    """Compute a ``figsize=(w, h)`` tuple in inches for a journal column.

    Parameters
    ----------
    width:
        One of ``"single"``, ``"1.5"``, ``"double"`` (journal column
        presets), or an explicit width in millimetres.
    aspect:
        Height-to-width ratio used when ``height_mm`` is not given.
        0.75 (a 4:3-ish figure) is a reasonable default; use ~0.62 for a
        golden-ratio-ish wide panel, or 1.0 for a square panel.
    height_mm:
        Explicit height in millimetres, overriding ``aspect``.

    Examples
    --------
    >>> figsize("single")
    (3.5039..., 2.6279...)
    >>> figsize("double", aspect=0.4)
    (7.2047..., 2.8818...)
    """
    width_mm = COLUMN_WIDTH_MM.get(width, width) if isinstance(width, str) else width
    if not isinstance(width_mm, (int, float)):
        raise ValueError(f"Unknown width preset {width!r}; use one of {list(COLUMN_WIDTH_MM)} or a number in mm")

    h_mm = height_mm if height_mm is not None else width_mm * aspect
    return (mm_to_in(width_mm), mm_to_in(h_mm))


def panel_label(
    ax,
    label: str | int,
    loc: str = "upper left",
    offset: tuple[float, float] = (-0.18, 0.08),
    fontweight: str = "bold",
    fontsize: float | None = None,
    **text_kwargs,
):
    """Add a bold lowercase panel label (e.g. "a", "b", "c") just outside
    the top-left corner of an axes, matching the multi-panel figure
    convention used across Nature journals.

    Parameters
    ----------
    ax:
        The axes to label.
    label:
        A letter (``"a"``), or an int (``0`` -> "a", ``1`` -> "b", ...).
    loc:
        Currently only ``"upper left"`` is implemented (the standard
        placement); kept as a parameter for future extension.
    offset:
        (x, y) offset in axes fraction coordinates from the top-left
        corner. Negative x nudges the label left of the axes; positive y
        nudges it above.
    fontweight, fontsize:
        Passed through to :meth:`~matplotlib.axes.Axes.text`. ``fontsize``
        defaults to the current ``axes.titlesize`` rcParam if not given.
    """
    if isinstance(label, int):
        label = string.ascii_lowercase[label]

    if loc != "upper left":
        raise NotImplementedError("only loc='upper left' is currently supported")

    fontsize = fontsize if fontsize is not None else plt.rcParams["axes.titlesize"]
    x, y = offset
    return ax.text(
        x,
        1.0 + y,
        label,
        transform=ax.transAxes,
        fontweight=fontweight,
        fontsize=fontsize,
        va="bottom",
        ha="left",
        **text_kwargs,
    )


def label_panels(axes: Iterable, labels: Sequence[str] | None = None, **kwargs):
    """Call :func:`panel_label` on each axes in ``axes``, in order,
    using consecutive letters (or a custom ``labels`` sequence).
    """
    axes = list(axes)
    labels = labels if labels is not None else string.ascii_lowercase[: len(axes)]
    return [panel_label(ax, lab, **kwargs) for ax, lab in zip(axes, labels)]


def daily_figure(
    figsize: tuple[float, float] | None = None,
    sidebar_width: float = 0.28,
    wspace: float = 0.06,
):
    """Create a figure laid out for the ``"daily"`` style: a main plot
    axes plus a blank, frameless sidebar axes to its right for notes,
    running commentary, a stats readout, a changelog -- whatever
    context doesn't belong inside the plot itself but is useful to keep
    next to it (this is for your own exploratory/notebook use, not a
    publication figure).

    Parameters
    ----------
    figsize:
        Overall figure size in inches. Defaults to the ``"daily"``
        style's ``figure.figsize`` rcParam (8.0 x 5.2in) if not given --
        call :func:`set_style` (or activate ``qplt.style("daily")``)
        first so that default picks up the right size.
    sidebar_width:
        Fraction (0-1) of the figure width given to the sidebar.
    wspace:
        Gap between the plot and the sidebar, as a fraction of the
        average axes width (passed straight to ``GridSpec``).

    Returns
    -------
    ``(fig, ax, side_ax)`` -- plot on ``ax`` as normal; write into
    ``side_ax`` directly, or via :func:`sidebar_stats` (fit
    parameters/metadata, monospace, values aligned in a column) or
    :func:`sidebar_text` (free-form notes).

    Examples
    --------
    >>> qplt.set_style("daily")
    >>> fig, ax, side = qplt.daily_figure()
    >>> ax.errorbar(x, y, yerr=yerr, fmt="o")
    >>> qplt.sidebar_stats(side, {"chi2/dof": 1.08, "T_c (K)": "92.3(4)"},
    ...     title="Fit")
    """
    if not (0 < sidebar_width < 1):
        raise ValueError("sidebar_width must be between 0 and 1 (exclusive)")

    figsize = figsize if figsize is not None else plt.rcParams["figure.figsize"]
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(1, 2, width_ratios=[1 - sidebar_width, sidebar_width], wspace=wspace)
    ax = fig.add_subplot(gs[0, 0])
    side_ax = fig.add_subplot(gs[0, 1])
    side_ax.axis("off")
    return fig, ax, side_ax


def residual_figure(
    figsize: tuple[float, float] | None = None,
    height_ratio: float = 0.28,
    hspace: float = 0.06,
    sidebar_width: float = 0.0,
    wspace: float = 0.06,
    zero_line: bool = True,
    resid_nbins: int | None = 3,
):
    """Create a figure with a main plot on top and a shorter residuals
    panel below it, sharing the x-axis -- the standard "data + fit
    above, fit minus data below" layout for checking a fit against
    data (a spectrum, a calibration curve, a resonance fit, ...).

    Works with whatever style is currently active, so the same call
    gives you either a publication panel or a daily-use one:

    - ``set_style("nature")`` (or ``"nature-cm"``) first for a
      publication-ready panel.
    - ``set_style("daily")`` first, and pass ``sidebar_width > 0``, for
      a quick-look version with a sidebar for fit stats next to the
      whole plot+residuals stack (see :func:`sidebar_stats`).

    Parameters
    ----------
    figsize:
        Overall figure size in inches. Defaults to the active style's
        ``figure.figsize`` rcParam.
    height_ratio:
        Fraction (0-1) of the plot-stack height given to the residuals
        panel.
    hspace:
        Vertical gap between the main and residuals panels, as a
        ``GridSpec`` fraction.
    sidebar_width:
        Fraction (0-1) of the figure width given to a blank sidebar to
        the right, for :func:`sidebar_stats`/:func:`sidebar_text`. 0
        (the default) omits the sidebar entirely.
    wspace:
        Gap between the plot stack and the sidebar (only relevant if
        ``sidebar_width`` > 0).
    zero_line:
        Draw a thin horizontal line at y=0 across the residuals panel
        (residuals are almost always centered on zero).
    resid_nbins:
        Max number of y-tick labels in the (short) residuals panel, to
        avoid crowding; set to ``None`` to leave the default locator
        alone.

    Returns
    -------
    ``(fig, ax, ax_resid, side_ax)`` -- ``ax`` and ``ax_resid`` share
    the x-axis, with ``ax``'s bottom tick labels hidden so only
    ``ax_resid`` shows x-axis ticks/labels. ``side_ax`` is ``None``
    unless ``sidebar_width`` > 0.

    Examples
    --------
    >>> qplt.set_style("nature")
    >>> fig, ax, ax_res, _ = qplt.residual_figure()
    >>> ax.plot(x, data, "o")
    >>> ax.plot(x, fit)
    >>> ax_res.plot(x, data - fit, "o")
    >>> ax_res.set_xlabel("x")
    >>> ax.set_ylabel("y")
    >>> ax_res.set_ylabel("Resid.")

    >>> qplt.set_style("daily")
    >>> fig, ax, ax_res, side = qplt.residual_figure(sidebar_width=0.28)
    >>> qplt.sidebar_stats(side, {"chi2/dof": 1.1}, title="Fit")
    """
    if not (0 < height_ratio < 1):
        raise ValueError("height_ratio must be between 0 and 1 (exclusive)")
    if not (0 <= sidebar_width < 1):
        raise ValueError("sidebar_width must be 0 (no sidebar) or between 0 and 1 (exclusive)")

    figsize = figsize if figsize is not None else plt.rcParams["figure.figsize"]
    fig = plt.figure(figsize=figsize)

    if sidebar_width > 0:
        outer = fig.add_gridspec(
            1, 2, width_ratios=[1 - sidebar_width, sidebar_width], wspace=wspace
        )
        plot_cell = outer[0, 0]
        side_ax = fig.add_subplot(outer[0, 1])
        side_ax.axis("off")
    else:
        plot_cell = fig.add_gridspec(1, 1)[0, 0]
        side_ax = None

    inner = plot_cell.subgridspec(2, 1, height_ratios=[1 - height_ratio, height_ratio], hspace=hspace)
    ax = fig.add_subplot(inner[0, 0])
    ax_resid = fig.add_subplot(inner[1, 0], sharex=ax)

    # Use tick_params (persistent Axis-level state), not setp on the
    # current get_xticklabels() -- those Text artists get replaced
    # whenever the view limits change (e.g. once the caller plots data
    # and autoscale kicks in), which would silently un-hide a label set
    # via setp before any data existed.
    ax.tick_params(
        axis="x", which="both", bottom=False, top=plt.rcParams["xtick.top"],
        labelbottom=False, labeltop=False,
    )

    if zero_line:
        ax_resid.axhline(
            0, color=plt.rcParams["axes.edgecolor"], linewidth=plt.rcParams["axes.linewidth"]
        )

    if resid_nbins is not None:
        from matplotlib.ticker import MaxNLocator

        ax_resid.yaxis.set_major_locator(MaxNLocator(nbins=resid_nbins))

    return fig, ax, ax_resid, side_ax


def sidebar_text(
    side_ax,
    text: str,
    title: str | None = None,
    wrap_width: int = 34,
    fontsize: float | None = None,
    title_fontsize: float | None = None,
    y: float = 0.98,
    title_gap: float = 0.08,
    color: str = "#222222",
    **text_kwargs,
):
    """Write a title + wrapped body of text into a sidebar axes (as
    created by :func:`daily_figure`, or any other blank/frameless axes).

    Paragraphs (separated by a blank line, i.e. ``"\\n\\n"``) are wrapped
    independently, so intentional paragraph breaks in ``text`` survive.

    Parameters
    ----------
    side_ax:
        The (typically axes-off) axes to write into.
    text:
        Body text. Use ``"\\n\\n"`` between paragraphs.
    title:
        Optional bold heading placed above the body.
    wrap_width:
        Characters per line before wrapping. Text sidebars are narrow,
        so the default favors a narrower wrap than prose; tune this to
        the actual sidebar width/fontsize you're using.
    fontsize, title_fontsize:
        Override the body/title font size; default to the current
        ``font.size`` / ``axes.titlesize`` rcParams.
    y:
        Starting vertical position (axes fraction, 0=bottom, 1=top).
    title_gap:
        Vertical gap (axes fraction) inserted between the title and the
        body, if a title is given.
    color:
        Text color for the body (and title, unless overridden via
        ``text_kwargs``).

    Returns
    -------
    The list of text artists created (title first, if given).
    """
    import textwrap

    fontsize = fontsize if fontsize is not None else plt.rcParams["font.size"]
    title_fontsize = (
        title_fontsize if title_fontsize is not None else plt.rcParams["axes.titlesize"]
    )

    artists = []
    cursor = y
    if title:
        artists.append(
            side_ax.text(
                0,
                cursor,
                title,
                transform=side_ax.transAxes,
                fontsize=title_fontsize,
                fontweight="bold",
                color=color,
                va="top",
                ha="left",
            )
        )
        cursor -= title_gap

    paragraphs = text.split("\n\n")
    wrapped = "\n\n".join(textwrap.fill(p.strip(), width=wrap_width) for p in paragraphs)
    artists.append(
        side_ax.text(
            0,
            cursor,
            wrapped,
            transform=side_ax.transAxes,
            fontsize=fontsize,
            color=color,
            va="top",
            ha="left",
            linespacing=1.5,
            **text_kwargs,
        )
    )
    return artists


def sidebar_stats(
    side_ax,
    stats,
    title: str | None = None,
    fmt: str = "{:.4g}",
    y: float = 0.98,
    title_gap: float = 0.07,
    fontsize: float | None = None,
    title_fontsize: float | None = None,
    color: str = "#111111",
    **text_kwargs,
):
    """Write a monospace key/value block into a sidebar axes -- fit
    parameters, chi-squared, run metadata -- the kind of thing worth
    keeping next to a plot while you're actually looking at the data,
    rather than a business-notes paragraph. Values line up in a column
    like a fit routine's printed output.

    Parameters
    ----------
    side_ax:
        Axes to write into (e.g. from :func:`daily_figure`).
    stats:
        A dict, or an iterable of ``(label, value)`` pairs (a dict is
        usually simplest; Python dicts preserve insertion order so rows
        come out in the order you wrote them). Numeric values are
        formatted with ``fmt``; strings are used as-is, so you can pass
        an already-formatted uncertainty like ``"92.3(4)"``.
    title:
        Optional bold heading above the block.
    fmt:
        Format spec applied to non-string, non-already-formatted values.

    Returns
    -------
    The list of text artists created (title first, if given).

    Examples
    --------
    >>> qplt.sidebar_stats(side, {
    ...     "chi2/dof": 1.08,
    ...     "T_c (K)": "92.3(4)",
    ...     "gamma": 0.35,
    ...     "N points": 42,
    ... }, title="Fit")
    """
    import numbers

    items = list(stats.items()) if hasattr(stats, "items") else list(stats)
    if not items:
        raise ValueError("stats must contain at least one (label, value) pair")

    label_width = max(len(str(label)) for label, _ in items)

    def _fmt_value(value):
        if isinstance(value, str):
            return value
        if isinstance(value, numbers.Real):
            return fmt.format(value)
        return str(value)

    body = "\n".join(
        f"{str(label):<{label_width}}  {_fmt_value(value)}" for label, value in items
    )

    fontsize = fontsize if fontsize is not None else plt.rcParams["font.size"]
    title_fontsize = (
        title_fontsize if title_fontsize is not None else plt.rcParams["axes.titlesize"]
    )

    artists = []
    cursor = y
    if title:
        artists.append(
            side_ax.text(
                0,
                cursor,
                title,
                transform=side_ax.transAxes,
                fontsize=title_fontsize,
                fontweight="bold",
                color=color,
                va="top",
                ha="left",
            )
        )
        cursor -= title_gap

    artists.append(
        side_ax.text(
            0,
            cursor,
            body,
            transform=side_ax.transAxes,
            fontsize=fontsize,
            color=color,
            va="top",
            ha="left",
            family="monospace",
            linespacing=1.6,
            **text_kwargs,
        )
    )
    return artists


def rasterize(artists):
    """Mark one or more artists to be rasterized (rather than kept as
    vector paths) when the figure is saved to a vector format (PDF/SVG/EPS).

    Use this on anything drawn as many individual shapes -- ``pcolormesh``/
    ``pcolor``/``contourf`` grids, dense ``scatter`` clouds, ``imshow`` of
    very large arrays -- so that a "colormap plot" doesn't get embedded as
    tens of thousands of separate vector polygons. An unrasterized
    ``pcolormesh`` over even a modest 200x200 grid emits 40,000 individual
    quad paths into the PDF, which is both a large file and painfully slow
    for viewers (Preview.app, Acrobat, LaTeX) to render or scroll. Lines,
    text, and axis furniture stay crisp vector output either way -- only
    the artist(s) passed here are affected.

    The rasterized region is still embedded inside the vector file (it's
    not a separate export); it's drawn at whatever ``dpi`` the figure is
    ultimately saved with (600 by default via :func:`savefig`, matching
    the qplt style's ``savefig.dpi``), so it stays print-sharp.

    Parameters
    ----------
    artists:
        A single artist (e.g. what ``ax.pcolormesh(...)`` returns) or an
        iterable of artists (e.g. what ``ax.bar(...)`` returns, or a list
        you've collected yourself).

    Returns
    -------
    The same ``artists`` argument, unchanged, so this can be used inline:

    >>> im = qplt.rasterize(ax.pcolormesh(x, y, z, cmap="qplt:ice"))
    """
    items = [artists] if hasattr(artists, "set_rasterized") else list(artists)
    for artist in items:
        artist.set_rasterized(True)
    return artists


def savefig(
    fig,
    path: str,
    formats: Sequence[str] = ("pdf", "png"),
    dpi: int = 600,
    **kwargs,
):
    """Save ``fig`` to one or more formats sharing the same base name.

    ``path`` may or may not include an extension; any extension given is
    stripped and replaced with each of ``formats``. PDF/SVG are
    recommended for submission (vector, font-embedded per the qplt
    style sheet); PNG at 600 dpi is convenient for quick previews/slides.

    Returns the list of file paths written.
    """
    import os

    base, _ = os.path.splitext(path)
    written = []
    for fmt in formats:
        out_path = f"{base}.{fmt}"
        fig.savefig(out_path, dpi=dpi, **kwargs)
        written.append(out_path)
    return written
