import os
import sys

import pytest
from PIL import Image

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk


def _profile_path(name: str) -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "default_profiles", name)
    )


@pytest.fixture
def light_defaults_path() -> str:
    return _profile_path("defaults_light.py")


@pytest.fixture
def dark_defaults_path() -> str:
    return _profile_path("defaults_dark.py")


def test_window_loads_defaults_file(light_defaults_path: str):
    window = ntk.Window(
        title="Defaults Load",
        width=360,
        height=220,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        expected_fill = ntk.colors_manager.convert_to_hex("#ffffff")
        expected_border = ntk.colors_manager.convert_to_hex("#222222")
        expected_background = ntk.colors_manager.convert_to_hex("#f2f7ff")
        assert window.defaults.default_fill.color == expected_fill
        assert window.defaults.default_border.color == expected_border
        assert window.background_color == expected_background
    finally:
        window.close()


def test_defaults_switch_updates_only_default_bound_values(
    light_defaults_path: str, dark_defaults_path: str
):
    window = ntk.Window(
        title="Defaults Switch",
        width=420,
        height=260,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        bound = ntk.Button(window, text="Bound", width=140, height=40, fill="default").place(
            10, 10
        )
        overridden = ntk.Button(
            window, text="Custom", width=140, height=40, fill="#00ff00"
        ).place(10, 60)

        before_bound = bound.fill
        before_override = overridden.fill

        window.set_defaults(dark_defaults_path)

        assert bound.fill != before_bound
        assert overridden.fill == before_override
    finally:
        window.close()


def test_window_background_updates_when_bound_to_defaults(
    light_defaults_path: str, dark_defaults_path: str
):
    window = ntk.Window(
        title="Background Defaults",
        width=420,
        height=260,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        assert window.background_color == ntk.colors_manager.convert_to_hex("#f2f7ff")
        window.set_defaults(dark_defaults_path)
        assert window.background_color == ntk.colors_manager.convert_to_hex("#0f1729")
    finally:
        window.close()


def test_window_background_explicit_override_stays_fixed(
    light_defaults_path: str, dark_defaults_path: str
):
    window = ntk.Window(
        title="Background Override",
        width=420,
        height=260,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
        background_color="#111111",
    )
    try:
        assert window.background_color == ntk.colors_manager.convert_to_hex("#111111")
        window.set_defaults(dark_defaults_path)
        assert window.background_color == ntk.colors_manager.convert_to_hex("#111111")
        window.configure(background_color="default")
        assert window.background_color == ntk.colors_manager.convert_to_hex("#0f1729")
    finally:
        window.close()


def test_styles_inherit_and_update_when_defaults_change(
    light_defaults_path: str, dark_defaults_path: str
):
    window = ntk.Window(
        title="Style Update",
        width=520,
        height=300,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        button_1 = ntk.Button(
            window,
            style=window.defaults.button_1,
            width=140,
            height=40,
            text="style-1",
        ).place(10, 10)
        button_2 = ntk.Button(
            window,
            style=window.defaults.button_2,
            width=140,
            height=40,
            text="style-2",
        ).place(10, 60)
        overridden = ntk.Button(
            window,
            style=window.defaults.button_1,
            width=140,
            height=40,
            text="override",
            fill="#aa00aa",
        ).place(10, 110)

        assert button_1.border_width == 2
        assert button_2.border_width == 2
        assert button_2.fill != button_1.fill
        overridden_fill = overridden.fill

        window.set_defaults(dark_defaults_path)

        assert button_1.fill == ntk.colors_manager.convert_to_hex("#30435f")
        assert button_2.fill == ntk.colors_manager.convert_to_hex("#4b5f39")
        assert overridden.fill == overridden_fill
    finally:
        window.close()


def test_default_font_reflows_on_resize_until_explicit_override(light_defaults_path: str):
    window = ntk.Window(
        title="Font Reflow",
        width=520,
        height=320,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        button = ntk.Button(
            window,
            text="Resize Me",
            font="default",
            width=120,
            height=36,
        ).place(10, 10)

        size_before = button.font[1]
        button.width = 240
        button.height = 72
        size_after_resize = button.font[1]
        assert size_after_resize >= size_before

        button.font = ("Helvetica", 13, "normal")
        button.width = 300
        button.height = 110
        assert button.font[1] == 13
    finally:
        window.close()


def test_image_widgets_default_background_is_transparent(
    light_defaults_path: str, tmp_path
):
    image_path = tmp_path / "pixel.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(image_path)

    window = ntk.Window(
        title="Image Defaults",
        width=320,
        height=220,
        render_mode="image_gl",
        fps=30,
        defaults_file=light_defaults_path,
    )
    try:
        button = ntk.Button(
            window,
            image=str(image_path),
            width=40,
            height=40,
            fill="default",
            border="default",
            border_width=3,
        ).place(10, 10)
        assert button.fill is None
        assert button.border is None
        assert button.border_width == 0
    finally:
        window.close()
