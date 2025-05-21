from .base import _widget

try:
    from .. import (
        colors_manager,
        image_manager,
    )
except ImportError:
    import colors_manager
    import image_manager


class Frame(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        image=None,
        fill="default",
        border="default",
        border_width=1,
        bounds_type="box",
    ):
        """_summary_

        Args:
            root (nebulatk.Window, optional): Root Window. Defaults to None.
            width (int, optional): width. Defaults to 0.
            height (int, optional): height. Defaults to 0.
            image (str, optional): Image path. Defaults to None.
            fill (color, optional): Fill color. Defaults to None.
            border (str, optional): Border color. Defaults to "black".
            border_width (int, optional): Border width. Defaults to 1.
            bounds_type (str, optional): Defaults to "box" if image is not provided, or "nonstandard" otherwise. Defaults to "box".
        """
        super().__init__(
            root=root,
            width=width,
            height=height,
            image=image,
            fill=fill,
            border=border,
            border_width=border_width,
            bounds_type=bounds_type,
        )
        self.can_hover = False
        self.can_click = False
        self.can_type = False
