import sys
import os
from unittest.mock import patch, ANY
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
    assert fonts_manager.ctypes_available
    assert fonts_manager.loadfont("test.ttf")


@pytest.mark.skipif(sys.platform == "win32", reason="windll only on Windows")
@patch("libfc.FcConfigAppFontAddFile")
@patch("libfc.FcConfigBuildFonts")
def test_load_font_linux(mock_libfc, mock_libfc_dir):
    assert not fonts_manager.ctypes_available
    assert fonts_manager.loadfont("test.ttf")
    mock_libfc.assert_called_once_with(ANY, "test.ttf")
    mock_libfc_dir.assert_called_once_with(ANY)
