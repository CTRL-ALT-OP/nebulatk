import os
import sys

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
