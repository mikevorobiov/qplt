"""Font bundling and registration for qplt.

We bundle the Liberation Sans / Liberation Serif families (SIL Open Font
License 1.1 -- see ``qplt/fonts/OFL.txt``). These are metric-compatible
drop-in replacements for Arial and Times New Roman respectively, which
means text set in Liberation Sans lines up character-for-character with
text set in Arial at the same size -- so figures look correct whether or
not the "real" commercial fonts are installed on the machine that opens
them, and swapping one for the other never reflows a layout.

If a system does have Arial/Helvetica/Times installed, matplotlib's
default font-fallback (``font.sans-serif`` / ``font.serif`` lists in the
style sheets) will generally prefer those automatically; the bundled fonts
just guarantee a consistent, correctly-metriced fallback everywhere else.
"""

from __future__ import annotations

from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fontfiles"

_BUNDLED_FILENAMES = [
    "LiberationSans-Regular.ttf",
    "LiberationSans-Bold.ttf",
    "LiberationSans-Italic.ttf",
    "LiberationSans-BoldItalic.ttf",
    "LiberationSerif-Regular.ttf",
    "LiberationSerif-Bold.ttf",
    "LiberationSerif-Italic.ttf",
    "LiberationSerif-BoldItalic.ttf",
]

_registered = False


def bundled_font_paths() -> list[Path]:
    """Return the filesystem paths of the fonts shipped inside this package."""
    return [FONTS_DIR / name for name in _BUNDLED_FILENAMES if (FONTS_DIR / name).exists()]


def register_fonts(extra_paths: list[str] | None = None) -> list[str]:
    """Register bundled (and optionally extra) font files with matplotlib's
    font manager, so they're discoverable by family name (e.g.
    ``"Liberation Sans"``) even if not installed at the OS level.

    Parameters
    ----------
    extra_paths:
        Additional ``.ttf``/``.otf`` file paths to register, e.g. real
        Arial/Helvetica files the user has a license to use locally.

    Returns
    -------
    A list of the font family names that were successfully registered.
    """
    global _registered
    import matplotlib.font_manager as fm

    registered_families = []
    paths = [str(p) for p in bundled_font_paths()] + list(extra_paths or [])
    for path in paths:
        try:
            fm.fontManager.addfont(path)
            registered_families.append(fm.FontProperties(fname=path).get_name())
        except (FileNotFoundError, RuntimeError):
            continue

    _registered = True
    return registered_families


def available_families() -> set[str]:
    """Set of all font family names matplotlib currently knows about."""
    import matplotlib.font_manager as fm

    return {f.name for f in fm.fontManager.ttflist}


def preferred_sans_stack() -> list[str]:
    """Best-effort ordered font.sans-serif fallback list: prefer a real
    Arial/Helvetica if the system has one, else fall back to the bundled
    metric-compatible Liberation Sans, else matplotlib's built-in DejaVu Sans.
    """
    have = available_families()
    stack = []
    for name in ("Arial", "Helvetica", "Helvetica Neue"):
        if name in have:
            stack.append(name)
    stack.append("Liberation Sans")
    stack.append("DejaVu Sans")
    return stack


def preferred_serif_stack() -> list[str]:
    """Same idea as :func:`preferred_sans_stack`, for serif (Times-like) text."""
    have = available_families()
    stack = []
    for name in ("Times New Roman", "Times"):
        if name in have:
            stack.append(name)
    stack.append("Liberation Serif")
    stack.append("DejaVu Serif")
    return stack
