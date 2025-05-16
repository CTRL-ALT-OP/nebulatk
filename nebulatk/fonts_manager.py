from tkinter import font as tkfont
from tkinter import Tk
import math

ctypes_available = True
try:
    from ctypes import windll, byref, create_unicode_buffer
except Exception as e:
    print(e)
    ctypes_available = False

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20


class Font:
    def __init__(self, font: str):
        if font in {"default", None}:
            # Default font
            self.font = ("Helvetica", -1)

        # If only font name is specified
        if type(font) is str:
            self.font = (font, 10)

        elif type(font) in (list, tuple):
            # Assume font is (font, size)
            self.font = font


def measure_text(root, font, text):
    """Measure the width of text with the given font.

    Args:
        root: The root tk window or nebulatk window (.root attribute)
        font: A tuple containing the font name, size, and optionally a style
        text (str): The text to measure

    Returns:
        int: The width of the text in pixels
    """
    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    if not isinstance(root, Tk):
        root = root.root

    return tkfont.Font(root, font=font).measure(text)


def get_font_metrics(root, font, metric="linespace"):
    """Get font metrics such as linespace.

    Args:
        root: The root tk window or nebulatk window (.root attribute)
        font: A tuple containing the font name, size, and optionally a style
        metric (str): The metric to retrieve. Defaults to "linespace"

    Returns:
        int: The requested metric value
    """
    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    if not isinstance(root, Tk):
        root = root.root

    return tkfont.Font(root, font=font).metrics(metric)


def loadfont(fontpath, private=True, enumerable=False):
    if not ctypes_available:
        return
    """Load a font into resources so that a process can use it

    Args:
        fontpath (str): Path to the font
        private (bool, optional): Whether this font should be private to this process. Defaults to True.
        enumerable (bool, optional): Enumerable. Defaults to False.

    Raises:
        TypeError: Fontpath must be of type str

    Returns:
        bool: Success of loading specified font
    """
    if not isinstance(fontpath, str):
        raise TypeError("Fontpath must be of type str")

    # Generate buffer and load the font resources
    pathbuf = create_unicode_buffer(fontpath)
    AddFontResourceEx = windll.gdi32.AddFontResourceExW
    # Generate flags
    flags = (FR_PRIVATE if private else 0) | (0 if enumerable else FR_NOT_ENUM)

    # Add fonts to resource, and return number of fonts added successfully
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)

    # Return success based on number of fonts added
    return bool(numFontsAdded)


def get_max_font_size(root, font, width, height, text):
    """Find the maximum font size for a given font and dimensions.

    Args:
        root (nebulatk.Window): The base window created by nebulatk.Window()
        font (tuple): A tuple containing the font name, size, and optionally a style
        width (int): The width of the bounding rectangle
        height (int): The height of the bounding rectangle
        text (str): The text that needs to fit in the bounding rectangle

    Returns:
        int: The maximum font size
    """

    # Set size to 90% of total widget size
    width *= 0.9
    height *= 0.9

    # The code will generate the maximum font size that can fit in the width, and a separate font size for the height

    # This size will be the font size for the width
    size = 1
    prev_size = 0

    # This size will be the font size for the width
    size2 = 1
    prev_size2 = 0

    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    # Generate starting width of text given the font size
    curr_width = measure_text(root, (font[0], size, font[2]), text)

    # Generate starting height of text given the font size2
    curr_height = get_font_metrics(root, (font[0], size, font[2]), "linespace")

    # Gradually increase size until the width of the text exceeds the bounds
    while curr_width < width:
        prev_size = size
        size += 1
        curr_width = measure_text(root, (font[0], size, font[2]), text)

    # Gradually increase size2 until the height of the text exceeds the bounds, or until size2 reaches size1
    while curr_height < height and size2 <= prev_size:
        prev_size2 = size2
        size2 += 1
        curr_height = get_font_metrics(root, (font[0], size2, font[2]), "linespace")

    # Final font
    # font = tkfont.Font(root.root, font=(font[0], prev_size2, font[2]), text=text)

    # Return last valid size
    return prev_size2


def get_min_button_size(root, font, text):
    """Find the minimum size of a button with a specified font and text. Returns width, height.

    Args:
        root (nebulatk.Window): The base window created by nebulatk.Window()
        font (tuple): A tuple containing the font name, size, and optionally a style
        text (str): The text that needs to fit in the bounding rectangle

    Returns:
        width (int): The minimum width of the button
        height (int): The minimum height of the button
    """

    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    # Minimum width is 110% of the width of the given font and text
    width = int(math.ceil(measure_text(root, font, text) / 0.9))

    # Minimum height is 110% of the height of the given font and text
    height = int(math.ceil(get_font_metrics(root, font, "linespace") / 0.9))

    return width, height


def get_max_length(root, text, font, width, end=0):
    """Generate the maximum slice of text that can fit in a fixed width

    Args:
        root (nebulatk.Window): root window
        text (str): text
        font (tuple): font
        width (int): width
        end (int, optional): Slice end position. Defaults to 0.

    Returns:
        _type_: _description_
    """

    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    # Initialize length of slice to be the maximum length of the text
    length = len(text)

    # Get the current width of the slice
    curr_width = measure_text(root, font, text[end - length : end])

    # Decrease length of slice until it fits
    while curr_width > width and length > 0:
        length -= 1
        curr_width = measure_text(root, font, text[end - length : end])

    # Return slice length
    return length


# Symbol sets

ALPHA = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

i_e = len(ALPHA)
ALPHA.extend(str.upper(ALPHA[i]) for i in range(i_e))
NUMERIC = list("12345567890")
SYMBOL = list("`~!@#$%^&*()_+-={}[]|\\:\";',.></? ")
ALPHANUMERIC = ALPHA + NUMERIC
ALPHANUMERIC_PLUS = ALPHANUMERIC + SYMBOL
