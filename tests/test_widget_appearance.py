import os
import sys
from types import SimpleNamespace

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import standard_methods
import widget_appearance
import pil_image_renderer


def _renderer():
    return pil_image_renderer.PILImageRenderer(
        window=SimpleNamespace(children=[]), width=10, height=10, fps=60
    )


def test_image_slot_resolution_matches_renderer_and_standard_methods():
    widget = SimpleNamespace(
        image="base",
        active_image="active",
        hover_image="hover",
        active_hover_image="hover-active",
        _active_image_slot="hover_object_active",
    )
    renderer = _renderer()

    assert widget_appearance.resolve_image(widget) == "hover-active"
    assert renderer._resolve_image(widget) == "hover-active"
    assert (
        standard_methods._resolve_image_for_slot(widget, "hover_object_active")
        == "hover-active"
    )


def test_fill_slot_resolution_matches_renderer_and_standard_methods():
    widget = SimpleNamespace(
        fill="#001122",
        active_fill="#334455",
        hover_fill="#667788",
        active_hover_fill="#99aabbcc",
        _active_bg_slot="bg_object_hover_active",
    )
    renderer = _renderer()

    assert widget_appearance.resolve_fill(widget) == "#99aabbcc"
    assert renderer._resolve_fill(widget) == (153, 170, 187, 204)
    assert (
        standard_methods._resolve_bg_for_slot(widget, "bg_object_hover_active")
        == "#99aabbcc"
    )


def test_text_slot_resolution_matches_renderer_and_standard_methods():
    widget = SimpleNamespace(
        text_color="#112233",
        active_text_color="#445566",
        _active_text_slot="active_text_object",
    )
    renderer = _renderer()

    assert widget_appearance.resolve_text_fill(widget) == "#445566"
    assert renderer._resolve_text_fill(widget) == (68, 85, 102, 255)
    assert (
        standard_methods._resolve_text_fill_for_slot(widget, "active_text_object")
        == "#445566"
    )


def test_global_visibility_still_requires_parent_chain_visible():
    root = SimpleNamespace(visible=True)
    root.root = root
    parent = SimpleNamespace(root=root, visible=False, _render_visible=True)
    child = SimpleNamespace(root=parent, visible=True, _render_visible=True)

    assert widget_appearance.is_widget_visible(child, True) is True
    assert standard_methods._globally_visible(child) is False
