from .base import _widget
from .label import Label
from .frame import Frame

try:
    from .. import (
        fonts_manager,
        colors_manager,
        image_manager,
        animation_controller,
    )
except ImportError:
    import fonts_manager
    import colors_manager
    import image_manager
    import animation_controller


class Entry(_widget):

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
        self.can_type = True

        # Create cursor for text entry
        self.cursor = (
            Label(
                root=self,
                width=2,  # Thinner cursor for a more standard look
                height=(
                    self.font[1] * 1.2 if hasattr(self, "font") else 14
                ),  # Match font height
                fill="#000000",
                border_width=0,
            )
            .place(0, 0)  # Adjusted initial placement
            .hide()
        )

        self.cursor.can_focus = False

        # Position cursor at the end of text
        self.cursor_position = len(self.text)
        self._update_cursor_position()

        # Create flashing cursor animation (blink effect)
        self.cursor_animation = animation_controller.Animation(
            self.cursor,
            {
                "fill": "#00000000",  # Fade out completely
            },
            duration=0.6,  # Slightly slower blink for a more natural feel
            looping=True,
        )
        self.cursor_animation.start()

        self._selection_bg = (
            Frame(self, width=0, height=self.height, fill="#ADD8E6AA")
            .place(0, 0)
            .hide()
        )

        self._selection_bg.can_focus = False

    def _update_cursor_position(self):
        relative_cursor_position = self.cursor_position - self.slice[0]
        text_width = fonts_manager.measure_text(
            self.master, self.font, self.text[:relative_cursor_position]
        )

        # New calculation for justify = right
        full_text_width = fonts_manager.measure_text(self.master, self.font, self.text)

        # Adjust cursor height to match font height
        self.cursor.height = self.font[1] * 1.2 if hasattr(self, "font") else 14

        # Center vertically based on entry height
        self.cursor.y = (self.height - self.cursor.height) / 2

        if self.justify == "left":
            self.cursor.x = (
                text_width - 1
            )  # Adjust to be more centered between characters
        elif self.justify == "right":
            self.cursor.x = text_width + (
                self.width - full_text_width - 1
            )  # Adjust to be more centered between characters
        elif self.justify == "center":
            total_width = fonts_manager.measure_text(self.master, self.font, self.text)
            self.cursor.x = (
                self.width / 2 - total_width / 2 + text_width - 1
            )  # Adjust to be more centered between characters
        self.update()

    def get(self):
        return self.entire_text

    def _find_cursor_position_from_click(self, click_x):

        # Convert to relative position within the entry
        rel_x = click_x - self.x

        # Adjust for text justification
        if self.justify == "center":
            total_width = fonts_manager.measure_text(self.master, self.font, self.text)
            rel_x = rel_x - (self.width / 2 - total_width / 2)
        elif self.justify == "right":
            total_width = fonts_manager.measure_text(self.master, self.font, self.text)
            rel_x = rel_x - (self.width - total_width - 5)
        elif self.justify == "left":
            rel_x = rel_x - 5

        # Find the closest character position

        # Try each position to find closest match
        closest_pos = 0
        min_diff = float("inf")

        for pos in range(len(self.text) + 1):
            pos_width = fonts_manager.measure_text(
                self.master, self.font, self.text[:pos]
            )
            diff = abs(pos_width - rel_x)

            if diff < min_diff:
                min_diff = diff
                closest_pos = pos
        return closest_pos

    def typed(self, char):
        super().typed(char)

        self._update_selection_highlight()

        self._update_cursor_position()

    def clicked(self, x=None, y=None):
        super().clicked()
        self.cursor.show()
        self.cursor.alpha = 1.0  # Ensure cursor is visible when clicked

        # If click position is provided, update cursor position
        if x is not None:
            self.cursor_position = (
                self._find_cursor_position_from_click(x) + self.slice[0]
            )
            self._update_cursor_position()
        self._start_selection(x, y)

    def change_active(self):
        super().change_active()
        self.cursor.hide()

    def dragging(self, x, y):
        super().dragging(x, y)
        self._update_selection(x, y)

    def _start_selection(self, x, y):
        """Begin text selection at the clicked position."""
        self._selection_start = self.cursor_position
        self._selection_end = self._selection_start
        self._update_selection_highlight()

    def _update_selection(self, x, y):
        """Update selection as the mouse moves."""

        self.cursor_position = self._find_cursor_position_from_click(x) + self.slice[0]
        self._update_cursor_position()
        self._selection_end = self.cursor_position
        self._update_selection_highlight()

    def _update_selection_highlight(self):
        """Render the selection highlight on the canvas."""
        if self._selection_start is not None and self._selection_end is not None:

            start = min(
                self._selection_start,
                self._selection_end,
            )
            end = max(
                self._selection_start,
                self._selection_end,
            )

            start = max(self.slice[0], start) - self.slice[0]
            end = min(self.slice[1], end) - self.slice[0]
            total_width = fonts_manager.measure_text(self.master, self.font, self.text)
            sel_start_x = fonts_manager.measure_text(
                self.master, self.font, self.text[:start]
            )
            sel_start_x = (
                self.width / 2 - total_width / 2 + sel_start_x
            )  # Adjust to be more centered between characters

            sel_end_x = sel_start_x + fonts_manager.measure_text(
                self.master, self.font, self.text[start:end]
            )
            self._selection_bg.width = sel_end_x - sel_start_x
            self._selection_bg.x = sel_start_x
            self._selection_bg.update()
            self._selection_bg.show()
        else:
            self._selection_bg.hide()

    def _get_char_offset(self, index):
        """Helper to approximate pixel offset for a character index."""
        # This is a placeholder; actual implementation depends on font metrics
        return index * 10  # Approximate width per character

    def get_selection(self):
        """Return the currently selected text."""
        if self._selection_start is not None and self._selection_end is not None:
            start = min(self._selection_start, self._selection_end)
            end = max(self._selection_start, self._selection_end)
            return self.entire_text[start:end]
        return ""
