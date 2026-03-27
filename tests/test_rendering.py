import os
import sys
from types import SimpleNamespace

from PIL import Image as PILImage

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import rendering


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

    @staticmethod
    def get_key_name(key, _scancode):
        return {321: "kp_1"}.get(key)


def test_key_name_helpers_match(monkeypatch):
    monkeypatch.setattr(rendering, "glfw", _FakeGlfw)

    for key in (_FakeGlfw.KEY_BACKSPACE, _FakeGlfw.KEY_A, 321, 999):
        assert rendering._native_window_process_key_name(key) == rendering.NativeGLWindow._key_name(
            object(), key
        )


def test_opengl_image_display_proxy_show_frame_submits_bytes():
    root = SimpleNamespace(submit_frame=lambda *_args: None)
    root.submit_frame_calls = []

    def _capture_submit(frame_rgba, width, height):
        root.submit_frame_calls.append((frame_rgba, width, height))

    root.submit_frame = _capture_submit
    display = rendering.OpenGLImageDisplay(root=root, width=1, height=1)

    frame = PILImage.new("RGBA", (3, 2), (10, 20, 30, 40))
    display.show_frame(frame)

    assert len(root.submit_frame_calls) == 1
    frame_rgba, width, height = root.submit_frame_calls[0]
    assert width == 3
    assert height == 2
    assert len(frame_rgba) == 3 * 2 * 4
    assert frame_rgba[:4] == bytes([10, 20, 30, 40])


def test_opengl_image_display_show_frame_sets_local_upload_state():
    display = rendering.OpenGLImageDisplay.__new__(rendering.OpenGLImageDisplay)
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
    display = rendering.OpenGLImageDisplay.__new__(rendering.OpenGLImageDisplay)
    display._proxy_mode = True

    # Should return immediately without touching GLFW/GL state.
    assert display.draw() is None
