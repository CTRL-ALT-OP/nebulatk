import os
import sys
from unittest.mock import MagicMock

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk

_window_internal = ntk._window_internal


def _make_window(fps=60):
    window = _window_internal(width=320, height=200, render_mode="image_gl", fps=fps)
    window.root = MagicMock()
    window.root.after = MagicMock()
    window.renderer = MagicMock()
    window.display = MagicMock()
    window._sync_window_size_from_native = MagicMock()
    return window


def test_render_tick_skips_rendering_while_batching():
    window = _make_window(fps=50)
    window._render_batch_depth = 1

    window._render_tick()

    window._sync_window_size_from_native.assert_called_once()
    window.renderer.render_if_due.assert_not_called()
    window.display.show_frame.assert_not_called()
    window.root.after.assert_called_once_with(20, window._render_tick)


def test_render_tick_shows_frame_and_clears_redraw_flag():
    window = _make_window(fps=40)
    window._render_batch_depth = 0
    window._redraw_needed = True
    frame = object()
    window.renderer.render_if_due.return_value = frame

    window._render_tick()

    window._sync_window_size_from_native.assert_called_once()
    window.renderer.render_if_due.assert_called_once()
    window.display.show_frame.assert_called_once_with(frame)
    assert window._redraw_needed is False
    window.root.after.assert_called_once_with(25, window._render_tick)


def test_render_tick_reschedules_when_no_frame_ready():
    window = _make_window(fps=30)
    window._render_batch_depth = 0
    window._redraw_needed = True
    window.renderer.render_if_due.return_value = None

    window._render_tick()

    window._sync_window_size_from_native.assert_called_once()
    window.renderer.render_if_due.assert_called_once()
    window.display.show_frame.assert_not_called()
    assert window._redraw_needed is True
    window.root.after.assert_called_once_with(33, window._render_tick)
