from PIL import Image as pil
from PIL import ImageTk as piltk
from PIL import ImageDraw as pildraw
import tkinter as tk


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
            image = image.resize((_object.width-(_object.border_width*2), _object.height-(_object.border_width*2)), pil.NEAREST)

        # Convert image for tkinter
        image_converted = piltk.PhotoImage(image, master=_object.master.root)

    # Return both PhotoImage and PilImage objects if requested
    if return_both:
        return image_converted, image

    return image_converted


def load_image_generic(image, return_both=False):
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
        image_converted = piltk.PhotoImage(image)

    # Return both PhotoImage and PilImage objects if requested
    if return_both:
        return image_converted, image
    return image_converted


def create_image(fill, width, height, border, border_width):
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
    image = piltk.PhotoImage(image)
    return image
