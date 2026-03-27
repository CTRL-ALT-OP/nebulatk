import os
import sys
import threading
from unittest.mock import MagicMock
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

from nebulatk import _window_internal


def _mock_widget(hit=True, can_focus=True, children=None):
    widget = MagicMock()
    widget.children = children or []
    widget.can_focus = can_focus
    widget.hit = hit
    return widget


def test_initialization_defaults_and_state():
    window = _window_internal(
        width=800,
        height=600,
        title="Test Window",
        canvas_width=800,
        canvas_height=600,
        closing_command=lambda: None,
        resizable=(True, False),
        override=True,
    )

    assert window.width == 800
    assert window.height == 600
    assert window.title == "Test Window"
    assert window.canvas_width == 800
    assert window.canvas_height == 600
    assert window.resizable == (True, False)
    assert window.override is True
    assert window.render_mode == "image_gl"
    assert window.children == []
    assert window.running is True


def test_render_mode_respects_constructor_argument():
    window = _window_internal(width=800, height=600, render_mode="custom")
    assert window.render_mode == "custom"


def test_taskbar_manager_property_is_read_only():
    window = _window_internal(width=800, height=600)
    with pytest.raises(AttributeError, match="read-only"):
        window.taskbar_manager = object()


def test_find_deepest_hit_prefers_nested_focusable(monkeypatch):
    window = _window_internal(width=800, height=600)

    deep = _mock_widget(hit=True, can_focus=True)
    nested_parent = _mock_widget(hit=True, can_focus=True, children=[deep])
    sibling = _mock_widget(hit=True, can_focus=True)
    window.children = [nested_parent, sibling]

    import bounds_manager

    monkeypatch.setattr(bounds_manager, "check_hit", lambda child, _x, _y: child.hit)
    found = window._find_deepest_hit(window.children, 10, 10)
    assert found is deep


def test_typing_and_typing_up_track_active_keys():
    window = _window_internal(width=800, height=600)
    active = MagicMock()
    window.active = active

    event = MagicMock()
    event.keysym = "a"

    window.typing(event)
    active.typed.assert_called_once_with(event)
    assert "a" in window.active_keys

    window.typing_up(event)
    assert "a" not in window.active_keys


def test_configure_updates_title_resizable_and_background():
    window = _window_internal(width=800, height=600, title="Old")
    window.root = MagicMock()
    window.resize = MagicMock()
    window._window_thread_id = threading.get_ident()

    window.configure(title="New Title", resizable=False, background_color="112233")

    window.root.title.assert_called_once_with("New Title")
    window.root.resizable.assert_called_once_with(False, False)
    window.resize.assert_not_called()
    assert window.title == "New Title"
    assert window.resizable == (False, False)
    assert window.background_color == "#112233"


def test_resize_updates_renderer_and_canvas_dimensions():
    window = _window_internal(width=800, height=600, canvas_width=800, canvas_height=600)
    window.root = MagicMock()
    window.renderer = MagicMock()
    window.display = MagicMock()
    window._apply_resizable_widgets = MagicMock()
    window._window_thread_id = threading.get_ident()

    window.resize(1000, 700)

    assert window.width == 1000
    assert window.height == 700
    assert window.canvas_width == 1000
    assert window.canvas_height == 700
    window.renderer.request_redraw.assert_called()

