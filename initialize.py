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

# ============================================================ INITIALIZATION METHODS ======================================================================


def load_initial(
    _object,
    root,
    width,
    height,
    border_width,
    justify=None,
    state=False,
    mode=None,
    command=None,
    command_off=None,
    slider_height=10,
    maximum=100,
    minimum=0,
    slider_border_width=0,
):
    """Initial loading for nebulatk widgets.

    Args:
        _object (nebulatk.Widget): widget
        root (nebulatk.Window): root window
        width (int): width
        height (int): height
        border_width (int): border width
        justify (str, optional): Justification for text. Defaults to None.
        state (bool, optional): Defaults to False.
        mode (int, optional): Defaults to None.
        command (function, optional): Defaults to None.
        command_off (function, optional): Defaults to None.
        slider_height (int, optional): Defaults to 10.
        maximum (int, optional): Defaults to 100.
        minimum (int, optional): Defaults to 0.
        slider_border_width (int, optional): Defaults to 0.
    """
    # Set root and master, to make parenting widgets to other widgets easier in the future
    _object.root = root
    _object.master = root.master

    # Set width and height, ensuring they are integers
    _object.width = int(width)
    _object.height = int(height)
    _object.slider_height = int(slider_height)

    # Set slider minimum and maximum values, ensuring they are integers
    _object.minimum = int(minimum)
    _object.maximum = int(maximum)

    # Set border, ensuring border_width values are integers
    _object.border_width = int(border_width)
    _object.slider_border_width = int(slider_border_width)

    # Initialize text variables
    _object.text = ""
    _object.original_text = ""
    _object.justify = justify

    # Set state and mode
    _object.state = state
    _object.mode = mode

    # Set commands
    _object.command = command
    _object.command_off = command_off

    # Initialize other variables to their defaults
    _object.visible = True
    _object.hovering = False

    _object.x = 0
    _object.y = 0

    _object.original_x = 0
    _object.original_y = 0

    _object.end = 0

    _object.object = None
    _object.slider_object = None
    _object.slider_bg_object = None
    _object.bg_object = None
    _object.bg_object_active = None
    _object.text_object = None
    _object.active_text_object = None
    _object.image_object = None


def load_text(_object, text, font):
    """Initializes text for nebulatk widgets

    Args:
        _object (nebulatk.Widget): widget
        text (str): text
        font (tuple): font tuple
    """
    if text != "":
        # Generate font
        if font == None:
            # Default font
            font = ("Helvetica", int(_object.width / len(text)))

        # If only font name is specified
        if type(font) == str:
            font = (font, int(_object.width / len(text)))

        # Get minimum size of widget
        min_width, min_height = fonts_manager.get_min_button_size(
            _object.master, font, text
        )

        # If the widget size is not specified, set it to the minimum size
        if _object.width == 0:
            _object.width = min_width
        if _object.height == 0:
            _object.height = min_height

        # Check if the font size is the default font size
        # If so, set it to the max font size possible for the widget size
        if font == (font[0], int(_object.width / len(text))):
            font = (
                font[0],
                fonts_manager.get_max_font_size(
                    _object.master, font, _object.width, _object.height, text
                ),
            )

    _object.text = text
    _object.entire_text = text
    _object.font = font


def load_bounds_type(_object, bounds_type, image=None):
    """Initialize bounds_type for nebulatk widgets

    Args:
        _object (nebulatk.Widget): widget
        bounds_type (str): bounds type
        image (_type_, optional): Image. Defaults to None.
    """
    # If the bounds type is the default, determine which default is required
    if bounds_type == "default":
        if image is None:
            bounds_type = "box"
        else:
            bounds_type = "non-standard"
    _object.bounds_type = bounds_type


def load_bulk_images(_object, **kwargs):
    """Load all images specified

    Args:
        _object (nebulatk.Widget): widget
        kwargs: Image name = image path
    """
    pil_images = {}

    for arg in kwargs:
        # Load image
        img, pil_img = image_manager.load_image(_object, kwargs[arg], True)

        # Load it into the widget
        setattr(_object, arg, img)
        pil_images[arg] = pil_img

    # Generate non-standard bounds if necessary
    if _object.image is not None:
        if _object.bounds_type == "non-standard":
            _object.bounds = bounds_manager.generate_bounds_for_nonstandard_image(
                pil_images["image"]
            )

        # New width and height is the image size
        _object.width, _object.height = pil_images["image"].size
        _object.width += _object.border_width*2
        _object.height += _object.border_width*2


def load_all_colors(
    _object,
    fill="default",
    active_fill="default",
    border="default",
    text_color="default",
    active_text_color=None,
    slider_fill=None,
    slider_border=None,
):
    """Load all colors into nebulatk widgets

    Args:
        _object (nebulatk.Widget): widget
        fill (color, optional): Fill color. Defaults to "default".
        active_fill (color, optional): Active fill color. Defaults to "default".
        border (color, optional): Border color. Defaults to "default".
        text_color (color, optional): Text color. Defaults to "default".
        active_text_color (color, optional): Active text color. Defaults to None.
        slider_fill (color, optional): Slider fill color. Defaults to None.
        slider_border (color, optional): Slider border color. Defaults to None.
    """
    # Generate default colors
    if _object.image == None:
        if fill == "default":
            fill = "white"

        if active_fill == "default":
            if fill == None:
                active_fill = None

            else:
                # Make active_fill distinct from fill if it is default
                if colors_manager.check_full_white_or_black(fill) == 1:
                    active_fill = colors_manager.darken(fill, 40)
                else:
                    active_fill = colors_manager.brighten(fill, 40)

        if border == "default":
            border = "black"

    # Set colors to none if default and an image is specified
    else:
        if fill == "default":
            fill = None
        if active_fill == "default":
            active_fill = None
        if border == "default":
            border = None

    # Set remaining defaults
    if text_color == "default":
        text_color = "black"

    if slider_fill == "default":
        slider_fill = "gray"
    if slider_border == "default":
        slider_border = None

    # Load colors into widget

    _object.fill = fill
    _object.active_fill = active_fill
    _object.slider_fill = slider_fill

    _object.border = border
    _object.slider_border = slider_border

    _object.text_color = text_color
    _object.active_text_color = active_text_color


# Transform all colors to hex for uniformity
def convert_all_colors(_object):
    """Transform all colors to hex for uniformity

    Args:
        _object (nebulatk.Widget): widget
    """
    _object.fill = colors_manager.convert_to_hex(_object.fill)
    _object.active_fill = colors_manager.convert_to_hex(_object.active_fill)
    _object.border = colors_manager.convert_to_hex(_object.border)
    _object.text_color = colors_manager.convert_to_hex(_object.text_color)
    _object.active_text_color = colors_manager.convert_to_hex(_object.active_text_color)
    _object.slider_fill = colors_manager.convert_to_hex(_object.slider_fill)
    _object.slider_border = colors_manager.convert_to_hex(_object.slider_border)
