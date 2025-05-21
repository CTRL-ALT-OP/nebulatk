from .base import _widget

try:
    from .. import (
        fonts_manager,
        colors_manager,
        image_manager,
    )
except ImportError:
    import fonts_manager
    import colors_manager
    import image_manager


class Label(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        orientation=0,
        text="",
        font=None,
        justify="center",
        text_color="default",
        fill="default",
        border="default",
        border_width=0,
        image=None,
        bounds_type="default",
    ):
        """_summary_

        Args:
            root (nebulatk.Window, optional): Root Window. Defaults to None.
            width (int, optional): width. Defaults to 0.
            height (int, optional): height. Defaults to 0.
            text (str, optional): Defaults to "".
            font (_type_, optional): Font. Font name, or font tuple. Defaults to None.
            fill (color, optional): Fill color. Defaults to "white".
            border (str, optional): Border color. Defaults to "black".
            border_width (int, optional): Border width. Defaults to 3.
            image (str, optional): Image path. Defaults to None.
            bounds_type (str, optional): _description_. Defaults to "box" if image is not provided, or "nonstandard" otherwise. Defaults to "box" if no image == provided, or "non-standard" if an image == provided.
        """
        super().__init__(
            root=root,
            width=width,
            height=height,
            orientation=orientation,
            text=text,
            font=font,
            justify=justify,
            border=border,
            text_color=text_color,
            fill=fill,
            border_width=border_width,
            image=image,
            bounds_type=bounds_type,
        )
        self.can_hover = False
        self.can_click = False
        self.can_type = False
