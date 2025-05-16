# Import tkinter and filedialog
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
        standard_methods,
        defaults,
        animation_controller,
    )
except ImportError:
    import bounds_manager
    import fonts_manager
    import colors_manager
    import image_manager
    import standard_methods
    import defaults
    import animation_controller


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


# Base Component interface
class Component:
    def __init__(self, width=0, height=0, x=0, y=0, **kwargs):
        self._position = [x, y]
        self._size = [width, height]

    def _update_children(self, children=None, command="update"):
        if children is None:
            children = self.children
        if children != []:
            for child in children:
                getattr(child, command)()
                self._update_children(child.children)

    def hide(self):
        self._visible = False
        self._hide(root=True)
        return self

    def show(self):
        self._visible = True
        self._show(root=True)
        return self

    def update(self):
        # Must implement in components
        pass

    def destroy(self):
        # Must implement in components
        pass

    def place(self, x=0, y=0):
        self._position = [x, y]
        return self

    # Properties:
    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible

        self.show() if visible else self.hide()

    @property
    def x(self):
        return self._position[0]

    @x.setter
    def x(self, x):
        self._position[0] = x

        self.place(x, self.y)

    @property
    def y(self):
        return self._position[1]

    @y.setter
    def y(self, y):
        self._position[1] = y

        self.place(self.x, y)

    @property
    def width(self):
        return self._size[0]

    @width.setter
    def width(self, width):
        self._size[0] = width

        self.resize(width, self.height)

    @property
    def height(self):
        return self._size[1]

    @height.setter
    def height(self, height):
        self._size[1] = height

        self.resize(self.width, height)


# Initialize base methods for all widgets.
# This is largely so we don't ever need to initialize methods that will never be used (e.g. hovered on a frame)
class _widget_properties:
    def __synthesize_color(self, name, color, no_image=True):
        if color == "default":
            if not no_image:
                return colors_manager.Color(None)
            if hasattr(self.master.defaults, f"default_{name}"):
                color = getattr(self.master.defaults, f"default_{name}")
            else:
                name = "_".join(
                    [i for i in name.split("_") if i not in ["active", "hover"]]
                )
                color = defaults._offset(self._colors[name], 40)
        else:
            color = colors_manager.Color(color)

        return color

    def __convert_image(self, image):
        return (
            image_manager.Image(image, self)
            if type(image) in (str, image_manager.Image)
            else image
        )

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        if self._root is not None and self.root != self.root.master:
            root.children.remove(self)

        if root != root.master:
            root.children.append(self)
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

        if self.initialized and self.master.updates_all:
            self._configure_size(self._size)

    @property
    def height(self):
        return self._size[1]

    @height.setter
    def height(self, height):
        self._size[1] = height

        if self.initialized and self.master.updates_all:
            self._configure_size(self._size)

    @property
    def x(self):
        return self._position[0]

    @x.setter
    def x(self, x):
        self._position[0] = x

        if self.initialized and self.master.updates_all:
            self._configure_position(self._position)

    @property
    def y(self):
        return self._position[1]

    @y.setter
    def y(self, y):
        self._position[1] = y

        if self.initialized and self.master.updates_all:
            self._configure_position(self._position)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

        if self.initialized and self.master.updates_all:
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

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def justify(self):
        return self._justify

    @justify.setter
    def justify(self, value):
        self._justify = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def text_color(self):
        return self._colors["text_color"].trunc_hex

    @text_color.setter
    def text_color(self, value):
        value = self.__synthesize_color("text_color", value, self._no_image)
        self._colors["text_color"] = value
        # print(self._colors)
        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def active_text_color(self):
        return self._colors["active_text_color"].trunc_hex

    @active_text_color.setter
    def active_text_color(self, value):
        value = self.__synthesize_color("active_text_color", value, self._no_image)
        self._colors["active_text_color"] = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def fill(self):
        return self._colors["fill"].color

    @fill.setter
    def fill(self, value):
        fill = self.__synthesize_color("fill", value, self._no_image)
        self._colors["fill"] = fill

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def active_fill(self):
        return self._colors["active_fill"].color

    @active_fill.setter
    def active_fill(self, value):
        active_fill = self.__synthesize_color("active_fill", value, self._no_image)
        self._colors["active_fill"] = active_fill

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def hover_fill(self):
        return self._colors["hover_fill"].color

    @hover_fill.setter
    def hover_fill(self, value):
        hover_fill = self.__synthesize_color("hover_fill", value, self._no_image)
        self._colors["hover_fill"] = hover_fill

        if self.initialized and self.master.updates_all:
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

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def border(self):
        return self._colors["border"].color

    @border.setter
    def border(self, value):
        border = self.__synthesize_color("border", value, self._no_image)
        self._colors["border"] = border

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        if self.border is None:
            value = 0
        self._border_width = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def image(self):
        return self._images["image"]

    @image.setter
    def image(self, value):
        value = self.__convert_image(value)

        self._images["image"] = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def active_image(self):
        return self._images["active_image"]

    @active_image.setter
    def active_image(self, value):
        value = self.__convert_image(value)

        self._images["active_image"] = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def hover_image(self):
        return self._images["hover_image"]

    @hover_image.setter
    def hover_image(self, value):
        value = self.__convert_image(value)

        self._images["hover_image"] = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def active_hover_image(self):
        return self._images["active_hover_image"]

    @active_hover_image.setter
    def active_hover_image(self, value):
        value = self.__convert_image(value)

        self._images["active_hover_image"] = value

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def bounds_type(self):
        return self._bounds_type

    @bounds_type.setter
    def bounds_type(self, value):
        self.bounds = []
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

        if self.initialized and self.master.updates_all:
            self.update()

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        self._bounds = value
        self._bounds_type = "non-standard"


class _widget(_widget_properties, Component):

    def __init__(
        self,
        root=None,
        # General Variables
        width: int = 0,
        height: int = 0,
        orientation: int = 0,
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
        super().__init__()
        self.__initialize_general(root, width, height, orientation)
        self.__initialize_text(text, font, justify, text_color, active_text_color)

        self.__initialize_colors(
            fill, active_fill, hover_fill, active_hover_fill, image is None
        )

        self.__initialize_border(border, border_width)

        self.__initialize_images(image, active_image, hover_image, active_hover_image)

        self.__initialize_bounds(bounds_type, custom_bounds)

        self.__initialize_commands(command, command_off, dragging_command)

        self.__initialize_trigger(mode, state)

        self.initialized = True

        self.can_focus = True

        self._images_initialized = {}

        self._scheduled_deletion = []

    def __initialize_general(self, root, width, height, orientation):
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

        self._visible = True
        self.hovering = False

        self._root = None
        self.root = root

        self.root.master.children.insert(0, self)

        self._size = [width, height]

        self._position = [0, 0]

        self.orientation = 0

        self._colors = {}

        self._images = {}

    def __initialize_text(self, text, font, justify, text_color, active_text_color):
        # print("hit", type(self), text_color)
        self.text = text
        self.entire_text = text

        self.font = font

        self.justify = justify

        self.text_color = text_color

        self.active_text_color = active_text_color

        self.cursor_position = 0
        self.slice = [0, len(self.text)]
        self._selection_start = 0
        self._selection_end = 0

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

    def __initialize_commands(self, command, command_off, dragging_command):
        self.command = command
        self.command_off = command_off
        self.dragging_command = dragging_command

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
    def clicked(self, x=None, y=None):
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
        if self.dragging_command:
            x, y = standard_methods.abs_position_to_rel(self, x, y)
            self.dragging_command(x, y)

    def destroy(self):
        standard_methods.delete(self)
        self.root.master.children.remove(self)

    def typed(self, char):
        if not self.can_type:
            return

        def update_selection_bounds():

            self._selection_start, self._selection_end = sorted(
                [self._selection_start, self._selection_end]
            )

        def delete_selection():
            start, end = (
                self._selection_start,
                self._selection_end,
            )
            self.entire_text = self.entire_text[:start] + self.entire_text[end:]
            self.cursor_position = self._selection_start
            self._selection_start = self._selection_end = self.cursor_position
            return start != end

        def update_display():
            self.end = len(self.entire_text)
            max_length = fonts_manager.get_max_length(
                self.master, self.entire_text, self.font, self.width, self.end
            )
            start_pos = max(
                0,
                min(
                    self.cursor_position - max_length // 2,
                    len(self.entire_text) - max_length,
                ),
            )
            end_pos = min(start_pos + max_length, len(self.entire_text))
            self.slice = [start_pos, end_pos]
            display_text = self.entire_text[start_pos:end_pos]
            if self.text_object is not None:
                self.configure(text=display_text)
            else:
                self.text = display_text
                self.update()

        deleted_text = False
        ctrl_or_cmd = {"Control_L", "Control_R", "Meta_L", "Meta_R"} & set(
            self.master.active_keys
        )

        if (
            char.keysym in ["BackSpace", "Delete"]
            or char.char in fonts_manager.ALPHANUMERIC_PLUS
        ):
            update_selection_bounds()
            deleted_text = delete_selection()

        if char.keysym == "BackSpace":
            if self.cursor_position > 0 and not deleted_text:
                self.entire_text = (
                    self.entire_text[: self.cursor_position - 1]
                    + self.entire_text[self.cursor_position :]
                )
                self.cursor_position -= 1
            self._selection_end = self.cursor_position
            self._selection_start = self.cursor_position

        elif char.keysym == "Delete":
            if self.cursor_position < len(self.entire_text) and not deleted_text:
                self.entire_text = (
                    self.entire_text[: self.cursor_position]
                    + self.entire_text[self.cursor_position + 1 :]
                )

        elif char.keysym == "Left":
            if self.cursor_position > 0:
                self.cursor_position -= 1
                self._selection_end = self.cursor_position
            if not {"Shift_L", "Shift_R"} & set(self.master.active_keys):
                self._selection_start = self.cursor_position

        elif char.keysym == "Right":
            if self.cursor_position < len(self.entire_text):
                self.cursor_position += 1
                self._selection_end = self.cursor_position
            if not {"Shift_L", "Shift_R"} & set(self.master.active_keys):
                self._selection_start = self.cursor_position

        elif char.keysym == "Home":
            self.cursor_position = 0
            self._selection_end = self.cursor_position
            if not {"Shift_L", "Shift_R"} & set(self.master.active_keys):
                self._selection_start = self.cursor_position

        elif char.keysym == "End":
            self.cursor_position = len(self.entire_text)
            self._selection_end = self.cursor_position
            if not {"Shift_L", "Shift_R"} & set(self.master.active_keys):
                self._selection_start = self.cursor_position

        elif char.keysym == "c" and ctrl_or_cmd:
            update_selection_bounds()
            if self._selection_start != self._selection_end:
                selected_text = self.entire_text[
                    self._selection_start : self._selection_end
                ]
                self.master.root.clipboard_clear()
                self.master.root.clipboard_append(selected_text)

        elif char.keysym == "v" and ctrl_or_cmd:
            update_selection_bounds()
            try:
                clipboard_text = self.master.root.clipboard_get()
                delete_selection()
            except tk.TclError:  # Empty clipboard
                self._selection_start = self._selection_end = self.cursor_position
                return

            if clipboard_text:
                self.entire_text = (
                    self.entire_text[: self.cursor_position]
                    + clipboard_text
                    + self.entire_text[self.cursor_position :]
                )
                self.cursor_position += len(clipboard_text)
                self._selection_start = self._selection_end = self.cursor_position

        elif char.keysym == "a" and ctrl_or_cmd:
            self._selection_start = 0
            self._selection_end = self.cursor_position = len(self.entire_text)

        elif char.char in fonts_manager.ALPHANUMERIC_PLUS:
            self.entire_text = (
                self.entire_text[: self.cursor_position]
                + char.char
                + self.entire_text[self.cursor_position :]
            )
            self.cursor_position += 1
            self._selection_end = self.cursor_position
            self._selection_start = self.cursor_position

        else:
            return  # Ignore unsupported input

        update_display()

    def change_active(self):
        pass

    def _hide(self, root=False):
        """Hide the widget"""

        # Flop off hides all items that are part of this widget
        standard_methods.flop_off(self)

        # If this widget is the root widget, hide all its children
        if root:
            self._update_children(command="_hide")

        # Always return self on methods the user might call. this allows for chaining like button = Button().place().hide()
        return self

    def _show(self, root=False):
        """Shows the widget"""
        # Show makes all items that are part of this widget visible
        standard_methods.flop_on(self)

        # If this widget is the root widget, hide all its children
        if root:
            self._update_children(command="_show")
        return self

    # Default place behavior
    def place(self, x=0, y=0):
        """Place the widget at the specified position.

        Args:
            x (int, optional): x position. Defaults to 0.
            y (int, optional): y position. Defaults to 0.
        """
        # old_x, old_y = self.x, self.y
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
        # bounds_manager.update_bounds(self, old_x, old_y, x, y, mode=self.bounds_type)

        self._position = [x, y]

        self._update_children()

        if hasattr(self, "original_x"):
            self.original_x = x
            self.original_y = y

        return self

    def update(self):
        standard_methods.schedule_delete(self)
        self.place(self.x, self.y)
        standard_methods.delete_scheduled(self)

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
        if not self.master.updates_all:
            self.update()
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
            return self.text[start:end]
        return ""


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


# Internal window class to implement threading
# NOTE: Threading and tcl do not combine well, so we have to do a lot of stuff ourselves and be careful that all modifications to the tcl windows are done in the same thread
class _window_internal(threading.Thread, Component):

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
        self.daemon = True

        # Initialize the bounds
        # Bounds == structured as:
        # bounds[y] = [
        #   [_object, start_x, end_x],
        #   [_object2, start_x, end_x],
        # ]
        Component.__init__(self, width, height)
        self.bounds = {}

        # Initialize variables
        self.root = None
        self.master = self
        self.canvas = None
        self.down = None
        self.active = None
        self.hovered = None
        self.resizable = resizable
        self.override = override
        self.updates_all = (
            False  # Whether updates to members update the widget automatically
        )

        self.children = []
        self.active_animations = []

        self.active_keys = []

        self.title = title

        # Initialize canvas size
        if canvas_height == "default":
            canvas_height = self.height
        if canvas_width == "default":
            canvas_width = self.width

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Because of threading and garbage collection, images created will sometimes have to be stored in this variable to ensure they do not get deleted
        self.images = {}

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

        active_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )
        """
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
        """
        # If the new object is actually new, update the current active widget
        # self.active is used for things like detecting what widget to send keypresses to
        if active_new is not self.active:
            if self.active is not None:
                self.active.change_active()
            self.active = active_new

        # If the new object wasn't already being clicked
        if active_new is not self.down:
            self.down = active_new

            # If the new object is a valid widget
            if active_new is not None:
                # Click on the object with click position
                active_new.clicked(x, y)

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

        # If something is already being clicked on, this is also a dragging event on that widget.
        if self.down is not None:
            self.down.dragging(x, y)

        hovered_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )

        if hovered_new is not self.hovered and hovered_new is not None:
            hovered_new.hovered()
        """
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
                        print("hovered")
                        i[0].hovered()

                    # Set hovered_new and break
                    hovered_new = i[0]
                    break
        """
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

    # Handle keystrokes
    def typing(self, event):
        # If a widget == active, we should send keystrokes to it
        if self.active:
            self.active.typed(event)

        if event.keysym not in self.active_keys:
            self.active_keys.append(event.keysym)

    def typing_up(self, event):
        if event.keysym in self.active_keys:
            self.active_keys.remove(event.keysym)

    # NOTE: CREATION HANDLERS
    # These are necessary so that threading works properly with tcl

    # Wrapper for canvas.create_image method
    def create_image(self, x, y, image, state="normal"):
        img = self.canvas.create_image(
            x, y, image=image.tk_image(self), anchor="nw", state=state
        )
        return img, image

    # Wrapper for canvas.create_rectangle method
    def create_rectangle(
        self, x, y, widt, height=0, fill=0, border_width=0, outline=None, state="normal"
    ):
        if x == widt or y == height:
            return None, None
        # To support transparency with RGBA, we need to check whether the rectangle includes transparency
        if fill is not None and fill[7:] != "ff":
            bg_image = image_manager.create_image(
                fill, int(widt - x), int(height - y), outline, border_width, self
            )
            id, image = self.create_image(x, y, bg_image, state=state)
            return id, image

        # Otherwise we can continue with creating the rectangle
        return (
            self.canvas.create_rectangle(
                x + border_width / 2,
                y + border_width / 2,
                widt - border_width / 2,
                height - border_width / 2,
                fill=fill[:7],
                width=border_width,
                outline=outline[:7],
                state=state,
            ),
            None,
        )

    # Wrapper for canvas.create_text method
    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal", angle=0
    ):
        return (
            self.canvas.create_text(
                x,
                y,
                text=text,
                font=font,
                fill=fill,
                anchor=anchor,
                state=state,
                angle=angle,
            ),
            None,
        )

    # Wrapper for canvas.move method
    def move(self, _object, x, y):
        if _object is not None:
            self.canvas.move(_object, x, y)

    def object_place(self, _object, x, y):
        if _object is not None:
            coords = self.canvas.coords(_object)
            self.move(_object, x - coords[0], y - coords[1])

    # Wrapper for canvas.delete method
    def delete(self, _object):
        self.canvas.delete(_object)

    # Wrapper for canvas.change_state method
    def change_state(self, _object, state):
        self.canvas.itemconfigure(_object, state=state)

    # NOTE: Other methods

    # Handle window closing
    def close(self):
        self.running = False
        self.close_animations()
        try:
            self.root.update()
            self.root.quit()
            self.join()
        except Exception as e:
            print(e)
        if self.closing_command is not None:
            self.closing_command()

    def destroy(self):
        self.close()

    def close_animations(self):
        for anim in self.active_animations.copy():
            anim.stop()
            if anim.thread is not None:
                while anim.thread.is_alive():
                    self.root.update()
                    sleep(0.01)
                anim.thread.join()

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
            self.close_animations()
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
        self.canvas.bind_all("<KeyRelease>", self.typing_up)
        self.root.protocol("WM_DELETE_WINDOW", close)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", self.leave_window)

        # Run mainloop
        self.root.mainloop()

        # print("exited")
        # NOTE: The following code is an alternative, but broken, method of running mainloop
        """while self.running:
            self.root.update_idletasks()
            self.root.update()
            sleep(0.01)"""

    # Add resize method to change window dimensions
    def resize(self, width=None, height=None):
        """Resize the window to the specified dimensions.

        Args:
            width (int, optional): New width. If None, keeps current width.
            height (int, optional): New height. If None, keeps current height.

        Returns:
            self: Returns self for method chaining
        """
        if width is not None:
            self._size[0] = int(width)
        if height is not None:
            self._size[1] = int(height)

        # Update the window geometry
        self.root.geometry(f"{self.width}x{self.height}")

        # If canvas dimensions should match window, update those too
        if self.canvas_width == "default":
            self.canvas_width = self.width
            self.canvas.configure(width=self.width)
        if self.canvas_height == "default":
            self.canvas_height = self.height
            self.canvas.configure(height=self.height)

        # Update all children to match new dimensions
        self._update_children()

        return self

    # Add show method similar to widget show
    def _show(self, root):
        """Show the window if it was previously hidden.

        Returns:
            self: Returns self for method chaining
        """
        # Use deiconify to make window visible if it was withdrawn
        if self.root is not None:
            self.root.deiconify()
            self.update()

        return self

    # Add hide method similar to widget hide
    def _hide(self, root):
        """Hide the window without destroying it.

        Returns:
            self: Returns self for method chaining
        """
        # Use withdraw to hide window without destroying it
        if self.root is not None:
            self.root.withdraw()

        return self

    # Add configure method similar to widget configure
    # Also Wrapper for canvas.configure method
    def configure(self, _object=None, **kwargs):
        """Configure window properties.

        Supported properties:
        - width: Window width
        - height: Window height
        - title: Window title
        - resizable: Tuple of (width_resizable, height_resizable)

        Returns:
            self: Returns self for method chaining
        """
        if _object:
            self.canvas.itemconfigure(_object, kwargs)
            return self

        if "width" in kwargs or "height" in kwargs:
            self.resize(kwargs.get("width"), kwargs.get("height"))

        if "title" in kwargs:
            self.title = kwargs["title"]
            if self.root is not None:
                self.root.title(self.title)

        if "resizable" in kwargs:
            self.resizable = kwargs["resizable"]
            if type(self.resizable) is bool:
                self.resizable = (self.resizable, self.resizable)
            if self.root is not None:
                self.root.resizable(self.resizable[0], self.resizable[1])

        return self

    def update(self):
        self.root.update()
        return self


def Window(
    width=500,
    height=500,
    title=None,
    canvas_width="default",
    canvas_height="default",
    closing_command=None,
    resizable=(True, True),
    override=False,
):
    """Window constructor

    Args:
        width (int, optional): Width. Defaults to 500.
        height (int, optional): Height. Defaults to 500.
        title (str, optional): Title. Defaults to ntk.
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

    if title is None:
        title = "ntk"

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
    """canvas = Window(title=None, width=800, height=500).place(400, 300)
    Frame(canvas, image="examples/Images/background.png", width=500, height=500).place(
        0, 0
    )
    # Button(canvas,10,10,text="hahah").place()
    # Button(canvas,text="hahah").place(50,10)
    # Button(canvas,text="hihih", font = ("Helvetica",36)).place(100,100)
    img = image_manager.Image("examples/Images/main_button_inactive.png")
    btn = Button(
        canvas,
        image=img,
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        width=100,
        height=100,
        mode="toggle",
        border_width=2,
    )
    btn.place(0, 0)
    btn.place(100, 200)
    btn = Button(
        canvas,
        image=img,
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        width=300,
        height=300,
        mode="toggle",
        border_width=2,
    )
    btn.place(0, 0)
    btn.place(200, 200)
    img.flip().flip("vertical")
    btn = Button(
        canvas,
        image=img,
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        width=100,
        height=100,
        mode="toggle",
        border_width=2,
    )
    btn.place(0, 0)
    btn.place(300, 200)
    btn = (
        Button(
            canvas,
            text="hi",
            font=("Helvetica", 50),
            fill=[255, 67, 67, 45],
            border_width=2,
        )
        .place(0, 400)
        .place(100, 400)
    )
    btn.text = "hello"
    btn.update()
    Slider(
        canvas,
        width=100,
        height=20,
        slider_width=20,
        slider_height=20,
        slider_border_width=2,
        slider_fill="#ffaaaa",
    ).place(100, 100)

    Entry(
        canvas,
        text="hi",
        font=("Helvetica", 50),
        fill=[255, 67, 67, 45],
        border_width=2,
    ).place(0, 400).place(200, 400)
    # ImageButton(canvas,image="Images/test_inactive.png",active_image="Images/test_active.png").place(0,0)
    # btn_4 = Button(canvas,15,15,text="hahah").place(15,15)
    # btn_4.place(50,60)

    # Frame(canvas,30,30, border = "green").place(160,80)
    print(canvas.children)
    print(standard_methods.get_rect_points(btn))
    # canvas.destroy()
    window = Window(width=800, height=600)
    sleep(2)
    window.resize(1000, 800)  # Change size
    window.configure(title="New Title", resizable=(False, False))  # Change properties
    window.hide()  # Hide window
    sleep(4)
    window.show()"""
    window = Window(width=800, height=600)
    btn = Button(
        window,
        width=100,
        height=100,
        mode="toggle",
        border_width=2,
    )
    btn.place(0, 0)

    def animate_btn():
        btn.width = 100
        btn.height = 100
        btn.place(0, 0)
        btn.update()
        keyframes = [
            (
                1.0,
                {"x": 50, "y": 50},
                animation_controller.Curves.ease_in_quad,
            ),  # Move to (50, 50) in 1s
            (
                1,
                {"x": 100, "y": 100},
                animation_controller.Curves.bounce,
                1,
            ),  # Then to (100, 100) in 0.5s
            animation_controller.Animation(
                btn,
                {"x": 0, "y": 0},
                1,
                animation_controller.Curves.ease_out_cubic,
            ),  # Back to (0, 0) in 1s
            [animation_controller.Animation(btn, {"width": 50}, 2.5), 0],
        ]
        anim_group = animation_controller.AnimationGroup(btn, keyframes, steps=60)
        anim_group.start()

    btn2 = Button(
        window,
        text="animate",
        width=100,
        height=50,
        command=animate_btn,
    )
    btn2.place(100, 0)

    anim2 = animation_controller.AnimationGroup(
        btn2,
        [
            [animation_controller.Animation(btn2, {"width": 50}, 1), 0],
            [animation_controller.Animation(btn2, {"height": 100}, 1), 0],
        ],
        steps=60,
        looping=True,
    )
    anim2.start()
    Entry(window, width=100, height=50, text="hello").place(0, 100)

    widget = Button(window, text="hello", width=100, height=100, fill="#FF0000").place(
        200, 200
    )  # Red
    anim = animation_controller.Animation(
        widget, {"fill": "#00FF0000"}, duration=1.0, looping=True
    )  # Animate to green
    anim.start()


if __name__ == "__main__":
    __main__()
