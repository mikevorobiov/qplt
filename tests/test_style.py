import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

import qplt


ALL_STYLES = ["nature", "nature-cm", "daily"]


def test_available_styles():
    assert set(qplt.available_styles()) == set(ALL_STYLES)


@pytest.mark.parametrize("name", ALL_STYLES)
def test_set_style_applies_without_error(name):
    qplt.set_style(name)
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 4])
    plt.close(fig)


@pytest.mark.parametrize(
    "style_name,expected_family",
    [
        ("nature", "sans-serif"),
        ("nature-cm", "serif"),
        ("daily", "serif"),
    ],
)
def test_style_font_family(style_name, expected_family):
    qplt.set_style(style_name)
    assert plt.rcParams["font.family"] == [expected_family]


@pytest.mark.parametrize(
    "style_name,expected_mathtext",
    [
        ("nature", "dejavusans"),
        ("nature-cm", "cm"),
        ("daily", "cm"),
    ],
)
def test_style_mathtext_fontset(style_name, expected_mathtext):
    qplt.set_style(style_name)
    assert plt.rcParams["mathtext.fontset"] == expected_mathtext


def test_cm_variant_matches_base_layout():
    """"nature-cm" should be layout-identical to "nature" -- only the
    typeface changes."""
    layout_keys = [
        "figure.figsize", "axes.linewidth", "axes.spines.top",
        "axes.spines.right", "xtick.direction", "ytick.direction",
        "xtick.top", "ytick.right", "lines.linewidth", "savefig.dpi",
    ]
    qplt.set_style("nature")
    base_values = {k: plt.rcParams[k] for k in layout_keys}
    qplt.set_style("nature-cm")
    cm_values = {k: plt.rcParams[k] for k in layout_keys}
    assert base_values == cm_values


def test_style_context_manager_scopes_and_restores():
    qplt.reset()
    before = dict(plt.rcParams)
    with qplt.style("nature"):
        assert plt.rcParams["font.size"] == 12.0
    # rcParams restored after the context exits
    assert plt.rcParams["font.size"] == before["font.size"]


def test_colormaps_registered():
    qplt.set_style()
    for name in ["qplt:ice", "qplt:ember", "qplt:diverging"]:
        cmap = matplotlib.colormaps[name]
        assert cmap is not None
        rgba = cmap(0.5)
        assert len(rgba) == 4


def test_palette_is_eight_distinct_hex_colors():
    assert len(qplt.PALETTE) == 8
    assert len(set(qplt.PALETTE)) == 8
    for c in qplt.PALETTE:
        assert c.startswith("#") and len(c) == 7


def test_figsize_presets():
    w, h = qplt.figsize("single")
    assert w == pytest.approx(89.0 / 25.4)
    w2, h2 = qplt.figsize("double")
    assert w2 > w


def test_figsize_rejects_unknown_string():
    with pytest.raises(ValueError):
        qplt.figsize("triple")


def test_panel_label_adds_text_artist():
    qplt.set_style()
    fig, ax = plt.subplots()
    n_before = len(ax.texts)
    qplt.panel_label(ax, "a")
    assert len(ax.texts) == n_before + 1
    assert ax.texts[-1].get_text() == "a"
    plt.close(fig)


def test_label_panels_uses_consecutive_letters():
    qplt.set_style()
    fig, axes = plt.subplots(1, 3)
    qplt.label_panels(axes)
    for ax, expected in zip(axes, "abc"):
        assert ax.texts[-1].get_text() == expected
    plt.close(fig)


def test_savefig_writes_multiple_formats(tmp_path):
    qplt.set_style()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    out = qplt.savefig(fig, str(tmp_path / "fig"), formats=("png", "pdf"))
    assert len(out) == 2
    for p in out:
        import os
        assert os.path.exists(p)
        assert os.path.getsize(p) > 0
    plt.close(fig)


def test_fonts_register_without_error():
    families = qplt.fonts.register_fonts()
    assert "Liberation Sans" in families
    assert "Liberation Serif" in families


def test_rasterize_marks_single_artist():
    qplt.set_style()
    fig, ax = plt.subplots()
    xg, yg = np.meshgrid(np.linspace(-1, 1, 5), np.linspace(-1, 1, 5))
    mesh = ax.pcolormesh(xg, yg, xg + yg)
    assert mesh.get_rasterized() is False or mesh.get_rasterized() is None
    returned = qplt.rasterize(mesh)
    assert returned is mesh
    assert mesh.get_rasterized() is True
    plt.close(fig)


def test_rasterize_marks_iterable_of_artists():
    qplt.set_style()
    fig, ax = plt.subplots()
    bars = ax.bar(["a", "b", "c"], [1, 2, 3])
    qplt.rasterize(bars)
    for patch in bars:
        assert patch.get_rasterized() is True
    plt.close(fig)


def test_pcolormesh_smaller_when_rasterized(tmp_path):
    qplt.set_style()
    xg, yg = np.meshgrid(np.linspace(-3, 3, 150), np.linspace(-3, 3, 150))
    field = np.cos(3 * xg) * np.sin(3 * yg)

    fig, ax = plt.subplots()
    ax.pcolormesh(xg, yg, field)
    vector_path = tmp_path / "vector.pdf"
    fig.savefig(vector_path)
    plt.close(fig)

    fig, ax = plt.subplots()
    qplt.rasterize(ax.pcolormesh(xg, yg, field))
    raster_path = tmp_path / "raster.pdf"
    fig.savefig(raster_path)
    plt.close(fig)

    import os
    assert os.path.getsize(raster_path) < os.path.getsize(vector_path) / 2


def test_daily_figure_returns_plot_and_sidebar_axes():
    qplt.set_style("daily")
    fig, ax, side = qplt.daily_figure()
    assert ax in fig.axes
    assert side in fig.axes
    assert ax is not side
    # sidebar should be blank/frameless by default
    assert not side.axison
    plt.close(fig)


def test_daily_figure_rejects_bad_sidebar_width():
    qplt.set_style("daily")
    with pytest.raises(ValueError):
        qplt.daily_figure(sidebar_width=0)
    with pytest.raises(ValueError):
        qplt.daily_figure(sidebar_width=1.5)


def test_sidebar_text_adds_title_and_body_artists():
    qplt.set_style("daily")
    fig, ax, side = qplt.daily_figure()
    n_before = len(side.texts)
    artists = qplt.sidebar_text(side, "Some notes.\n\nMore notes.", title="Notes")
    assert len(side.texts) == n_before + 2  # title + body
    assert artists[0].get_text() == "Notes"
    assert "Some notes." in artists[1].get_text()
    plt.close(fig)


def test_sidebar_text_without_title_adds_one_artist():
    qplt.set_style("daily")
    fig, ax, side = qplt.daily_figure()
    n_before = len(side.texts)
    qplt.sidebar_text(side, "Just a body, no title.")
    assert len(side.texts) == n_before + 1
    plt.close(fig)


def test_sidebar_stats_formats_numbers_and_aligns_labels():
    qplt.set_style("daily")
    fig, ax, side = qplt.daily_figure()
    artists = qplt.sidebar_stats(
        side, {"chi2/dof": 1.0834, "T_c (K)": "92.3(4)", "N": 42}, title="Fit"
    )
    assert artists[0].get_text() == "Fit"
    body = artists[1].get_text()
    assert "1.083" in body  # formatted via the default "{:.4g}" spec
    assert "92.3(4)" in body  # strings pass through verbatim
    assert artists[1].get_fontfamily() == ["monospace"]
    plt.close(fig)


def test_sidebar_stats_accepts_list_of_pairs_and_rejects_empty():
    qplt.set_style("daily")
    fig, ax, side = qplt.daily_figure()
    artists = qplt.sidebar_stats(side, [("a", 1), ("b", 2)])
    assert len(artists) == 1  # no title given
    with pytest.raises(ValueError):
        qplt.sidebar_stats(side, {})
    plt.close(fig)


@pytest.mark.parametrize("style_name", ALL_STYLES)
def test_residual_figure_returns_shared_x_axes_without_sidebar(style_name):
    qplt.set_style(style_name)
    fig, ax, ax_res, side = qplt.residual_figure()
    assert ax in fig.axes and ax_res in fig.axes
    assert side is None
    assert ax.get_shared_x_axes().joined(ax, ax_res)
    plt.close(fig)


def test_residual_figure_hides_main_panel_bottom_labels_persistently():
    qplt.set_style("nature")
    fig, ax, ax_res, _ = qplt.residual_figure()
    # hidden immediately at creation time...
    assert ax.xaxis.get_tick_params()["labelbottom"] is False
    # ...and still hidden after data is added and the figure is drawn
    # (a regression check: naively hiding via setp(get_xticklabels())
    # doesn't survive autoscale creating new tick-label artists)
    ax.plot([0, 1, 2], [0, 1, 4])
    ax_res.plot([0, 1, 2], [0, 0.1, -0.1])
    fig.canvas.draw()
    assert ax.xaxis.get_tick_params()["labelbottom"] is False
    assert ax_res.xaxis.get_tick_params()["labelbottom"] is True
    plt.close(fig)


def test_residual_figure_draws_zero_line_by_default():
    qplt.set_style("nature")
    fig, ax, ax_res, _ = qplt.residual_figure()
    assert len(ax_res.lines) == 1  # the zero line
    plt.close(fig)

    fig, ax, ax_res, _ = qplt.residual_figure(zero_line=False)
    assert len(ax_res.lines) == 0
    plt.close(fig)


def test_residual_figure_with_sidebar():
    qplt.set_style("daily")
    fig, ax, ax_res, side = qplt.residual_figure(sidebar_width=0.28)
    assert side is not None
    assert not side.axison
    assert side in fig.axes
    qplt.sidebar_stats(side, {"chi2/dof": 1.1}, title="Fit")
    plt.close(fig)


def test_residual_figure_rejects_bad_ratios():
    qplt.set_style("nature")
    with pytest.raises(ValueError):
        qplt.residual_figure(height_ratio=0)
    with pytest.raises(ValueError):
        qplt.residual_figure(height_ratio=1)
    with pytest.raises(ValueError):
        qplt.residual_figure(sidebar_width=1.0)
    with pytest.raises(ValueError):
        qplt.residual_figure(sidebar_width=-0.1)
