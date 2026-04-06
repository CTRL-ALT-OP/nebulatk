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
    assert fonts_manager.Font("default").font == ("Helvetica", -1)

    assert fonts_manager.Font("Arial").font == ("Arial", 10)


def test_create_font_rejects_invalid_type():
    with pytest.raises(TypeError):
        fonts_manager.Font(123)


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


def test_windows_font_resolver_prefers_style(monkeypatch):
    catalog = (
        {
            "family_token": "timesnewroman",
            "style_tokens": set(),
            "path": r"C:\Windows\Fonts\times.ttf",
        },
        {
            "family_token": "timesnewroman",
            "style_tokens": {"bold"},
            "path": r"C:\Windows\Fonts\timesbd.ttf",
        },
    )
    monkeypatch.setattr(fonts_manager, "_windows_font_catalog", lambda: catalog)
    assert (
        fonts_manager._resolve_windows_font_path("Times New Roman", "bold")
        == r"C:\Windows\Fonts\timesbd.ttf"
    )
    assert (
        fonts_manager._resolve_windows_font_path("Times New Roman", "normal")
        == r"C:\Windows\Fonts\times.ttf"
    )


def test_get_font_debug_info_reports_selected_candidate(monkeypatch):
    class DummyFont:
        path = r"C:\Windows\Fonts\arial.ttf"

    monkeypatch.setattr(
        fonts_manager, "_font_candidates", lambda family, style: (["arial.ttf"], None)
    )
    monkeypatch.setattr(fonts_manager.ImageFont, "truetype", lambda candidate, size: DummyFont())
    info = fonts_manager.get_font_debug_info(("Arial", 12, "normal"))

    assert info["requested_family"] == "Arial"
    assert info["requested_size"] == 12
    assert info["selected_candidate"] == "arial.ttf"
    assert info["loaded_font_path"] == r"C:\Windows\Fonts\arial.ttf"
    assert info["used_default_font"] is False


def test_resolve_draw_font_normalizes_missing_style(monkeypatch):
    captured = {}
    token = object()

    def fake_load(family, size, style):
        captured["family"] = family
        captured["size"] = size
        captured["style"] = style
        return token

    monkeypatch.setattr(fonts_manager, "_load_font", fake_load)

    resolved = fonts_manager.resolve_draw_font(("Arial", 12))
    assert resolved is token
    assert captured == {"family": "Arial", "size": 12, "style": "normal"}


def test_resolve_draw_font_falls_back_on_invalid_font(monkeypatch):
    captured = {}
    token = object()

    def fake_load(family, size, style):
        captured["family"] = family
        captured["size"] = size
        captured["style"] = style
        return token

    monkeypatch.setattr(fonts_manager, "_load_font", fake_load)

    resolved = fonts_manager.resolve_draw_font(123)
    assert resolved is token
    assert captured == {"family": "arial", "size": 12, "style": "normal"}


def test_get_font_debug_info_uses_shared_selection_path(monkeypatch):
    dummy_info = {
        "requested_family": "Arial",
        "requested_size": 12,
        "requested_style": "normal",
        "windows_resolved_path": None,
        "candidate_chain": ["arial.ttf"],
        "selected_candidate": "arial.ttf",
        "loaded_font": object(),
        "loaded_font_path": r"C:\Windows\Fonts\arial.ttf",
        "used_default_font": False,
    }
    monkeypatch.setattr(
        fonts_manager, "_resolve_font_selection", lambda _family, _size, _style: dummy_info
    )

    info = fonts_manager.get_font_debug_info(("Arial", 12, "normal"))
    assert info["requested_family"] == "Arial"
    assert info["requested_size"] == 12
    assert info["requested_style"] == "normal"
    assert info["selected_candidate"] == "arial.ttf"
