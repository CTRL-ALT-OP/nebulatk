import threading

# Import from parent module
try:
    from .. import (
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
