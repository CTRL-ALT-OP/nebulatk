from math import sin, asin, cos, radians, sqrt

# Define the names of objects
IMAGE_OBJECTS = [
    "image_object",
    "active_object",
    "hover_object",
    "hover_object_active",
]

BG_OBJECTS = [
    "bg_object",
    "bg_object_active",
    "bg_object_hover",
    "bg_object_hover_active",
]

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


def sign(x):
    return (1, -1)[x < 0]


def rel_position_to_abs(_object, x, y):
    # Add up positions for relative offsets in parent tree
    obj = _object
    while hasattr(obj, "root") and hasattr(obj, "master") and obj.root != obj.master:
        # Safety check: only add position if root has x and y attributes
        if hasattr(obj.root, "x") and hasattr(obj.root, "y"):
            x += obj.root.x
            y += obj.root.y
        obj = obj.root
    return x, y


def abs_position_to_rel(_object, x, y):
    # Add up positions for relative offsets in parent tree
    obj = _object
    while hasattr(obj, "root") and hasattr(obj, "master") and obj.root != obj.master:
        # Safety check: only subtract position if root has x and y attributes
        if hasattr(obj.root, "x") and hasattr(obj.root, "y"):
            x -= obj.root.x
            y -= obj.root.y
        obj = obj.root
    return x, y


def get_line_point_rel(angle, length):
    bx = length * sin(angle)
    by = length * cos(angle)
    return bx, by


def offset_point(a, _a, _b):
    bx = a[0] + _b
    by = a[1] + _a
    return bx, by


def normalize_angle(angle):
    return (360 + angle) % 360


def get_rect_points(_object):
    """Gets 4 points of a rectangle, given the object's position and orientation"""

    x, y = rel_position_to_abs(_object, _object.x, _object.y)
    a = (x, y)

    # Normalize angle to be within [0, 360)
    angle = normalize_angle(_object.orientation)

    # Convert angle to radians for trigonometric functions
    rad_angle = radians(angle)

    _a, _b = get_line_point_rel(rad_angle, _object.width)

    b = offset_point(a, _a, _b)

    _a2, _b2 = get_line_point_rel(rad_angle, _object.height)

    d = offset_point(a, _b2, -_a2)

    c = offset_point(d, _a, _b)

    return a, b, c, d


def get_rel_point_rect(_object, x, y):
    """Returns the relative point in a rectangle given a pair of absolute coordinates, and compensating for rotation"""
    a = rel_position_to_abs(_object, _object.x, _object.y)
    a1 = y - a[1]
    b1 = x - a[0]
    signs = (sign(b1), sign(a1))
    c = sqrt(pow(a1, 2) + pow(b1, 2))
    if c == 0:
        return 0, 0
    B = asin(a1 / c)
    A = radians(normalize_angle(_object.orientation))

    A2 = A - B

    bx = c * signs[0] * abs(cos(A2))
    by = c * signs[1] * abs(sin(A2))

    return int(round(bx)), int(round(by))


def get_rect_area(_object):
    return _object.width * _object.height


def get_triangle_area(a, b, c):
    """Gets the area of a triangle, given 3 points"""
    return (
        abs(
            (b[0] * a[1] - a[0] * b[1])
            + (c[0] * b[1] - b[0] * c[1] + a[0] * c[1] - c[0] * a[1])
        )
        / 2
    )


# ============================================================ FLOPS ======================================================================
# NOTE: Flops now update widget state and active variants. They no longer
# toggle visibility between multiple backend render objects.


def _globally_visible(_object):
    global_visible = True
    root = _object
    while hasattr(root, "root") and root.root != root:
        if not getattr(root, "visible", True):
            global_visible = False
            break
        root = root.root
    return (
        global_visible
        and getattr(_object, "visible", True)
        and getattr(_object, "_render_visible", True)
    )


def _resolve_image_for_slot(_object, slot):
    image_by_slot = {
        "image_object": "image",
        "active_object": "active_image",
        "hover_object": "hover_image",
        "hover_object_active": "active_hover_image",
    }
    fallback = {
        "hover_object_active": ["active_hover_image", "hover_image", "active_image", "image"],
        "hover_object": ["hover_image", "image"],
        "active_object": ["active_image", "image"],
        "image_object": ["image"],
    }
    for image_attr in fallback.get(slot, [image_by_slot.get(slot, "image")]):
        if check(_object, image_attr):
            return getattr(_object, image_attr)
    return None


def _resolve_bg_for_slot(_object, slot):
    color_by_slot = {
        "bg_object": "fill",
        "bg_object_active": "active_fill",
        "bg_object_hover": "hover_fill",
        "bg_object_hover_active": "active_hover_fill",
    }
    fallback = {
        "bg_object_hover_active": ["active_hover_fill", "hover_fill", "active_fill", "fill"],
        "bg_object_hover": ["hover_fill", "fill"],
        "bg_object_active": ["active_fill", "fill"],
        "bg_object": ["fill"],
    }
    for color_attr in fallback.get(slot, [color_by_slot.get(slot, "fill")]):
        value = getattr(_object, color_attr, None)
        if value is not None:
            return value
    return None


def _resolve_text_fill_for_slot(_object, slot):
    if slot == "active_text_object":
        return getattr(_object, "active_text_color", None) or getattr(
            _object, "text_color", None
        )
    return getattr(_object, "text_color", None)


def _request_redraw(_object):
    requester = getattr(_object, "master", None)
    if requester is not None and hasattr(requester, "request_redraw"):
        requester.request_redraw()


def _sync_image_state(_object):
    _request_redraw(_object)


def _sync_bg_state(_object):
    _request_redraw(_object)


def _sync_text_state(_object):
    _request_redraw(_object)


def image_flop(_object, val):
    """Select active image variant for the widget."""
    _object._active_image_slot = val
    _sync_image_state(_object)


def bg_flop(_object, val):
    """Select active background variant for the widget."""
    _object._active_bg_slot = val
    _sync_bg_state(_object)


def text_flop(_object, val):
    """Select active text style variant for the widget."""
    _object._active_text_slot = val
    _sync_text_state(_object)


def _first_available_bg(_object, candidates):
    for candidate in candidates:
        if candidate:
            return candidate
    return None


def _get_bg_target(_object, hovering=False):
    return _first_available_bg(
        _object,
        [
            "bg_object_hover_active" if hovering and _object.state else None,
            "bg_object_hover" if hovering else None,
            "bg_object_active" if _object.state else None,
            "bg_object",
        ],
    )


def _apply_background_state(_object, hovering=None):
    target = _get_bg_target(_object, _object.hovering if hovering is None else hovering)
    if target:
        bg_flop(_object, target)


def flop_off(_object):
    """Hide widget render output without backend state toggles."""
    _object._render_visible = False
    _sync_image_state(_object)
    _sync_bg_state(_object)
    _sync_text_state(_object)


def flop_on(_object):
    """Show widget render output and sync active variants."""
    _object._render_visible = True
    if _object.state:
        if _object.hovering:
            image_flop(_object, "hover_object_active")
        else:
            image_flop(_object, "active_object")
    elif _object.hovering:
        image_flop(_object, "hover_object")
    else:
        image_flop(_object, "image_object")
    _apply_background_state(_object)

    if getattr(_object, "active_text_color", None) is not None and _object.state:
        text_flop(_object, "active_text_object")
    else:
        text_flop(_object, "text_object")

    # _object.master.change_state(_object.slider_bg_object, visible)


# ============================================================ STANDARD WIDGET MANAGMENT METHODS ==========================================


# ------------------------------------------------------------ DELETION BEHAVIOUR -----------------------------------------------------------


def delete(_object, delayed=False):
    """Widget deletion behaviour

    Args:
        _object (nebulatk.Widget): widget
    """
    if delayed:
        return
    for obj in ALL_OBJECTS:
        if hasattr(_object, obj):
            setattr(_object, obj, None)
    _request_redraw(_object)


# ------------------------------------------------------------ DELETION SCHEDULING BEHAVIOUR -----------------------------------------------
def schedule_delete(_object):
    return


def delete_scheduled(_object):
    _object._scheduled_deletion = []


# ------------------------------------------------------------ HOVERING BEHAVIOUR -----------------------------------------------------------


def hovered_standard(_object):
    """Widget hover behaviour for standard type widgets

    Args:
        _object (nebulatk.Widget): widget
    """
    if _object.visible:
        image_flop(_object, "hover_object")
        _apply_background_state(_object, hovering=True)
        if getattr(_object, "active_text_color", None) is not None:
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
        _apply_background_state(_object, hovering=True)


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
            if getattr(_object, "active_text_color", None) is not None:
                text_flop(_object, "text_object")
        _apply_background_state(_object, hovering=False)


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
    _apply_background_state(_object)


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
    _apply_background_state(_object)
    if not _object.state:
        bg_flop(_object, "bg_object")
    else:
        bg_flop(_object, "bg_object_active")

    if getattr(_object, "active_text_color", None) is not None:
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


def update_positions(_object, x, y, avoid_slider=False):
    """Update positions of all objects

    Args:
        _object (nebulatk.Widget): widget
        x (int): x position
        y (int): y position
        avoid_slider (bool, optional): Request to avoid touching the slider background objects. Defaults to False.
    """
    _object._position = [int(x), int(y)]
    _request_redraw(_object)


# ------------------------------------------------------------ PLACEMENT BEHAVIOURS ---------------------------------------------------------


def place_bulk(_object, x, y):
    """Bulk place objects

    Args:
        _object (nebulatk.Widget): widget
    """
    _object._position = [int(x), int(y)]
    flop_on(_object)
    _request_redraw(_object)


def generate_text(_object, x, y):
    _request_redraw(_object)
