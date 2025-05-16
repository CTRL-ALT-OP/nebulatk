import sys
import os
from unittest.mock import patch
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import the fonts_manager module
import fonts_manager


def test_create_font():
    assert fonts_manager.Font(None).font == ("Helvetica", -1)

    assert fonts_manager.Font("Arial").font == ("Arial", 10)


@pytest.mark.skipif(sys.platform != "win32", reason="windll only on Windows")
@patch("ctypes.windll.gdi32.AddFontResourceExW")
def test_load_font(mock_windll):
    if fonts_manager.ctypes_available:
        assert fonts_manager.loadfont("test.ttf")
