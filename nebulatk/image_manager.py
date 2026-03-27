from PIL import Image as pil
from PIL import ImageDraw as pildraw

import math

try:
    from . import standard_methods
    from . import colors_manager
except ImportError:
    import standard_methods
    import colors_manager


class Image:
    def __init__(self, image, _object=None):
        self.image = None
        self._source_image = None
        self.tk_images = {}
        self.bounds = []

        if type(image) is Image:
            self.image = image.image
            self._source_image = self.image.copy() if self.image is not None else None

            if _object is not None:
                # Resize image if size isn't specified
                if _object.width != 0 and _object.height != 0:
                    self.resize(
                        _object.width - (_object.border_width * 2),
                        _object.height - (_object.border_width * 2),
                    )

                if _needs_tk_conversion(_object):
                    # Convert image for tkinter only when a tkinter canvas backend is active
                    self.tk_images[_object.master] = convert_image(_object, self.image)

        elif type(image) is str:
            # Open image
            self.image = pil.open(image)
            self._source_image = self.image.copy() if self.image is not None else None
            if _object is not None:
                # Resize image if size isn't specified
                if _object.width != 0 and _object.height != 0:
                    self.resize(
                        _object.width - (_object.border_width * 2),
                        _object.height - (_object.border_width * 2),
                    )

                if _needs_tk_conversion(_object):
                    # Convert image for tkinter only when a tkinter canvas backend is active
                    self.tk_images[_object.master] = convert_image(_object, self.image)

        elif image is not None:
            self.image = image
            self._source_image = self.image.copy() if self.image is not None else None

            if _object is not None:
                if _needs_tk_conversion(_object):
                    self.tk_images[_object.master] = convert_image(_object, self.image)

    def resize(self, width, height):
        self.tk_images = {}
        if width != 0 and height != 0 and self._source_image is not None:
            self.image = self._source_image.resize(
                (
                    width,
                    height,
                ),
                pil.NEAREST,
            )
        return self

    def flip(self, direction="horizontal"):
        self.tk_images = {}
        if direction == "horizontal":
            self.image = self.image.transpose(pil.FLIP_LEFT_RIGHT)
        elif direction == "vertical":
            self.image = self.image.transpose(pil.FLIP_TOP_BOTTOM)
        self._source_image = self.image.copy() if self.image is not None else None
        return self

    def rotate(self, angle):
        self.tk_images = {}
        pil_img = self.image.rotate(angle, expand=True)
        self.image = pil_img
        self._source_image = self.image.copy() if self.image is not None else None
        return self

    def recolor(self, color):
        self.tk_images = {}
        pil_img = self.image.convert("RGBA")
        data = pil_img.getdata()

        color = colors_manager.Color(color)
        color = color.rgba
        new_data = [
            (
                *color[:3],
                standard_methods.clamp(data[i][3] - (255 - color[3]), 0, 255),
            )
            for i in range(len(data))
        ]
        return self._update_pil_data(pil_img, new_data)

    def set_transparency(self, transparency):
        self.tk_images = {}
        pil_img = self.image.convert("RGBA")
        data = pil_img.getdata()
        new_data = [
            (
                *data[i][:3],
                standard_methods.clamp(transparency, 0, 255),
            )
            for i in range(len(data))
        ]
        return self._update_pil_data(pil_img, new_data)

    def increment_transparency(self, transparency):
        self.tk_images = {}
        pil_img = self.image.convert("RGBA")
        data = pil_img.getdata()
        new_data = [
            (
                *data[i][:3],
                standard_methods.clamp(data[i][3] - transparency, 0, 255),
            )
            for i in range(len(data))
        ]
        return self._update_pil_data(pil_img, new_data)

    def set_relative_transparency(self, transparency, curve="lin", exponent=1):
        """
        Update transparency based on given curve.

        transparency: The new maximum transparency
        curve: The curve to use for updating transparency
        exponent: The exponent for the curve (only used if curve is "exp")
        """
        curves = {
            "exp": lambda x, n=exponent: math.pow(
                (math.pow(transparency, 1 / n) / 255 * x), n
            ),
            "lin": lambda x: transparency * (x / 255),
            "sqrt": lambda x: curves["exp"](x, 0.5),
            "quad": lambda x: curves["exp"](x, 2),
            "cubic": lambda x: curves["exp"](x, 3),
            "log": lambda x: transparency / math.log(255 + 1) * math.log(x + 1),
        }

        self.tk_images = {}
        pil_img = self.image.convert("RGBA")
        data = pil_img.getdata()
        new_data = [
            (
                *data[i][:3],
                standard_methods.clamp(int(curves[curve](data[i][3])), 0, 255),
            )
            for i in range(len(data))
        ]

        return self._update_pil_data(pil_img, new_data)

    def _update_pil_data(self, pil_img, new_data):
        pil_img.putdata(new_data)
        self.image = pil_img
        self._source_image = self.image.copy() if self.image is not None else None
        return self

    def tk_image(self, _object):
        if not _needs_tk_conversion(_object):
            return self.image
        if _object.master not in self.tk_images:
            self.tk_images[_object.master] = convert_image(_object, self.image)
        return self.tk_images[_object.master]


def convert_image(_object, image):
    # OpenGL pipeline consumes PIL images directly.
    return image


def _needs_tk_conversion(_object):
    master = getattr(_object, "master", None)
    if master is None:
        return False
    if hasattr(master, "_window"):
        window = master._window
    else:
        window = master
    render_mode = getattr(window, "render_mode", "canvas")
    return render_mode != "image_gl"


def load_image(_object, image, return_both=False):
    """Load an image with PIL

    Args:
        _object (nebulatk.Widget): widget
        image (str): path to the image
        return_both (bool, optional): Request for both TkImage and PilImage. Defaults to False.

    Returns:
        TkImage: Tkinter-compatible image
    OR:
        TkImage: Tkinter-compatible image
        PilImage: Pil image
    """
    image_converted = None
    if image is not None:
        # Open image
        image = pil.open(image)

        # Resize image if size isn't specified
        if _object.width != 0 and _object.height != 0:
            image = image.resize(
                (
                    _object.width - (_object.border_width * 2),
                    _object.height - (_object.border_width * 2),
                ),
                pil.NEAREST,
            )

        # Convert image for tkinter only when required by backend
        if _needs_tk_conversion(_object):
            image_converted = convert_image(_object, image)

    # Return both PhotoImage and PilImage objects if requested
    return (image_converted, image) if return_both else image_converted


def load_image_generic(window, image, return_both=False):
    """Alternative to load_image without resizing. Does not require a parent widget.

    Args:
        image (str): path to the image
        return_both (bool, optional): Request for both TkImage and PilImage. Defaults to False.

    Returns:
        TkImage: Tkinter-compatible image
    OR:
        TkImage: Tkinter-compatible image
        PilImage: Pil image
    """
    image_converted = None
    if image is not None:
        # Open image
        image = pil.open(image)

        # Convert image for tkinter only when required by backend
        if _needs_tk_conversion(window):
            image_converted = convert_image(window, image)

    # Return both PhotoImage and PilImage objects if requested
    return (image_converted, image) if return_both else image_converted


def create_image(fill, width, height, border, border_width, master):
    """Generate a new TkImage image

    Args:
        fill (color): fill color
        width (int): width
        height (int): height
        border (color): border color
        border_width (int): border_width

    Returns:
        TkImage: Tkinter-compatible image
    """
    # Create base image
    image = pil.new("RGBA", (width, height), (0, 0, 0, 255))
    # Generate corners of rectangle (0-indexed)
    shape = [(0, 0), (width - 1, height - 1)]

    # Draw rectangle on image
    image1 = pildraw.Draw(image)
    image1.rectangle(shape, fill=fill, outline=border, width=border_width)

    # Convert image
    image = Image(image, master)
    return image
