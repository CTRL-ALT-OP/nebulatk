from typing import Any, List, Optional, TYPE_CHECKING
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import the fonts_manager module
import fonts_manager


def test_create_font():
    assert fonts_manager.Font(None).font == ("Helvetica", -1)

    assert fonts_manager.Font("Arial").font == ("Arial", 10)


@patch("ctypes.windll.gdi32.AddFontResourceExW")
def test_load_font(mock_windll):
    if fonts_manager.ctypes_available:
        assert fonts_manager.loadfont("test.ttf")
