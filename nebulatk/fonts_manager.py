import math
from tkinter import font as tkfont, Tk

# Detect Windows
ctypes_available = True
try:
    from ctypes import windll, byref, create_unicode_buffer
except ImportError:
    ctypes_available = False
    from ctypes import cdll, c_char_p, c_void_p
    from ctypes.util import find_library

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

# ——— Prepare Fontconfig if on UNIX ———
if not ctypes_available:
    # Try to load the library once at import-time
    libfc_path = find_library("fontconfig") or "libfontconfig.so.1"
    try:
        _libfc = cdll.LoadLibrary(libfc_path)
    except OSError as e:
        print(e)
        _libfc = None
    else:
        # initialize Fontconfig
        if not _libfc.FcInit():
            raise RuntimeError("Fontconfig FcInit() failed")
        # configure restypes
        _libfc.FcConfigGetCurrent.restype = c_void_p  # opaque pointer
        # FcConfigAppFontAddFile takes (FcConfig*, const char*)
        _libfc.FcConfigAppFontAddFile.argtypes = (c_void_p, c_char_p)
        # FcConfigBuildFonts takes (FcConfig*)
        _libfc.FcConfigBuildFonts.argtypes = (c_void_p,)
else:
    _libfc = None


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
        # Handle Container objects - access the window's root
        if hasattr(root, "_window"):
            # For nested containers, traverse to the top-level window
            current = root._window
            while hasattr(current, "_window") and current._window != current:
                current = current._window
            root = current.root
        else:
            root = root.root

    return tkfont.Font(root, font=font).measure(text)


def get_font_metrics(root, font, attr):
    """Get font metrics for the given font.

    Args:
        root: The root tk window or nebulatk window (.root attribute)
        font: A tuple containing the font name, size, and optionally a style
        attr (str): The attribute to get (e.g., 'linespace')

    Returns:
        int: The value of the requested font metric
    """
    # Generate full length font tuple
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)

    if not isinstance(root, Tk):
        # Handle Container objects - access the window's root
        if hasattr(root, "_window"):
            # For nested containers, traverse to the top-level window
            current = root._window
            while hasattr(current, "_window") and current._window != current:
                current = current._window
            root = current.root
        else:
            root = root.root

    return tkfont.Font(root, font=font).metrics(attr)


def loadfont(fontpath: str, private: bool = True, enumerable: bool = False) -> bool:
    """
    Load a font into the OS or process so that Tkinter (and other toolkits)
    can see it by name.

    On Windows: uses AddFontResourceExW.
    On UNIX: uses Fontconfig's FcConfigAppFontAddFile + FcConfigBuildFonts.

    Returns True on success, False on failure.
    """
    if not isinstance(fontpath, str):
        raise TypeError("fontpath must be a str")

    if ctypes_available:
        # — Windows branch —
        buf = create_unicode_buffer(fontpath)
        AddFont = windll.gdi32.AddFontResourceExW
        flags = (FR_PRIVATE if private else 0) | (0 if enumerable else FR_NOT_ENUM)
        added = AddFont(byref(buf), flags, 0)
        return bool(added)

    # — UNIX branch —
    if _libfc is None:
        # Fontconfig library didn't load
        print("Fontconfig library didn't load")
        return False

    # get the current config pointer
    cfg = _libfc.FcConfigGetCurrent()
    if not cfg:
        return False

    # encode and add
    encoded = fontpath.encode("utf-8")
    ok = _libfc.FcConfigAppFontAddFile(cfg, encoded)
    if ok == 0:
        return False

    # rebuild in-memory list
    if not _libfc.FcConfigBuildFonts(cfg):
        return False

    return True


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
