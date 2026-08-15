"""Color palettes and colormaps for qplt.

Palettes are original hand-tuned selections designed to evoke the muted,
precise color language common in Nature Physics figures: moderately
saturated, mid-to-dark tones (no neon defaults), and colorblind-conscious
hue spacing (informed by Okabe-Ito hue separation principles, but not a
copy of that specific palette).

Everything here is plain data + small helpers -- no bundled third-party
palette code.
"""

from __future__ import annotations

from matplotlib.colors import LinearSegmentedColormap, ListedColormap

# ---------------------------------------------------------------------------
# Qualitative palette -- for categorical series (lines, scatter groups, bars)
# ---------------------------------------------------------------------------
QUALITATIVE = {
    "indigo": "#1F5C99",
    "vermillion": "#C1441C",
    "teal": "#1B8A82",
    "amber": "#E8A63C",
    "violet": "#6B4C9A",
    "slate": "#55595C",
    "rose": "#C24B7C",
    "olive": "#7A9A3C",
}

# Ordered list, used as the default axes color cycle.
QUALITATIVE_ORDER = [
    "indigo",
    "vermillion",
    "teal",
    "amber",
    "violet",
    "rose",
    "olive",
    "slate",
]

PALETTE = [QUALITATIVE[name] for name in QUALITATIVE_ORDER]

# A softer, lower-contrast variant for dense scatter or fill areas.
PALETTE_MUTED = [
    "#5B84AD",
    "#C97A5C",
    "#5AA39D",
    "#E3BE7C",
    "#9481B3",
    "#C97F9E",
    "#A2B87C",
    "#8B9092",
]

# ---------------------------------------------------------------------------
# Sequential colormap -- single hue, light to dark (heatmaps, density plots)
# ---------------------------------------------------------------------------
_ICE_STOPS = [
    "#F4F8FB",
    "#CADCEB",
    "#8FB3D6",
    "#4E82B3",
    "#1F5C99",
    "#123A66",
    "#081B33",
]
ice = LinearSegmentedColormap.from_list("qplt:ice", _ICE_STOPS, N=256)

_EMBER_STOPS = [
    "#FFF6EC",
    "#FBDDB0",
    "#F2AE5E",
    "#DC7A2E",
    "#C1441C",
    "#8A2A13",
    "#4D1409",
]
ember = LinearSegmentedColormap.from_list("qplt:ember", _EMBER_STOPS, N=256)

# ---------------------------------------------------------------------------
# Diverging colormap -- blue / white / vermillion (colorblind-friendlier
# alternative to red-green diverging maps)
# ---------------------------------------------------------------------------
_DIVERGING_STOPS = [
    "#123A66",
    "#1F5C99",
    "#8FB3D6",
    "#F5F1EA",
    "#EAAE8C",
    "#C1441C",
    "#6E2410",
]
diverging = LinearSegmentedColormap.from_list(
    "qplt:diverging", _DIVERGING_STOPS, N=256
)

# Discrete (listed) version of the qualitative palette, usable as a colormap
# e.g. for a small number of categories mapped via BoundaryNorm.
qualitative_cmap = ListedColormap(PALETTE, name="qplt:qualitative")

CMAPS = {
    "qplt:ice": ice,
    "qplt:ember": ember,
    "qplt:diverging": diverging,
    "qplt:qualitative": qualitative_cmap,
}


def register_colormaps() -> None:
    """Register all qplt colormaps (and their reversed variants) with
    matplotlib's global colormap registry, so they can be retrieved with
    ``matplotlib.colormaps["qplt:ice"]`` / ``plt.get_cmap(...)``.

    Safe to call more than once (re-registration of an existing name is
    skipped rather than raising).
    """
    import matplotlib as mpl

    for name, cmap in CMAPS.items():
        for candidate_name, candidate_cmap in (
            (name, cmap),
            (f"{name}_r", cmap.reversed()),
        ):
            try:
                mpl.colormaps.register(candidate_cmap, name=candidate_name)
            except ValueError:
                # Already registered (e.g. set_style() called twice).
                pass


def get_palette(muted: bool = False) -> list[str]:
    """Return the default ordered qualitative color list.

    Parameters
    ----------
    muted:
        If True, return the softer/lower-contrast variant.
    """
    return list(PALETTE_MUTED if muted else PALETTE)
