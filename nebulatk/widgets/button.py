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


class Button(_widget):

    def __init__(
        self,
        root=None,
        # General Variables
        width: int = 0,
        height: int = 0,
        # Text Variables
        text: str = "",
        font: fonts_manager.Font = None,
        justify: str = "center",
        text_color: colors_manager.Color = "default",
        active_text_color: colors_manager.Color = None,
        # Color Variables
        fill: colors_manager.Color = "default",
        active_fill: colors_manager.Color = "default",
        hover_fill: colors_manager.Color = "default",
        active_hover_fill: colors_manager.Color = "default",
        # Border Variables
        border: colors_manager.Color = "default",
        border_width: int = 0,
        # Image Variables
        image: image_manager.Image = None,
        active_image: image_manager.Image = None,
        hover_image: image_manager.Image = None,
        active_hover_image: image_manager.Image = None,
        # Bound Variables
        bounds_type: str = "default",
        custom_bounds: list = None,
        # Commands
        command=None,
        command_off=None,
        dragging_command=None,
        # Trigger Variables
        mode: str = "standard",
        state: bool = False,
    ):
        super().__init__(
            root,
            width,
            height,
            0,
            text,
            font,
            justify,
            text_color,
            active_text_color,
            fill,
            active_fill,
            hover_fill,
            active_hover_fill,
            border,
            border_width,
            image,
            active_image,
            hover_image,
            active_hover_image,
            bounds_type,
            custom_bounds,
            command,
            command_off,
            dragging_command,
            mode,
            state,
        )
        self.can_hover = True
        self.can_click = True
        self.can_type = False
