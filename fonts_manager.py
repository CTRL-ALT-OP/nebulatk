from tkinter import font as tkfont
import math
from ctypes import windll, byref, create_unicode_buffer

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20


def loadfont(fontpath, private=True, enumerable=False):
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
    # Check that the font is a string
    if isinstance(fontpath, str):
        # Generate buffer and load the font resources
        pathbuf = create_unicode_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError("Fontpath must be of type str")

    # Generate flags
    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)

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
    curr_width = tkfont.Font(
        root.root, font=(font[0], size, font[2]), text=text
    ).measure(text)

    # Generate starting height of text given the font size2
    curr_height = tkfont.Font(
        root.root, font=(font[0], size, font[2]), text=text
    ).metrics("linespace")

    # Gradually increase size until the width of the text exceeds the bounds
    while curr_width < width:
        prev_size = size
        size += 1
        curr_width = tkfont.Font(
            root.root, font=(font[0], size, font[2]), text=text
        ).measure(text)

    # Gradually increase size2 until the height of the text exceeds the bounds, or until size2 reaches size1
    while curr_height < height and size2 <= prev_size:
        prev_size2 = size2
        size2 += 1
        curr_height = tkfont.Font(
            root.root, font=(font[0], size2, font[2]), text=text
        ).metrics("linespace")

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
    width = int(
        math.ceil(tkfont.Font(root.root, font=font, text=text).measure(text) / 0.9)
    )

    # Minimum height is 110% of the height of the given font and text
    height = int(
        math.ceil(
            tkfont.Font(root.root, font=font, text=text).metrics("linespace") / 0.9
        )
    )

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
    curr_width = tkfont.Font(
        root.root, font=font, text=text[end - length : end]
    ).measure(text[end - length : end])

    # Decrease length of slice until it fits
    while curr_width > width and length > 0:
        length -= 1
        curr_width = tkfont.Font(
            root.root, font=font, text=text[end - length : end]
        ).measure(text[end - length : end])

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

# Append upper case symbols to ALPHA
i = 0
i_e = len(ALPHA)
while i < i_e:
    ALPHA.append(str.upper(ALPHA[i]))
    i += 1

NUMERIC = list("12345567890")
SYMBOL = list("`~!@#$%^&*()_+-={}[]|\:\";',.></? ")
ALPHANUMERIC = ALPHA + NUMERIC
ALPHANUMERIC_PLUS = ALPHANUMERIC + SYMBOL
