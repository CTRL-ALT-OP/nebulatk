import math
import os
import logging
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

logger = logging.getLogger(__name__)

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
        logger.warning("Failed to load fontconfig library: %s", e)
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
        elif type(font) is str:
            self.font = (font, 10)

        elif type(font) in (list, tuple):
            # Assume font is (font, size)
            self.font = font
        else:
            raise TypeError(
                "font must be 'default', None, a font name string, or a tuple/list"
            )


def _normalize_font(font):
    if len(font) < 3:
        return (font[0], font[1], "normal")
    return font


def _normalize_font_token(value):
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _normalize_font_style(style):
    token = _normalize_font_token(style)
    return token or "normal"


def _style_tokens_from_name(display_name):
    token = _normalize_font_token(display_name)
    style_tokens = set()
    for marker in ("bold", "italic", "oblique", "black", "light", "medium", "semibold"):
        if marker in token:
            style_tokens.add(marker)
    return style_tokens


@lru_cache(maxsize=1)
def _windows_font_catalog():
    if os.name != "nt":
        return ()
    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    rows = []

    # Prefer registry metadata because filenames often do not match family names.
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
        ) as key:
            index = 0
            while True:
                try:
                    display_name, file_name, _ = winreg.EnumValue(key, index)
                except OSError:
                    break
                index += 1

                if not isinstance(file_name, str):
                    continue
                file_lower = file_name.lower()
                if not file_lower.endswith((".ttf", ".otf", ".ttc")):
                    continue
                file_path = (
                    str(fonts_dir / file_name) if not os.path.isabs(file_name) else file_name
                )
                base_name = display_name.split("(", 1)[0].strip()
                rows.append(
                    {
                        "family_token": _normalize_font_token(base_name),
                        "style_tokens": _style_tokens_from_name(display_name),
                        "path": file_path,
                    }
                )
    except Exception:
        rows = []

    if rows:
        return tuple(rows)

    # Fallback: filename-based scan for environments where registry is unavailable.
    if not fonts_dir.exists():
        return ()
    try:
        for entry in fonts_dir.iterdir():
            if not entry.is_file():
                continue
            if entry.suffix.lower() not in (".ttf", ".otf", ".ttc"):
                continue
            rows.append(
                {
                    "family_token": _normalize_font_token(entry.stem),
                    "style_tokens": _style_tokens_from_name(entry.stem),
                    "path": str(entry),
                }
            )
    except Exception:
        return ()
    return tuple(rows)


def _resolve_windows_font_path(family, style):
    catalog = _windows_font_catalog()
    family_token = _normalize_font_token(family)
    if not family_token or not catalog:
        return None

    matches = [
        row
        for row in catalog
        if row["family_token"] == family_token or family_token in row["family_token"]
    ]
    if not matches:
        return None

    style_token = _normalize_font_style(style)

    if style_token != "normal":
        style_matches = [
            row["path"] for row in matches if style_token in row.get("style_tokens", set())
        ]
        if style_matches:
            return style_matches[0]

    regular = []
    stylized = []
    for row in matches:
        if row.get("style_tokens"):
            stylized.append(row["path"])
        else:
            regular.append(row["path"])
    if regular:
        return regular[0]
    return stylized[0] if stylized else None


def _font_candidates(family, style):
    candidates = [family]
    resolved_path = None
    if not family.lower().endswith((".ttf", ".otf", ".ttc")):
        resolved_path = _resolve_windows_font_path(family, style)
        if resolved_path is not None:
            candidates.insert(0, resolved_path)
        candidates.extend(
            [
                f"{family}.ttf",
                f"{family}.otf",
                "arial.ttf",
                "DejaVuSans.ttf",
            ]
        )
    return candidates, resolved_path


@lru_cache(maxsize=256)
def _load_font(family, size, style="normal"):
    size = max(1, int(size))
    candidates, _ = _font_candidates(family, style)
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_font_debug_info(font):
    """Return detailed diagnostics for a font tuple used by rendering."""
    font = _normalize_font(font)
    family = str(font[0])
    size = max(1, int(font[1]))
    style = str(font[2])
    normalized_style = _normalize_font_style(style)
    candidates, windows_resolved_path = _font_candidates(family, normalized_style)

    selected_candidate = None
    used_default_font = False
    try:
        for candidate in candidates:
            try:
                loaded_font = ImageFont.truetype(candidate, size)
                selected_candidate = candidate
                break
            except Exception:
                continue
        if selected_candidate is None:
            loaded_font = ImageFont.load_default()
            used_default_font = True
    except Exception:
        loaded_font = ImageFont.load_default()
        used_default_font = True

    return {
        "requested_family": family,
        "requested_size": size,
        "requested_style": normalized_style,
        "windows_resolved_path": windows_resolved_path,
        "candidate_chain": candidates,
        "selected_candidate": selected_candidate,
        "loaded_font_path": getattr(loaded_font, "path", None),
        "used_default_font": used_default_font,
    }


def measure_text(root, font, text):
    """Measure the width of text with the given font.

    Args:
        root: The root tk window or nebulatk window (.root attribute)
        font: A tuple containing the font name, size, and optionally a style
        text (str): The text to measure

    Returns:
        int: The width of the text in pixels
    """
    font = _normalize_font(font)
    pil_font = _load_font(font[0], font[1], font[2])
    if not text:
        return 0
    left, _, right, _ = pil_font.getbbox(text)
    return int(right - left)


def get_font_metrics(root, font, attr):
    """Get font metrics for the given font.

    Args:
        root: The root tk window or nebulatk window (.root attribute)
        font: A tuple containing the font name, size, and optionally a style
        attr (str): The attribute to get (e.g., 'linespace')

    Returns:
        int: The value of the requested font metric
    """
    font = _normalize_font(font)
    pil_font = _load_font(font[0], font[1], font[2])
    ascent, descent = pil_font.getmetrics()
    metrics = {
        "ascent": int(ascent),
        "descent": int(descent),
        "linespace": int(ascent + descent),
    }
    return metrics.get(attr, metrics["linespace"])


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
        logger.warning("Fontconfig library didn't load")
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

    font = _normalize_font(font)

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

    font = _normalize_font(font)

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

    font = _normalize_font(font)

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
NUMERIC = list("0123456789")
SYMBOL = list("`~!@#$%^&*()_+-={}[]|\\:\";',.></? ")
ALPHANUMERIC = ALPHA + NUMERIC
ALPHANUMERIC_PLUS = ALPHANUMERIC + SYMBOL
