import sys
import os
from unittest.mock import patch
import pytest
import importlib
import types

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


class FuncStub:
    def __init__(self, fn):
        self._fn = fn

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


class DummyFC:
    def __init__(self):
        self.inited = False
        self.config = object()
        self.add_calls = []
        self.build_calls = []
        self.FcInit = FuncStub(self._fcinit)
        self.FcConfigGetCurrent = FuncStub(self._getcurrent)
        self.FcConfigAppFontAddFile = FuncStub(self._addfile)
        self.FcConfigBuildFonts = FuncStub(self._buildfonts)

    def _fcinit(self):
        self.inited = True
        return True

    def _getcurrent(self):
        return self.config

    def _addfile(self, cfg, path_bytes):
        self.add_calls.append((cfg, path_bytes))
        return 1  # non-zero == success

    def _buildfonts(self, cfg):
        self.build_calls.append(cfg)
        return True


def test_loadfont_linux_branch(monkeypatch):
    # A container to hold the DummyFC instance when LoadLibrary is called:
    created = {}

    # Build a stub 'ctypes' module
    stub_ctypes = types.ModuleType("ctypes")

    # Replace LoadLibrary with one that saves its DummyFC and returns it
    def fake_load(name):
        inst = DummyFC()
        created["fc"] = inst
        return inst

    stub_ctypes.cdll = types.SimpleNamespace(LoadLibrary=fake_load)
    stub_ctypes.c_char_p = __import__("ctypes").c_char_p
    stub_ctypes.c_void_p = __import__("ctypes").c_void_p

    # Stub out ctypes.util.find_library
    stub_ctypes_util = types.ModuleType("ctypes.util")
    stub_ctypes_util.find_library = lambda name: "libfontconfig.so.1"

    # Inject our stubs
    monkeypatch.setitem(sys.modules, "ctypes", stub_ctypes)
    monkeypatch.setitem(sys.modules, "ctypes.util", stub_ctypes_util)
    sys.modules.pop("fonts_manager", None)

    # Re-import under test
    fm = importlib.import_module("fonts_manager")
    assert fm.ctypes_available is False

    # Call loadfont — our fake_load will have run, populating `created['fc']`
    ok = fm.loadfont("/tmp/foo.ttf")
    assert ok is True

    # Grab the exact instance that the module used
    dummy = created["fc"]
    # Now assert directly on *our* dummy
    assert dummy.add_calls == [(dummy.config, b"/tmp/foo.ttf")]
    assert dummy.build_calls == [dummy.config]
