import os
import sys
from types import SimpleNamespace

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import rendering
import pil_image_renderer


def _make_widget(x, y, width, height, fill, visible=True):
    return SimpleNamespace(
        x=x,
        y=y,
        width=width,
        height=height,
        fill=fill,
        visible=visible,
        _render_visible=True,
        border_width=0,
        border=None,
        text="",
        font=None,
        children=[],
    )


def _make_renderer(children, fps=10):
    window = SimpleNamespace(children=children)
    return rendering.PILImageRenderer(window=window, width=20, height=20, fps=fps)


def test_render_if_due_returns_none_before_frame_interval(monkeypatch):
    now = [10.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])

    renderer = _make_renderer(children=[])
    renderer._last_render = now[0]
    renderer._redraw_requested = True

    assert renderer.render_if_due() is None
    assert renderer._redraw_requested is True


def test_render_if_due_updates_last_render_without_redraw(monkeypatch):
    now = [20.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])

    renderer = _make_renderer(children=[])
    renderer._last_render = 0.0
    renderer._redraw_requested = False

    frame = renderer.render_if_due()
    assert frame is None
    assert renderer._last_render == now[0]
    assert renderer.last_frame.size == (20, 20)


def test_render_if_due_draws_frame_and_clears_redraw(monkeypatch):
    widget = _make_widget(2, 2, 6, 6, "#2244ccff")
    renderer = _make_renderer(children=[widget])

    now = [30.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])
    renderer._last_render = 0.0
    renderer._redraw_requested = True

    frame = renderer.render_if_due()
    assert frame is not None
    assert renderer.last_frame is frame
    assert renderer._redraw_requested is False

    pixel = frame.getpixel((4, 4))
    assert pixel[0] < 80
    assert pixel[1] < 120
    assert pixel[2] > 150
    assert pixel[3] > 0


def test_render_children_respects_front_to_back_order(monkeypatch):
    # children[0] is top-most for hit testing; renderer draws reversed(children),
    # so the first child should win in overlap regions.
    top = _make_widget(4, 4, 10, 10, "#ff0000ff")
    bottom = _make_widget(0, 0, 12, 12, "#0000ffff")
    renderer = _make_renderer(children=[top, bottom], fps=1)

    now = [40.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])
    renderer._last_render = 0.0
    renderer._redraw_requested = True

    frame = renderer.render_if_due()
    assert frame is not None

    overlap = frame.getpixel((6, 6))
    bottom_only = frame.getpixel((1, 1))
    assert overlap == (255, 0, 0, 255)
    assert bottom_only == (0, 0, 255, 255)


def test_render_children_skips_invisible_widgets(monkeypatch):
    hidden_top = _make_widget(0, 0, 12, 12, "#ff0000ff", visible=False)
    visible_bottom = _make_widget(0, 0, 12, 12, "#00ff00ff", visible=True)
    renderer = _make_renderer(children=[hidden_top, visible_bottom], fps=1)

    now = [50.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])
    renderer._last_render = 0.0
    renderer._redraw_requested = True

    frame = renderer.render_if_due()
    assert frame is not None

    pixel = frame.getpixel((6, 6))
    assert pixel == (0, 255, 0, 255)


def test_container_layers_clip_children_and_overlay_in_order(monkeypatch):
    class Container:
        pass

    container = Container()
    container.x = 2
    container.y = 2
    container.width = 10
    container.height = 10
    container.fill = None
    container.visible = True
    container._render_visible = True
    container.border_width = 0
    container.border = None
    container.text = ""
    container.font = None

    clipped_child = _make_widget(-4, 1, 8, 8, "#ff0000ff")
    container.children = [clipped_child]

    background = _make_widget(0, 0, 20, 20, "#0000ffff")
    renderer = _make_renderer(children=[container, background], fps=1)

    now = [60.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])
    renderer._last_render = 0.0
    renderer._redraw_requested = True

    frame = renderer.render_if_due()
    assert frame is not None

    assert frame.getpixel((3, 4)) == (255, 0, 0, 255)
    # Would be red without container clipping.
    assert frame.getpixel((7, 4)) == (0, 0, 255, 255)
    assert frame.getpixel((1, 4)) == (0, 0, 255, 255)


def test_renderer_uses_public_font_resolver(monkeypatch):
    widget = _make_widget(1, 1, 16, 10, None)
    widget.text = "Hi"
    widget.font = ("Arial", 12)
    widget.text_color = "#000000ff"
    widget.justify = "center"

    captured = {"font_spec": None}
    original_resolve = pil_image_renderer.fonts_manager.resolve_draw_font

    def spy(font_spec):
        captured["font_spec"] = font_spec
        return original_resolve(font_spec)

    monkeypatch.setattr(pil_image_renderer.fonts_manager, "resolve_draw_font", spy)

    renderer = _make_renderer(children=[widget], fps=1)
    renderer._last_render = 0.0
    renderer._redraw_requested = True
    frame = renderer.render_if_due()

    assert frame is not None
    assert captured["font_spec"] == ("Arial", 12)
