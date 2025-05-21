from .base import _widget
from .button import Button

try:
    from .. import (
        fonts_manager,
        colors_manager,
        image_manager,
        standard_methods,
    )
except ImportError:
    import fonts_manager
    import colors_manager
    import image_manager
    import standard_methods


class Slider(_widget):

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
        # Slider properties
        slider_width: int = 0,
        slider_height: int = 0,
        # Text Variables
        slider_text: str = "",
        slider_font: fonts_manager.Font = None,
        slider_justify: str = "center",
        slider_text_color: colors_manager.Color = "default",
        slider_active_text_color: colors_manager.Color = None,
        # Color Variables
        slider_fill: colors_manager.Color = "default",
        slider_active_fill: colors_manager.Color = "default",
        slider_hover_fill: colors_manager.Color = "default",
        slider_active_hover_fill: colors_manager.Color = "default",
        # Border Variables
        slider_border: colors_manager.Color = "default",
        slider_border_width: int = 0,
        # Image Variables
        slider_image: image_manager.Image = None,
        slider_active_image: image_manager.Image = None,
        slider_hover_image: image_manager.Image = None,
        slider_active_hover_image: image_manager.Image = None,
        # Bound Variables
        slider_bounds_type: str = "default",
        slider_custom_bounds: list = None,
    ):
        """Slider widget

        Args:
            root (nebulatk.Window, optional): Root Window. Defaults to None.

            width (int, optional): width. Defaults to 0.
            height (int, optional): height. Defaults to 0.

            slider_height (int, optional): Slider height. Defaults to 10.

            minimum (int, optional): Minimum slider value. Defaults to 0.
            maximum (int, optional): Maximum slider value. Defaults to 100.

            text (str, optional): Defaults to "".
            font (_type_, optional): Font. Font name, or font tuple. Defaults to None.
            justify (str, optional): Justification for text. Defaults to None.

            text_color (str, color): color. Defaults to "default".
            active_text_color (color, optional): color. Defaults to None.

            fill (color, optional): Fill color. Defaults to "white".
            active_fill (color, optional): Active fill color

            border (color, optional): Border color. Defaults to "black".

            border_width (int, optional): Border width. Defaults to 0.
            slider_border_width (int, optional): Border width. Defaults to 0.

            slider_fill (color, optional): Slider fill color. Defaults to "default".
            slider_border (color, optional): Border color. Defaults to "black".

            image (str, optional): Image path. Defaults to None.
            active_image (str, optional): Image path. Defaults to None.
            hover_image (str, optional): Image path. Defaults to None.
            hover_image_active (str, optional): Image path. Defaults to None.

            bounds_type (str, optional): Defaults to "box" if image is not provided, or "nonstandard" otherwise.

            command (function, optional): Defaults to None.
            command_off (function, optional): Defaults to None.

            state (bool, optional): _description_. Defaults to False.
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
        self.button = Button(
            self,
            width=slider_width,
            height=slider_height,
            text=slider_text,
            font=slider_font,
            justify=slider_justify,
            text_color=slider_text_color,
            active_text_color=slider_active_text_color,
            fill=slider_fill,
            active_fill=slider_active_fill,
            hover_fill=slider_hover_fill,
            active_hover_fill=slider_active_hover_fill,
            border=slider_border,
            border_width=slider_border_width,
            image=slider_image,
            active_image=slider_active_image,
            hover_image=slider_hover_image,
            active_hover_image=slider_active_hover_image,
            bounds_type=slider_bounds_type,
            custom_bounds=slider_custom_bounds,
            dragging_command=self._dragging,
        ).place()

    # Implement dragging along x axis for slider
    def _dragging(self, x, y):
        # Change our x position to be on the edge of the slider
        # this has the effect of the mouse moving the slider from the center of the slider
        x = x - self.button.width / 2

        # Clamp our x to the minimum and maximum values, compensating for the position offset,
        x = standard_methods.clamp(x, 0, self.width - self.button.width)

        # Update the positions of all the objects in the slider, avoiding updating the actual background and widget positions
        self.button.place(x, self.button.y)
