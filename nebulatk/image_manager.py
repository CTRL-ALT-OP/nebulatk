from PIL import Image as pil
from PIL import ImageTk as piltk
from PIL import ImageDraw as pildraw

try:
    from . import bounds_manager
except ImportError:
    import bounds_manager


class Image:
    def __init__(self, path, _object=None, image=None):
        self.image = None
        self.tk_images = {}
        self.bounds = []

        if path is not None:
            # Open image
            self.image = pil.open(path)
            print(_object)
            if _object is not None:
                # Resize image if size isn't specified
                if _object.width != 0 and _object.height != 0:
                    self.resize(
                        _object.width - (_object.border_width * 2),
                        _object.height - (_object.border_width * 2),
                    )

                # Convert image for tkinter
                self.tk_images[_object.master] = convert_image(_object, self.image)

        elif image is not None:
            self.image = image

            if _object is not None:
                self.tk_images[_object.master] = convert_image(_object, self.image)

    def resize(self, width, height):
        self.tk_images = {}
        if width != 0 and height != 0:
            self.image = self.image.resize(
                (
                    width,
                    height,
                ),
                pil.NEAREST,
            )

    def tk_image(self, _object):
        if _object.master not in self.tk_images:
            self.tk_images[_object.master] = convert_image(_object, self.image)
        return self.tk_images[_object.master]


def convert_image(_object, image):
    return piltk.PhotoImage(image, master=_object.master.root)


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

        # Convert image for tkinter
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

        # Convert image for tkinter
        image_converted = convert_image(image, window)

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
    image = Image(None, master, image)
    return image
