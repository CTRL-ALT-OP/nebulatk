import os
import sys

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk


class _ClipboardRoot:
    def __init__(self):
        self._clipboard = ""

    def after(self, _delay_ms, callback, *args):
        callback(*args)

    def update(self):
        return None

    def clipboard_clear(self):
        self._clipboard = ""

    def clipboard_append(self, text):
        self._clipboard += str(text)

    def clipboard_get(self):
        return self._clipboard


@pytest.fixture
def canvas() -> ntk.Window:
    """Create a test window for widget testing."""
    window = ntk._window_internal(
        title="Test Window",
        width=800,
        height=500,
        render_mode="image_gl",
        fps=60,
    )
    window.root = _ClipboardRoot()
    yield window
    window.close_animations()
