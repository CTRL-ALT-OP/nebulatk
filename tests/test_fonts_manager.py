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
    assert fonts_manager.ctypes_available
    assert fonts_manager.loadfont("test.ttf")


def test_loadfont_unix(monkeypatch):
    # Pretend Windows‐API isn’t available
    monkeypatch.setattr(fonts_manager, "ctypes_available", False)

    # Create a fake _libfc with the same API shape
    class FakeFC:
        def __init__(self):
            self.config = object()
            self.add_calls = []
            self.build_calls = []

        def FcInit(self):
            return True

        def FcConfigGetCurrent(self):
            return self.config

        def FcConfigAppFontAddFile(self, cfg, path_bytes):
            self.add_calls.append((cfg, path_bytes))
            return 1  # success

        def FcConfigBuildFonts(self, cfg):
            self.build_calls.append(cfg)
            return True

    fake = FakeFC()
    monkeypatch.setattr(fonts_manager, "_libfc", fake)

    # Call with a dummy path
    result = fonts_manager.loadfont("/tmp/dummy.ttf")
    assert result is True

    # Verify the calls
    assert fake.add_calls == [(fake.config, b"/tmp/dummy.ttf")]
    assert fake.build_calls == [fake.config]
