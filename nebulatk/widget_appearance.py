"""Shared widget appearance resolution helpers for rendering/state logic."""

from __future__ import annotations


IMAGE_SLOT_FALLBACKS = {
    "hover_object_active": [
        "active_hover_image",
        "hover_image",
        "active_image",
        "image",
    ],
    "hover_object": ["hover_image", "image"],
    "active_object": ["active_image", "image"],
    "image_object": ["image"],
}

BG_SLOT_FALLBACKS = {
    "bg_object_hover_active": [
        "active_hover_fill",
        "hover_fill",
        "active_fill",
        "fill",
    ],
    "bg_object_hover": ["hover_fill", "fill"],
    "bg_object_active": ["active_fill", "fill"],
    "bg_object": ["fill"],
}


def safe_getattr(obj, name, default=None):
    try:
        return getattr(obj, name)
    except Exception:
        return default


def is_widget_visible(widget, parent_visible=True):
    return (
        parent_visible
        and safe_getattr(widget, "visible", True)
        and safe_getattr(widget, "_render_visible", True)
    )


def resolve_slot_value(widget, slot, fallback_map, default_attrs):
    attrs = fallback_map.get(slot, list(default_attrs))
    for attr in attrs:
        value = safe_getattr(widget, attr, None)
        if value is not None:
            return value
    return None


def resolve_image(widget):
    slot = safe_getattr(widget, "_active_image_slot", "image_object")
    value = resolve_slot_value(widget, slot, IMAGE_SLOT_FALLBACKS, ("image",))
    if value is None:
        return None
    return safe_getattr(value, "image", value)


def resolve_fill(widget):
    slot = safe_getattr(widget, "_active_bg_slot", "bg_object")
    return resolve_slot_value(widget, slot, BG_SLOT_FALLBACKS, ("fill",))


def resolve_text_fill(widget):
    slot = safe_getattr(widget, "_active_text_slot", "text_object")
    if slot == "active_text_object":
        return safe_getattr(widget, "active_text_color", None) or safe_getattr(
            widget, "text_color", None
        )
    return safe_getattr(widget, "text_color", None)


def to_rgba(color):
    if color is None:
        return None
    if isinstance(color, tuple):
        if len(color) == 4:
            return color
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
    if isinstance(color, str):
        value = color.strip().lstrip("#")
        if len(value) == 6:
            return (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                255,
            )
        if len(value) == 8:
            return (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                int(value[6:8], 16),
            )
    return color
