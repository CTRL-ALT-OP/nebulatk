try:
    from . import image_manager
    from . import fonts_manager
    from . import bounds_manager
    from . import colors_manager
except ImportError:
    import image_manager
    import fonts_manager
    import bounds_manager
    import colors_manager


# Define the names of objects
IMAGE_OBJECTS = [
    "image_object",
    "active_object",
    "hover_object",
    "hover_object_active",
]

BG_OBJECTS = ["bg_object", "bg_object_active"]

TEXT_OBJECTS = [
    "text_object",
    "active_text_object",
]

SLIDER_OBJECTS = ["slider_object", "slider_bg_object"]

ALL_OBJECTS = IMAGE_OBJECTS + BG_OBJECTS + TEXT_OBJECTS  # + SLIDER_OBJECTS


def check(_object, attribute):
    """Check if the given attribute is defined and is not None.

    Args:
        _object (nebulatk.Widget): widget
        attribute (str): attribute

    Returns:
        bool: Returns True if both checks are satisfied, False otherwise
    """
    return bool(hasattr(_object, attribute) and getattr(_object, attribute) is not None)


# Unfortunately not included in the python math library
def clamp(number, minimum=0, maximum=0):
    """Implement clamp method

    Args:
        number (int): Number to clamp
        minimum (int, optional): Floor. Defaults to 0.
        maximum (int, optional): Ceiling. Defaults to 0.

    Returns:
        int: Clamped number
    """
    number = min(number, maximum)
    number = max(number, minimum)

    return number


def rel_position_to_abs(_object, x, y):
    # Add up positions for relative offsets in parent tree
    obj = _object
    while obj.root != obj.master:
        x += obj.root.x
        y += obj.root.y
        obj = obj.root
    return x, y


def abs_position_to_rel(_object, x, y):
    # Add up positions for relative offsets in parent tree
    obj = _object
    while obj.root != obj.master:
        x -= obj.root.x
        y -= obj.root.y
        obj = obj.root
    return x, y


# ============================================================ FLOPS ======================================================================
# NOTE: Flops hide all items of a type, and shows the selected item


def image_flop(_object, val):
    """Hides all images, and shows the selected image

    Args:
        _object (nebulatk.Widget): widget
        val (str): Item to show
    """
    visible = "normal" if _object.visible else "hidden"
    if check(_object, val):
        for obj in IMAGE_OBJECTS:
            if hasattr(_object, obj):
                if val == obj:
                    _object.master.change_state(getattr(_object, obj), state=visible)
                else:
                    _object.master.change_state(getattr(_object, obj), state="hidden")


def bg_flop(_object, val):
    """Hides all background objects, and shows the selected background object

    Args:
        _object (nebulatk.Widget): widget
        val (str): Item to show
    """
    visible = "normal" if _object.visible else "hidden"
    for obj in BG_OBJECTS:
        if check(_object, obj):
            if val == obj:
                _object.master.change_state(getattr(_object, obj), state=visible)
            else:
                _object.master.change_state(getattr(_object, obj), state="hidden")


def text_flop(_object, val):
    """Hides all text objects, and shows the selected text object

    Args:
        _object (nebulatk.Widget): widget
        val (str): Item to show
    """
    visible = "normal" if _object.visible else "hidden"
    if hasattr(_object, val) and getattr(_object, val) is not None:
        for obj in TEXT_OBJECTS:
            if hasattr(_object, obj):
                if val == obj:
                    _object.master.change_state(getattr(_object, obj), state=visible)
                else:
                    _object.master.change_state(getattr(_object, obj), state="hidden")


def flop_off(_object):
    """Hides all objects

    Args:
        _object (nebulatk.Widget): widget
    """
    for obj in ALL_OBJECTS:
        if hasattr(_object, obj):
            _object.master.change_state(getattr(_object, obj), state="hidden")


def flop_on(_object):
    """Shows all objects

    Args:
        _object (nebulatk.Widget): widget
    """
    visible = "normal" if _object.visible else "hidden"
    if _object.state:
        if _object.hovering:
            image_flop(_object, "hover_object_active")
        else:
            image_flop(_object, "active_object")
    elif _object.hovering:
        image_flop(_object, "hover_object")
    else:
        image_flop(_object, "image_object")
    if _object.bg_object_active is not None and _object.state:
        bg_flop(_object, "bg_object_active")

    else:
        bg_flop(_object, "bg_object")

    if _object.active_text_object is not None and _object.state:
        text_flop(_object, "active_text_object")
    else:
        text_flop(_object, "text_object")

    # _object.master.change_state(_object.slider_bg_object, visible)


# ============================================================ STANDARD WIDGET MANAGMENT METHODS ==========================================


# ------------------------------------------------------------ DELETION BEHAVIOUR -----------------------------------------------------------


def delete(_object):
    """Widget deletion behaviour

    Args:
        _object (nebulatk.Widget): widget
    """
    # Iterate through all items in the widget and delete them if they exist
    for obj in ALL_OBJECTS:
        if check(_object, obj):
            _object.master.delete(getattr(_object, obj))
            setattr(_object, obj, None)


# ------------------------------------------------------------ HOVERING BEHAVIOUR -----------------------------------------------------------


def hovered_standard(_object):
    """Widget hover behaviour for standard type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        image_flop(_object, "hover_object")
        if _object.bg_object_active is not None:
            bg_flop(_object, "bg_object_active")
        if _object.active_text_object is not None:
            text_flop(_object, "active_text_object")


def hovered_toggle(_object):
    """Widget hover behaviour for toggle type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        if _object.state:
            image_flop(_object, "hover_object_active")
        else:
            image_flop(_object, "hover_object")


def hover_end(_object):
    """Widget hover end behaviour for all widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        if _object.state:
            image_flop(_object, "active_object")
        else:
            image_flop(_object, "image_object")
            if _object.active_text_object is not None:
                text_flop(_object, "text_object")
        if _object.bg_object_active is not None:
            bg_flop(_object, "bg_object")


# ------------------------------------------------------------ TOGGLE BEHAVIOUR -------------------------------------------------------------


def toggle_object_standard(_object):
    """Widget toggle behaviour for standard type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    _object.state = not _object.state
    if _object.hovering:
        image_flop(_object, "hover_object_active")
    else:
        image_flop(_object, "active_object")


def toggle_object_toggle(_object):
    """Widget toggle behaviour for toggle type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    _object.state = not _object.state
    if _object.state:
        if _object.hovering:
            image_flop(_object, "hover_object_active")
        else:
            image_flop(_object, "active_object")

    elif _object.hovering:
        image_flop(_object, "hover_object")
    else:
        image_flop(_object, "image_object")
    if check(_object, "bg_object_active"):
        if not _object.state:
            bg_flop(_object, "bg_object")

        else:
            bg_flop(_object, "bg_object_active")

    if check(_object, "active_text_object"):
        if not _object.state:
            text_flop(_object, "text_object")

        else:
            text_flop(_object, "active_text_object")


# ------------------------------------------------------------ CLICK BEHAVIOUR --------------------------------------------------------------


def clicked_standard(_object):
    """Widget click behaviour for standard type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        toggle_object_standard(_object)
        if _object.command is not None:
            _object.command()


def clicked_toggle(_object):
    """Widget click behaviour for toggle type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        toggle_object_toggle(_object)

        if _object.command is not None and _object.state:
            _object.command()
        if _object.command_off is not None and not _object.state:
            _object.command_off()
        elif _object.command is not None and not _object.state:
            _object.command()


# ------------------------------------------------------------ POSITION BEHAVIOURS ----------------------------------------------------------


def _update_position(_object, item, x, y, old_x, old_y):
    """Internal update_position method

    Args:
        _object (nebulatk.Widget): widget
        item (str): item
        x (int): x position
        y (int): y position
    """
    if check(_object, item):
        if item.find("image") != -1:
            x += _object.border_width / 2
            y += _object.border_width / 2
        _object.master.object_place(getattr(_object, item), x, y)


def update_positions(_object, x, y, avoid_slider=False):
    """Update positions of all objects

    Args:
        _object (nebulatk.Widget): widget
        x (int): x position
        y (int): y position
        avoid_slider (bool, optional): Request to avoid touching the slider background objects. Defaults to False.
    """
    x, y = rel_position_to_abs(_object, x, y)
    old_x, old_y = rel_position_to_abs(_object, _object.x, _object.y)

    for obj in ALL_OBJECTS:
        if obj == "slider_bg_object" and avoid_slider:
            continue
        _update_position(_object, obj, x, y, old_x, old_y)


# ------------------------------------------------------------ PLACEMENT BEHAVIOURS ---------------------------------------------------------


def place_bulk(_object, x, y):
    """Bulk place objects

    Args:
        _object (nebulatk.Widget): widget
    """
    x, y = rel_position_to_abs(_object, x, y)
    # Only place background rectangles if there == a fill or border
    # Place slider_bg_object
    colors = _object._colors
    state = "normal" if _object.visible else "hidden"
    """if colors["slider_fill"] is not None or (
        colors["slider_border"] is not None and _object.slider_border_width != 0
    ):
        _object.slider_bg_object = _object.master.create_rectangle(
            x,
            y + _object.height / 2 - _object.slider_height / 2,
            x + _object.maximum + _object.width,
            y + _object.height / 2 - _object.slider_height / 2 + _object.slider_height,
            fill=_object.slider_fill,
            border_width=_object.slider_border_width,
            outline=_object.slider_border,
            state=state,
        )"""
    # Place bg_object
    if _object.fill is not None or (
        _object.border is not None and _object.border_width != 0
    ):
        _object.bg_object = _object.master.create_rectangle(
            x,
            y,
            x + _object.width,
            y + _object.height,
            fill=_object.fill,
            border_width=_object.border_width,
            outline=_object.border,
            state=state,
        )

    # Place bg_object_active
    if _object.active_fill is not None:
        _object.bg_object_active = _object.master.create_rectangle(
            x,
            y,
            x + _object.width,
            y + _object.height,
            fill=_object.active_fill,
            border_width=_object.border_width,
            outline=_object.border,
            state="hidden",
        )

    # Place images
    for img in ["image", "active_image", "hover_image", "active_hover_image"]:
        if check(_object, img):
            state = "hidden"
            img_object = img.split("_")[0] + "_object"
            if img == "image" and _object.visible:
                state = "normal"
            if img == "active_hover_image":
                img_object = "hover_object_active"

            setattr(
                _object,
                img_object,
                _object.master.create_image(
                    x + _object.border_width,
                    y + _object.border_width,
                    getattr(_object, img),
                    state=state,
                ),
            )

    # Place text objects
    if _object.text != "":
        generate_text(_object, x, y)


def generate_text(_object, x, y):
    state = "normal" if _object.visible else "hidden"
    # Set x offset and anchor based on justify
    if _object.justify == "center":
        local_x = x + (_object.width / 2)
        anchor = "center"

    elif _object.justify == "left":
        local_x = x
        anchor = "w"

    elif _object.justify == "right":
        local_x = x + _object.width
        anchor = "e"

    # Set y offset
    local_y = y + (_object.height / 2)

    _object.text_object = _object.master.create_text(
        local_x,
        local_y,
        text=_object.text,
        font=_object.font,
        fill=_object.text_color,
        anchor=anchor,
        state=state,
        angle=_object.angle,
    )
    if _object.active_text_color is not None:
        _object.active_text_object = _object.master.create_text(
            local_x,
            local_y,
            text=_object.text,
            font=_object.font,
            fill=_object.active_text_color,
            anchor=anchor,
            state="hidden",
        )
