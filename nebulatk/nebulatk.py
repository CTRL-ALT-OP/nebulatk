# Import tkinter and filedialog
import sys
import threading
import tkinter as tk

# Import python standard packages
from time import sleep
from tkinter import filedialog as tkfile_dialog


# Importing from another file works differently than if running this file directly for some reason.
# Import all required modules from nebulatk
try:
    from . import (
        bounds_manager,
        fonts_manager,
        colors_manager,
        image_manager,
        initialize,
        standard_methods,
        defaults,
    )
except ImportError:
    import bounds_manager
    import fonts_manager
    import colors_manager
    import image_manager
    import initialize
    import standard_methods
    import defaults


# Our implementation of tkinter's file_dialog.
# This mostly just exists so that the user doesn't have to import nebulatk and tkinter
def FileDialog(window, initialdir=None, mode="r", filetypes=(("All files", "*"))):
    """Identical to tkinter.FileDialog

    Args:
        window (nebulatk.Window): Root window
        initialdir (str, optional): Initial directory to open to. Defaults to None.
        mode (str, optional): File open mode. Defaults to "r".
        filetypes (list, optional): List of filetypes. Format like:
            [
                ("Name","*.ext"),
                ("Name", ("*.ext", "*.ext2"))
            ]
            Defaults to [("All files", "*")].

    Returns:
        file: Open file
    """
    window.leave_window(None)
    file = tkfile_dialog.askopenfile(
        initialdir=initialdir,
        mode=mode,
        filetypes=filetypes,
    )
    window.leave_window(None)
    return file


# Initialize base methods for all widgets.
# This is largely so we don't ever need to initialize methods that will never be used (e.g. hovered on a frame)
class _widget_properties:
    def __synthesize_color(self, name, color, no_image=True):
        if not no_image:
            return colors_manager.Color(None)
        if color == "default":
            if hasattr(self.master.defaults, f"default_{name}"):
                color = getattr(self.master.defaults, f"default_{name}")
            else:
                name = name.lstrip("active_hover_")
                color = defaults._offset(self._colors[name], 40)
        else:
            color = colors_manager.Color(color)
        return color

    def __convert_image(self, image):
        return image_manager.Image(image) if type(image) is str else image

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        if self._root is not None and self.root != self.root.master:
            root.children.remove(self)

        self._root = root
        self.master = root.master
        self.children = []

        if self.initialized:
            self.update()

    @property
    def width(self):
        return self._size[0]

    @width.setter
    def width(self, width):
        self._size[0] = width

        if self.initialized:
            self._configure_size(self._size)

    @property
    def height(self):
        return self._size[1]

    @height.setter
    def width(self, width):
        self._size[1] = width

        if self.initialized:
            self._configure_size(self._size)

    @property
    def x(self):
        return self._position[0]

    @x.setter
    def x(self, x):
        self._position[0] = x

        if self.initialized:
            self._configure_position(self._position)

    @property
    def y(self):
        return self._position[1]

    @y.setter
    def y(self, y):
        self._position[1] = y

        if self.initialized:
            self._configure_position(self._position)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

        if self.initialized:
            self.update()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

        if self.initialized:
            self._configure_text(self._text)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        if font == "default":
            font = self.master.defaults.get_attribute("default_font").font
        else:
            font = fonts_manager.Font(font).font

        if self.text not in ("", None):
            min_width, min_height = fonts_manager.get_min_button_size(
                self.master, font, self.text
            )

            # If the widget size is not specified, set it to the minimum size
            if self._size[0] == 0:
                self._size[0] = min_width
            if self._size[1] == 0:
                self._size[1] = min_height

            # Check if the font size is the default font size
            # If so, set it to the max font size possible for the widget size
            if font[1] == -1:
                font = (
                    font[0],
                    fonts_manager.get_max_font_size(
                        self.master, font, self.width, self.height, self.text
                    ),
                )

        self._font = font

        if self.initialized:
            self.update()

    @property
    def justify(self):
        return self._justify

    @justify.setter
    def justify(self, value):
        self._justify = value

        if self.initialized:
            self.update()

    @property
    def text_color(self):
        return self._colors["text_color"].color

    @text_color.setter
    def text_color(self, value):
        value = self.__synthesize_color("text_color", value, self._no_image)
        self._colors["text_color"] = value

        if self.initialized:
            self.update()

    @property
    def active_text_color(self):
        return self._colors["active_text_color"].color

    @active_text_color.setter
    def active_text_color(self, value):
        value = self.__synthesize_color("active_text_color", value, self._no_image)
        self._colors["active_text_color"] = value

        if self.initialized:
            self.update()

    @property
    def fill(self):
        return self._colors["fill"].color

    @fill.setter
    def fill(self, value):
        fill = self.__synthesize_color("fill", value, self._no_image)
        self._colors["fill"] = fill

        if self.initialized:
            self.update()

    @property
    def active_fill(self):
        return self._colors["active_fill"].color

    @active_fill.setter
    def active_fill(self, value):
        active_fill = self.__synthesize_color("active_fill", value, self._no_image)
        self._colors["active_fill"] = active_fill

        if self.initialized:
            self.update()

    @property
    def hover_fill(self):
        return self._colors["hover_fill"].color

    @hover_fill.setter
    def hover_fill(self, value):
        hover_fill = self.__synthesize_color("hover_fill", value, self._no_image)
        self._colors["hover_fill"] = hover_fill

        if self.initialized:
            self.update()

    @property
    def active_hover_fill(self):
        return self._colors["active_hover_fill"].color

    @active_hover_fill.setter
    def active_hover_fill(self, value):
        active_hover_fill = self.__synthesize_color(
            "active_hover_fill", value, self._no_image
        )
        self._colors["active_hover_fill"] = active_hover_fill

        if self.initialized:
            self.update()

    @property
    def border(self):
        return self._colors["border"].color

    @border.setter
    def border(self, value):
        border = self.__synthesize_color("border", value, self._no_image)
        self._colors["border"] = border

        if self.initialized:
            self.update()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        if self.border is None:
            value = 0
        self._border_width = value

        if self.initialized:
            self.update()

    @property
    def image(self):
        return self._images["image"]

    @image.setter
    def image(self, value):
        value = self.__convert_image(value)

        self._images["image"] = value

        if self.initialized:
            self.update()

    @property
    def active_image(self):
        return self._images["active_image"]

    @active_image.setter
    def active_image(self, value):
        value = self.__convert_image(value)

        self._images["active_image"] = value

        if self.initialized:
            self.update()

    @property
    def hover_image(self):
        return self._images["hover_image"]

    @hover_image.setter
    def hover_image(self, value):
        value = self.__convert_image(value)

        self._images["hover_image"] = value

        if self.initialized:
            self.update()

    @property
    def active_hover_image(self):
        return self._images["active_hover_image"]

    @active_hover_image.setter
    def active_hover_image(self, value):
        value = self.__convert_image(value)

        self._images["active_hover_image"] = value

        if self.initialized:
            self.update()

    @property
    def bounds_type(self):
        return self._bounds_type

    @bounds_type.setter
    def bounds_type(self, value):
        if value == "default":
            value = "non-standard" if self._images["image"] is not None else "box"

        if self._images["image"] is not None:
            if value == "non-standard":
                self.bounds = bounds_manager.generate_bounds_for_nonstandard_image(
                    self._images["image"].image
                )

            # New width and height is the image size
            size = self._images["image"].image.size
            self._size = [
                size[0] + self.border_width * 2,
                size[1] + self.border_width * 2,
            ]
        if value == "custom":
            value = "non-standard"

        self._bounds_type = value

        if self.initialized:
            self.update()

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        self._bounds = value
        self._bounds_type = "non-standard"

        if self.initialized:
            bounds_manager.update_bounds(self, self.x, self.y, self.bounds_type)


class _widget(_widget_properties):

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
        custom_bounds: list | tuple = None,
        # Commands
        command=None,
        command_off=None,
        # Trigger Variables
        mode: str = "standard",
        state: bool = False,
    ):
        self.__initialize_general(root, width, height)

        self.__initialize_text(text, font, justify, text_color, active_text_color)

        self.__initialize_colors(
            fill, active_fill, hover_fill, active_hover_fill, image is None
        )

        self.__initialize_border(border, border_width)

        self.__initialize_images(image, active_image, hover_image, active_hover_image)

        self.__initialize_bounds(bounds_type, custom_bounds)

        self.__initialize_commands(command, command_off)

        self.__initialize_trigger(mode, state)

        self.initialized = True

    def __initialize_general(self, root, width, height):
        self.initialized = False
        self._no_image = True

        self.bg_object = None
        self.bg_object_active = None
        self.bg_object_hover = None
        self.bg_object_hover_active = None
        self.image_object = None
        self.active_object = None
        self.hover_object = None
        self.hover_object_active = None

        self.text_object = None
        self.active_text_object = None

        self.visible = True

        self._root = None
        self.root = root

        self._size = [width, height]

        self._position = [0, 0]

        self.angle = 0

        self._colors = {}

        self._images = {}

    def __initialize_text(self, text, font, justify, text_color, active_text_color):
        self.text = text
        self._entire_text = text

        self.font = font

        self.justify = justify

        self.text_color = text_color

        self.active_text_color = active_text_color

    def __initialize_colors(
        self, fill, active_fill, hover_fill, active_hover_fill, no_image
    ):
        self._no_image = no_image

        self.fill = fill

        self.active_fill = active_fill

        self.hover_fill = hover_fill

        self.active_hover_fill = active_hover_fill

    def __initialize_border(self, border, border_width):
        self.border = border
        self.border_width = border_width

    def __initialize_images(self, image, active_image, hover_image, active_hover_image):
        self.image = image
        self.active_image = active_image
        self.hover_image = hover_image
        self.active_hover_image = active_hover_image

    def __initialize_bounds(self, bounds_type, custom_bounds):
        if custom_bounds:
            self.bounds = custom_bounds
            self.bounds_type = "custom"
        else:
            self.bounds_type = bounds_type

    def __initialize_commands(self, command, command_off):
        self.command = command
        self.command_off = command_off

    def __initialize_trigger(self, mode, state):
        self.mode = mode
        self.state = state

    def hovered(self):
        if self.can_hover:
            if self.mode == "toggle":
                standard_methods.hovered_toggle(self)
            elif self.mode == "standard":
                standard_methods.hovered_standard(self)
            self.hovering = True

    def hover_end(self):
        if self.can_hover:
            standard_methods.hover_end(self)
            self.hovering = False

    # Utilize our standard methods to manage clicking
    def clicked(self):
        if self.can_click:
            if self.mode == "toggle":
                standard_methods.clicked_toggle(self)

            elif self.mode == "standard":
                standard_methods.clicked_standard(self)

    # No standard method for releasing, most other widgets don't use this method
    def release(self):
        if self.can_click and self.mode == "standard":
            self.state = not self.state

            if self.visible:
                if self.hovering:
                    # image_flop hides all other images and shows the selected image
                    standard_methods.image_flop(self, "hover_object")
                else:
                    standard_methods.image_flop(self, "image_object")

                if self.command_off is not None:
                    self.command_off()

    # Utilize our standard methods to manage toggling
    def toggle(self):
        """Toggle appearance of button"""
        if self.mode == "toggle":
            standard_methods.toggle_object_toggle(self)

        elif self.mode == "standard":
            standard_methods.toggle_object_standard(self)

    def dragging(self, x, y):
        pass

    def destroy(self):
        standard_methods.delete(self)

    def typed(self, character):
        pass

    def change_active(self):
        pass

    def _update_children(self, children=None, command="update"):
        if children is None:
            children = self.children
        if children != []:
            for child in children:
                getattr(child, command)()
                self._update_children(child.children)

    def _hide(self):
        """Hide the widget"""

        # Flop off hides all items that are part of this widget
        standard_methods.flop_off(self)

        # Remove this widget from the bounds
        bounds_manager.remove_bounds(self, self.bounds_type)

        # Always return self on methods the user might call. this allows for chaining like button = Button().place().hide()
        return self

    def hide(self):
        self.visible = False
        self._hide()
        self._update_children(command="_hide")
        return self

    def _show(self):
        """Shows the widget"""
        # Show makes all items that are part of this widget visible
        standard_methods.flop_on(self)

        # Add this widget to bounds
        bounds_manager.update_bounds(self, self.x, self.y, self.bounds_type)
        return self

    def show(self):
        self.visible = True
        self._show()
        self._update_children(command="_show")
        return self

    # Default place behavior
    def place(self, x=0, y=0):
        """Place the widget at the specified position.

        Args:
            x (int, optional): x position. Defaults to 0.
            y (int, optional): y position. Defaults to 0.
        """
        self.abs_x = x
        self.abs_y = y
        x = int(x)
        y = int(y)
        if self.bg_object is None and self.image_object is None:
            standard_methods.place_bulk(self, x, y)
            if self.bg_object is not None and self.bounds_type == "box":
                self.object = self.bg_object
            elif self.image_object is not None:
                self.object = self.image_object
            else:
                self.object = self.text_object
        else:
            standard_methods.update_positions(self, x, y)
        bounds_manager.update_bounds(self, x, y, mode=self.bounds_type)

        self.x = x
        self.y = y

        self._update_children()

        if hasattr(self, "original_x"):
            self.original_x = x
            self.original_y = y

        return self

    def update(self):
        standard_methods.delete(self)
        self.place(self.x, self.y)

    def _configure_size(self, size):
        self.update()

    def _configure_text(self, text):
        # Update text in this widget
        if self.text_object is not None:
            self.master.configure(self.text_object, text=text)

        if self.active_text_object is not None:
            self.master.configure(self.active_text_object, text=text)

    def _configure_position(self, position):
        standard_methods.update_positions(self, position[0], position[1])

    # Default configure behavior
    def configure(self, **kwargs):
        """Configure the widget with the specified parameters"""
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self


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
        custom_bounds: list | tuple = None,
        # Commands
        command=None,
        command_off=None,
        # Trigger Variables
        mode: str = "standard",
        state: bool = False,
    ):
        super().__init__(
            root,
            width,
            height,
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
            mode,
            state,
        )

        self.can_hover = True
        self.can_click = True
        self.can_type = False


class Slider(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        slider_height=10,
        minimum=0,
        maximum=100,
        text="",
        font=None,
        justify="center",
        text_color="default",
        active_text_color=None,
        fill="default",
        active_fill="default",
        border="default",
        border_width=0,
        slider_border_width=0,
        slider_fill="default",
        slider_border="default",
        image=None,
        active_image=None,
        hover_image=None,
        hover_image_active=None,
        bounds_type="default",
        command=None,
        command_off=None,
        state=False,
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

        # Load most initial variables
        initialize.load_initial(
            self,
            root,
            width,
            height,
            border_width,
            justify,
            state,
            None,
            command,
            command_off,
            slider_height,
            maximum,
            minimum,
            slider_border_width,
        )

        # Load bounds type
        initialize.load_bounds_type(self, bounds_type, image)

        # Load all of our images
        initialize.load_bulk_images(
            self,
            image=image,
            active_image=active_image,
            hover_image=hover_image,
            hover_image_active=hover_image_active,
        )

        # Load and initialize our text and font
        initialize.load_text(self, text, font)

        # Load all of our colors
        initialize.load_all_colors(
            self,
            fill,
            active_fill,
            border,
            text_color,
            active_text_color,
            slider_fill,
            slider_border,
        )

        # Convert all of our colors to hexadecimal
        initialize.convert_all_colors(self)

    # Utilize our standard methods for hovering
    def hovered(self):
        standard_methods.hovered_standard(self)
        self.hovering = True

    def hover_end(self):
        standard_methods.hover_end(self)
        self.hovering = False

    # Utilize standard method for toggling
    def toggle(self):
        standard_methods.toggle_object_standard(self)

    # Implement dragging along x ax== for slider
    def dragging(self, x, y):
        # Change our x position to be on the edge of the slider
        # this has the effect of the mouse moving the slider from the center of the slider
        x = x - self.width / 2

        # Clamp our x to the minimum and maximum values, compensating for the position offset,
        x = standard_methods.clamp(
            x, self.minimum + self.original_x, self.maximum + self.original_x
        )

        # Update the positions of all the objects in the slider, avoiding updating the actual background and widget positions
        standard_methods.update_positions(self, x, self.y, avoid_slider=True)

        # Update the bounds of the slider
        bounds_manager.update_bounds(self, x, self.y, mode=self.bounds_type)

        # Execute whatever command == set for dragging
        if self.command:
            self.command()

        # Update our x position
        self.x = x


class Label(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        text="",
        font=None,
        justify="center",
        text_color="default",
        fill="default",
        border="default",
        border_width=0,
        image=None,
        bounds_type="default",
        angle=0,
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
            text=text,
            font=font,
            justify=justify,
            border=border,
            text_color=text_color,
            fill=fill,
            border_width=border_width,
            image=image,
            bounds_type=bounds_type,
            angle=angle,
        )
        self.can_hover = False
        self.can_click = False
        self.can_type = False


class Entry(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
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
            bounds_type (str, optional): Defaults to "box" if image is not provided, or "nonstandard" otherwise.
        """
        # Load most initial variables
        initialize.load_initial(
            self,
            root,
            width,
            height,
            border_width,
            justify,
        )

        # Load our bounds type
        initialize.load_bounds_type(self, bounds_type, image)

        # Load all of our images
        initialize.load_bulk_images(self, image=image)

        # Load and initialize our text and font
        initialize.load_text(self, text, font)

        # Load all of our colors
        initialize.load_all_colors(
            self, fill=fill, border=border, text_color=text_color
        )

        # Convert all of our colors to hexadecimal
        initialize.convert_all_colors(self)

    def clicked(self):
        self.active = True

    def typed(self, character):
        # We will be using self.entire_text, not self.text, as self.configure will change self.text to be the displayed slice of self.entire_text
        # Backspace character
        if character == "\x08":
            self.entire_text = self.entire_text[:-1]

        # If the character is a visible character
        elif character in fonts_manager.ALPHANUMERIC_PLUS:
            self.entire_text = self.entire_text + character

        # Move end of display to the end of the text
        self.end = len(self.entire_text)

        # Get maximum length of characters we can fit in the widget
        max_length = fonts_manager.get_max_length(
            self.master, self.entire_text, self.font, self.width, self.end
        )

        # Configure display text to be the slice of text that we can fit in the widget
        if self.text_object is not None:
            self.configure(
                text=self.entire_text[self.end - max_length : self.end],
            )
        else:
            self.text = self.entire_text[self.end - max_length : self.end]
            self.update()

    def get(self):
        return self.entire_text


class Frame(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        image=None,
        fill=None,
        border="black",
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
        print("hi")
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


# Internal window class to implement threading
# NOTE: Threading and tcl do not combine well, so we have to do a lot of stuff ourselves and be careful that all modifications to the tcl windows are done in the same thread
class _window_internal(threading.Thread):

    def __init__(
        self,
        width=500,
        height=500,
        title="ntk",
        canvas_width="default",
        canvas_height="default",
        closing_command=None,
        resizable=(True, True),
        override=False,
    ):
        # Initialize the thread
        super().__init__()

        # Initialize the bounds
        # Bounds == structured as:
        # bounds[y] = [
        #   [_object, start_x, end_x],
        #   [_object2, start_x, end_x],
        # ]
        self.bounds = {}

        # Initialize variables
        self.root = None
        self.master = self
        self.canvas = None
        self.down = None
        self.active = None
        self.hovered = None
        self.width = int(width)
        self.height = int(height)
        self.resizable = resizable
        self.override = override

        self.title = title

        # Initialize canvas size
        if canvas_height == "default":
            canvas_height = self.height
        if canvas_width == "default":
            canvas_width = self.width

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Because of threading and garbage collection, images created will sometimes have to be stored in this variable to ensure they do not get deleted
        self.images = []

        # Initialize rest of variables
        self.running = True
        self.closing_command = closing_command

        self.defaults = defaults.new()

    # NOTE: EVENT HANDLERS

    # Handle mouse clicked down event
    def click(self, event):
        # Mouse position == a float, so convert to integer
        x = int(event.x)
        y = int(event.y)

        # Temp variable active_new
        # Default to None in case no object was clicked on
        active_new = None

        # Find the object that was clicked
        # Check if there are any objects initialized at that position
        if y in self.bounds:
            # Iterate over all objects at that y coordinate
            for i in self.bounds[y]:
                # Check if the mouse was within that object's boundary
                if x <= i[2] and x >= i[1]:
                    # Object found
                    # Set active_new and break
                    active_new = i[0]
                    break

        # If the new object == actually new, update the current active widget
        # self.active == used for things like detecting what widget to send keypresses to
        if active_new is not self.active:
            self.active = active_new

        # If the new object wasn't already being clicked
        if active_new is not self.down:
            self.down = active_new

            # If the new object == a valid widget
            if active_new is not None:
                # Click on the object
                active_new.clicked()

    # Handle mouse click up events
    def click_up(self, event):
        # If something was being clicked on, release the widget
        if self.down:
            self.down.release()
            self.down = None

    # Handle mouse movement event
    def hover(self, event):
        # Mouse position == a float, so convert to integer
        x = int(event.x)
        y = int(event.y)

        # Temp variable hovered_new
        # Default to None in case no object was hovered over
        hovered_new = None

        # If something == already being clicked on, this == also a dragging event on that widget.
        if self.down is not None:
            self.down.dragging(x, y)

        # Find the object that was hovered over
        # Check if there are any objects initialized at that position
        if y in self.bounds:
            # Iterate over all objects at that y coordinate
            for i in self.bounds[y]:
                # Check if the mouse was within that object's boundary
                if x <= i[2] and x >= i[1]:
                    # Object found
                    # If this object wasn't already being hovered over, trigger new object's hovered event
                    if i[0] is not self.hovered:
                        i[0].hovered()

                    # Set hovered_new and break
                    hovered_new = i[0]
                    break

        # If the object wasn't already being hovered over, check that there was something being hovered over previously and trigger the old object's hover_end event
        if hovered_new is not self.hovered:
            if self.hovered is not None:
                self.hovered.hover_end()

            # Update the currently hovered object
            self.hovered = hovered_new

    # Handle the mouse leaving the window
    def leave_window(self, event):
        # If something was being hovered, trigger the hover_end event
        if self.hovered is not None:
            self.hovered.hover_end()

        # If something was being clicked on, simulate the mouse button being released
        if self.down is not None:
            self.down.release()

        # Ensure that the variables for selected, clicked, and hovered objects are reset
        self.hovered = None
        self.down = None
        self.active = None

    # Handle keystrokes
    def typing(self, event):
        # If a widget == active, we should send keystrokes to it
        if self.active:
            self.active.typed(event.char)

    # NOTE: CREATION HANDLERS
    # These are necessary so that threading works properly with tcl

    # Wrapper for canvas.create_image method
    def create_image(self, x, y, image, state="normal"):
        self.images.append(image)
        return self.canvas.create_image(
            x, y, image=image.tk_image(self), anchor="nw", state=state
        )

    # Wrapper for canvas.create_rectangle method
    def create_rectangle(
        self, x, y, widt, height=0, fill=0, border_width=0, outline=None, state="normal"
    ):
        # To support transparency with RGBA, we need to check whether the rectangle includes transparency
        if fill is not None and len(fill) > 7:
            bg_image = image_manager.create_image(
                fill, widt, height, outline, border_width, self
            )
            self.images.append(bg_image)
            return self.create_image(x, y, bg_image, state=state)

        # Otherwise we can continue with creating the rectangle
        return self.canvas.create_rectangle(
            x + border_width / 2,
            y + border_width / 2,
            widt - border_width / 2,
            height - border_width / 2,
            fill=fill,
            width=border_width,
            outline=outline,
            state=state,
        )

    # Wrapper for canvas.create_text method
    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal", angle=0
    ):
        return self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            fill=fill,
            anchor=anchor,
            state=state,
            angle=angle,
        )

    # Wrapper for canvas.move method
    def move(self, _object, x, y):
        if _object is not None:
            self.canvas.move(_object, x, y)

    # Wrapper for canvas.delete method
    def delete(self, _object):
        self.canvas.delete(_object)

    # Wrapper for canvas.change_state method
    def change_state(self, _object, state):
        self.canvas.itemconfigure(_object, state=state)

    # Wrapper for canvas.configure method
    def configure(self, _object, **kwargs):
        self.canvas.itemconfigure(_object, kwargs)

    # NOTE: Other methods

    # Handle window closing
    def close(self):
        self.running = False
        try:
            self.root.update()
            self.join()
        except Exception as e:
            print(e)
        if self.closing_command is not None:
            self.closing_command()

    def destroy(self):
        self.close()

    # Add in window.place() to simplify tcl's root.geometry method
    def place(self, x=0, y=0):
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        return self

    # Wrapper for root.bind() method, in future, add global keypress handling
    def bind(self, key, command):
        self.root.bind(key, command)

    # Main method
    def run(self):
        # Create window
        self.root = tk.Tk()
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            borderwidth=0,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Initialize window
        self.root.geometry(f"{self.width}x{self.height}")

        self.root.title(self.title)

        self.root.resizable(self.resizable[0], self.resizable[1])

        self.root.overrideredirect(self.override)

        def close():
            self.running = False
            try:
                self.root.quit()
            except Exception as e:
                print(f"exception{e}")
            if self.closing_command is not None:
                self.closing_command()

        # Bind events to our new event handlers
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<ButtonRelease-1>", self.click_up)
        self.canvas.bind_all("<Key>", self.typing)
        self.root.protocol("WM_DELETE_WINDOW", close)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", self.leave_window)

        # Run mainloop
        self.root.mainloop()

        # NOTE: The following code == an alternative, but broken, method of running mainloop
        """while self.running:
            self.root.update_idletasks()
            self.root.update()
            sleep(0.01)"""


def Window(
    width=500,
    height=500,
    title="ntk",
    canvas_width="default",
    canvas_height="default",
    closing_command=sys.exit,
    resizable=(True, True),
    override=False,
):
    """Window constructor

    Args:
        width (int, optional): Width. Defaults to 500.
        height (int, optional): Height. Defaults to 500.
        canvas_width (str, optional): Canvas width. Defaults to width.
        canvas_height (str, optional): Canvas height. Defaults to height.
        closing_command (function, optional): Command to execute on close. Defaults to sys.exit.
        resizable (iterable or boolean, optional): Controls whether the window is resizable on the X axis, then Y axis

    Returns:
        _type_: _description_
    """
    # Create window

    if type(resizable) is bool:
        resizable = (resizable, resizable)

    canvas = _window_internal(
        width,
        height,
        title,
        canvas_width,
        canvas_height,
        closing_command,
        resizable,
        override,
    )

    # Start window thread
    canvas.start()

    # Wait for window to be created, as it == in a separate thread and not blocking this thread
    while canvas.root is None:
        sleep(0.1)

    # Return the window
    return canvas


fonts = [
    "Algerian",
    "Blackadder ITC",
    "Bradley Hand ITC",
    "Castellar",
    "Cooper Black",
    "Edwardian Script ITC",
    "Forte",
    "Comic Sans MS",
    "Bauhaus 93",
    "Harlow Solid Italic",
]

colors = [
    "FD3A4A",
    "FD3A4A",
    "A7F432",
    "5DADEC",
    "BFAFB2",
    "FF5470",
    "FFDB00",
    "FF7A00",
    "#45ba52",
    "#2a89d5",
    "#5c21de",
    "#d14d2e",
]


# NOTE: EXAMPLE WINDOW
def __main__():
    canvas = Window()
    f = Frame(
        canvas, image="examples/Images/background.png", width=500, height=500
    ).place(0, 0)
    print(f.border, f.border_width)
    # Button(canvas,10,10,text="hahah").place()
    # Button(canvas,text="hahah").place(50,10)
    # Button(canvas,text="hihih", font = ("Helvetica",36)).place(100,100)
    Button(
        canvas,
        text="hillo",
        image="examples/Images/main_button_inactive.png",
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        mode="toggle",
    ).place(0, 0)
    Button(
        canvas,
        text="hi",
        font=("Helvetica", 50),
        fill=[255, 67, 67, 45],
    ).place(0, 400)
    # ImageButton(canvas,image="Images/test_inactive.png",active_image="Images/test_active.png").place(0,0)
    # btn_4 = Button(canvas,15,15,text="hahah").place(15,15)
    # btn_4.place(50,60)

    # Frame(canvas,30,30, border = "green").place(160,80)


if __name__ == "__main__":
    __main__()
