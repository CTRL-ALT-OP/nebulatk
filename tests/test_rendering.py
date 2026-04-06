import os
import sys
from types import SimpleNamespace

import pytest
from PIL import Image as PILImage

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import native_gl_window
import opengl_image_display


class _FakeGlfw:
    KEY_BACKSPACE = 8
    KEY_DELETE = 46
    KEY_LEFT = 263
    KEY_RIGHT = 262
    KEY_HOME = 268
    KEY_END = 269
    KEY_LEFT_SHIFT = 340
    KEY_RIGHT_SHIFT = 344
    KEY_LEFT_CONTROL = 341
    KEY_RIGHT_CONTROL = 345
    KEY_LEFT_SUPER = 343
    KEY_RIGHT_SUPER = 347
    KEY_A = 65
    KEY_Z = 90
    PRESS = 1
    REPEAT = 2
    RELEASE = 0
    MOD_CONTROL = 0x0002
    MOD_ALT = 0x0004
    MOD_SUPER = 0x0008

    @staticmethod
    def get_key_name(key, _scancode):
        return {321: "kp_1", _FakeGlfw.KEY_A: "a"}.get(key)


def test_key_name_helpers_match(monkeypatch):
    monkeypatch.setattr(native_gl_window, "glfw", _FakeGlfw)

    for key in (_FakeGlfw.KEY_BACKSPACE, _FakeGlfw.KEY_A, 321, 999):
        assert native_gl_window._native_window_process_key_name(
            key
        ) == native_gl_window.NativeGLWindow._key_name(object(), key)


def test_should_dispatch_keypress_event_uses_char_callback_for_plain_text(monkeypatch):
    monkeypatch.setattr(native_gl_window, "glfw", _FakeGlfw)

    assert native_gl_window._should_dispatch_keypress_event("a", "a", 0) is False
    assert native_gl_window._should_dispatch_keypress_event("A", "a", 0) is False
    assert (
        native_gl_window._should_dispatch_keypress_event("a", "a", _FakeGlfw.MOD_CONTROL)
        is True
    )
    assert native_gl_window._should_dispatch_keypress_event("BackSpace", "", 0) is True


def test_build_key_event_uses_glfw_key_name(monkeypatch):
    monkeypatch.setattr(native_gl_window, "glfw", _FakeGlfw)
    event = native_gl_window._build_key_event(10, 20, _FakeGlfw.KEY_A, 0)

    assert event.x == 10
    assert event.y == 20
    assert event.keysym == "a"
    assert event.char == "a"


def test_text_input_char_helper():
    assert native_gl_window._is_text_input_char("A") is True
    assert native_gl_window._is_text_input_char("\n") is False
    assert native_gl_window._is_text_input_char("Left") is False


def test_opengl_image_display_proxy_show_frame_submits_bytes():
    root = SimpleNamespace(submit_frame=lambda *_args: None)
    root.submit_frame_calls = []

    def _capture_submit(frame_rgba, width, height):
        root.submit_frame_calls.append((frame_rgba, width, height))

    root.submit_frame = _capture_submit
    display = opengl_image_display.OpenGLImageDisplay(root=root, width=1, height=1)

    frame = PILImage.new("RGBA", (3, 2), (10, 20, 30, 40))
    display.show_frame(frame)

    assert len(root.submit_frame_calls) == 1
    frame_rgba, width, height = root.submit_frame_calls[0]
    assert width == 3
    assert height == 2
    assert len(frame_rgba) == 3 * 2 * 4
    assert frame_rgba[:4] == bytes([10, 20, 30, 40])


def test_opengl_image_display_show_frame_sets_local_upload_state():
    display = opengl_image_display.OpenGLImageDisplay.__new__(
        opengl_image_display.OpenGLImageDisplay
    )
    display._proxy_mode = False
    display.width = 0
    display.height = 0
    display._frame_rgba = None
    display._needs_texture_upload = False

    frame = PILImage.new("RGBA", (4, 3), (1, 2, 3, 255))
    display.show_frame(frame)

    assert display.width == 4
    assert display.height == 3
    assert display._frame_rgba is not None
    assert len(display._frame_rgba) == 4 * 3 * 4
    assert display._needs_texture_upload is True

    display.show_frame_bytes(b"\x01\x02\x03\x04", 1, 1)
    assert display.width == 1
    assert display.height == 1
    assert display._frame_rgba == b"\x01\x02\x03\x04"
    assert display._needs_texture_upload is True


def test_opengl_image_display_draw_is_noop_in_proxy_mode():
    display = opengl_image_display.OpenGLImageDisplay.__new__(
        opengl_image_display.OpenGLImageDisplay
    )
    display._proxy_mode = True

    # Should return immediately without touching GLFW/GL state.
    assert display.draw() is None


def test_handle_process_message_records_startup_error():
    window = native_gl_window.NativeGLWindow.__new__(native_gl_window.NativeGLWindow)
    window._window_id = "native-test"
    window._startup_error = None

    window._handle_process_message(
        {"type": "error", "window_id": "native-test", "reason": "glfw.init failed"}
    )
    assert window._startup_error == "glfw.init failed"


def test_wait_for_process_ready_raises_with_startup_error():
    window = native_gl_window.NativeGLWindow.__new__(native_gl_window.NativeGLWindow)
    window._hwnd = 0
    window._startup_error = "glfw.create_window() failed."
    window._process_events = lambda: None
    window._process = SimpleNamespace(is_alive=lambda: False)

    with pytest.raises(RuntimeError, match="glfw.create_window\\(\\) failed\\."):
        window._wait_for_process_ready()
