from .base import _widget
from .button import Button

try:
    from .. import (
        bounds_manager,
        fonts_manager,
        colors_manager,
        image_manager,
        standard_methods,
    )
except ImportError:
    import bounds_manager
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
        direction: str = "horizontal",
        dragging_command=None,
        resize: bool = False,
        style=None,
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
            resize=resize,
            style=style,
        )
        self.can_hover = False
        self.can_click = False
        self.can_type = False
        self.direction = (direction or "horizontal").lower()
        if self.direction not in ("horizontal", "vertical"):
            raise ValueError("direction must be either 'horizontal' or 'vertical'")
        self._dragging_command = dragging_command
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
            dragging_command=self._wrapped_dragging,
        ).place()

    def _wrapped_dragging(self, x, y):
        self._dragging(x, y)
        if self._dragging_command is not None:
            self._dragging_command(x, y)

    # Implement dragging along the configured axis for slider.
    def _dragging(self, x, y):
        if self.direction == "vertical":
            # Move the slider based on mouse Y from the button center.
            y = y - self.button.height / 2
            y = standard_methods.clamp(y, 0, self.height - self.button.height)
            self.button.place(self.button.x, y)
            return

        # Move the slider based on mouse X from the button center.
        x = x - self.button.width / 2
        x = standard_methods.clamp(x, 0, self.width - self.button.width)
        self.button.place(x, self.button.y)


class Scrollbar(Slider):
    def __init__(
        self,
        *args,
        scroll_target=None,
        scroll_step=20,
        side_scrolling=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scroll_target = self if scroll_target is None else scroll_target
        self.scroll_step = max(1, int(scroll_step))
        self.side_scrolling = bool(side_scrolling)

    def _wheel_notches(self, event, axis="y"):
        if axis == "y" and hasattr(event, "num"):
            if event.num == 4:
                return 1
            if event.num == 5:
                return -1

        if axis == "x":
            delta = int(getattr(event, "delta_x", 0) or 0)
        else:
            delta = int(getattr(event, "delta_y", getattr(event, "delta", 0)) or 0)
        if delta == 0:
            return 0
        if delta % 120 == 0:
            return int(delta / 120)
        return 1 if delta > 0 else -1

    def handles_scroll_event(self, event, event_x=None, event_y=None):
        target = self if self.scroll_target is None else self.scroll_target
        if event_x is None:
            event_x = getattr(event, "x", None)
        if event_y is None:
            event_y = getattr(event, "y", None)
        if event_x is None or event_y is None:
            return False
        event_x = int(event_x)
        event_y = int(event_y)
        if not bounds_manager.check_hit(
            target, event_x, event_y, require_focus=False
        ):
            return False

        if self.button.dragging_command is None:
            return False

        scroll_axis = "x" if self.side_scrolling else "y"
        notches = self._wheel_notches(event, axis=scroll_axis)
        if notches == 0:
            return False

        movement = -notches * self.scroll_step
        center_x = self.button.x + (self.button.width / 2)
        center_y = self.button.y + (self.button.height / 2)
        if self.direction == "vertical":
            center_y += movement
        else:
            center_x += movement

        self.button.dragging_command(center_x, center_y)
        return True
