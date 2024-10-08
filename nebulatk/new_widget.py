import colors_manager
import fonts_manager
import image_manager
import standard_methods
import bounds_manager


class _widget_properties:
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
    def fill(self):
        return self._colors["fill"]

    @fill.setter
    def fill(self, value):
        fill = self.__synthesize_color("fill", value, self._images["image"] is None)
        self._colors["fill"] = fill

        if self.initialized:
            self.update()

    @property
    def active_fill(self):
        return self._colors["active_fill"]

    @active_fill.setter
    def active_fill(self, value):
        active_fill = self.__synthesize_color(
            "active_fill", value, self._images["image"] is None
        )
        self._colors["active_fill"] = active_fill

        if self.initialized:
            self.update()

    @property
    def hover_fill(self):
        return self._colors["hover_fill"]

    @hover_fill.setter
    def hover_fill(self, value):
        hover_fill = self.__synthesize_color(
            "hover_fill", value, self._images["image"] is None
        )
        self._colors["hover_fill"] = hover_fill

        if self.initialized:
            self.update()

    @property
    def active_hover_fill(self):
        return self._colors["active_hover_fill"]

    @active_hover_fill.setter
    def active_hover_fill(self, value):
        active_hover_fill = self.__synthesize_color(
            "active_hover_fill", value, self._images["image"] is None
        )
        self._colors["active_hover_fill"] = active_hover_fill

        if self.initialized:
            self.update()

    @property
    def border(self):
        return self._colors["border"]

    @border.setter
    def border(self, value):
        border = self.__synthesize_color("border", value)
        self._colors["border"] = border

        if self.initialized:
            self.update()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
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

        self._bounds_type = value

        if self.initialized:
            self.update()

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        self._bounds = value

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
        fill: colors_manager.Color = "default_fill",
        active_fill: colors_manager.Color = "default_active_fill",
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

        self._root = None
        self.root = root

        self._size = [width, height]

        self._position = [0, 0]

        self._colors = {}

        self._images = {}

    def __synthesize_color(self, name, color, no_image=True):
        if no_image:
            return None
        if color == "default":
            color = self.master.defaults.get_attribute(f"default_{name}")
        else:
            color = colors_manager.Color(color)
        return color

    def __convert_image(self, image):
        return image_manager.Image(image) if type(image) is str else image

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
        fill: colors_manager.Color = "default_fill",
        active_fill: colors_manager.Color = "default_active_fill",
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
