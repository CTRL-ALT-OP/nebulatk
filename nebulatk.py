# Import tkinter and filedialog
import tkinter as tk
from tkinter import filedialog as tkfile_dialog

# Import python standard packages
from time import sleep
import threading
import sys

# Importing from another file works differently than if running this file directly for some reason.
# Import all required modules from nebulatk
try:
    from . import image_manager
    from . import fonts_manager
    from . import bounds_manager
    from . import colors_manager
    from . import initialize
    from . import standard_methods
except ImportError:
    import image_manager
    import fonts_manager
    import bounds_manager
    import colors_manager
    import initialize
    import standard_methods


# Initialize base methods for all widgets.
# This is largely so we don't ever need to initialize methods that will never be used (e.g. hovered on a frame)
class _widget:

    def hovered(self):
        pass

    def hover_end(self):
        pass

    def clicked(self):
        pass

    def dragging(self, x, y):
        pass

    def release(self):
        pass

    def destroy(self):
        standard_methods.delete(self)

    def typed(self, character):
        pass

    def change_active(self):
        pass

    def hide(self):
        """Hide the widget"""
        self.visible = False

        # Flop off hides all items that are part of this widget
        standard_methods.flop_off(self)

        # Remove this widget from the bounds
        bounds_manager.remove_bounds(self, self.bounds_type)

        # Always return self on methods the user might call. this allows for chaining like button = Button().place().hide()
        return self

    def show(self):
        """Shows the widget"""
        # Show makes all items that are part of this widget v==ible
        standard_methods.flop_on(self)

        # Add this widget to bounds
        bounds_manager.update_bounds(self, self.x, self.y, self.bounds_type)
        return self

    # Default place behavior
    def place(self, x=0, y=0):
        """Place the widget at the specified position.

        Args:
            x (int, optional): x position. Defaults to 0.
            y (int, optional): y position. Defaults to 0.
        """
        x = int(x)
        y = int(y)

        if self.bg_object == None and self.image_object == None:
            standard_methods.place_bulk(self)
            if self.bg_object is not None and self.bounds_type == "box":
                self.object = self.bg_object
            elif self.image_object is not None:
                self.object = self.image_object
            else:
                self.object = self.text_object

        standard_methods.update_positions(self, x, y)
        bounds_manager.update_bounds(self, x, y, mode=self.bounds_type)

        self.x = x
        self.y = y

        if hasattr(self, "original_x"):
            self.original_x = x
            self.original_y = y

        return self

    def update(self):
        standard_methods.delete(self)
        self.place(self.x, self.y)
        
    
    # Default configure behavior
    def configure(self, x=None, y=None, width = None, height = None, text=None, fill="Default"):
        """Configure the widget with the specified parameters

        Args:
            x (int, optional): x position. Defaults to None.
            y (int, optional): y position. Defaults to None.
            text (str, optional): Text. Defaults to None.
            fill (color, optional): Fill color. Defaults to "Default".
        """
        if x is not None:
            # Update x position of all items in this widget
            standard_methods.update_positions(self, x, self.y)

        if y is not None:
            # Update y position of all items in this widget
            standard_methods.update_positions(self, self.x, y)

        if text is not None:
            # Update text in this widget
            if self.text_object is not None:
                self.master.configure(self.text_object, text=text)

            if self.active_text_object is not None:
                self.master.configure(self.active_text_object, text=text)

            self.text = text

        if fill != "Default":
            self.fill = fill
            self.update()
            
        if width is not None:
            self.width = width
            self.update()
            
        if height is not None:
            self.height = height
            self.update()
            
        
        # Update the bounds for this widget
        bounds_manager.update_bounds(self, x, y, mode=self.bounds_type)

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        if hasattr(self, "original_x"):
            self.original_x = x
            self.original_y = y
        return self


# Our implementation of tkinter's file_dialog.
# This mostly just exists so that the user doesn't have to import nebulatk and tkinter
def FileDialog(window, initialdir=None, mode="r", filetypes=[("All files", "*")]):
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


class Button(_widget):

    def __init__(
        self,
        root=None,
        width=0,
        height=0,
        text="",
        font=None,
        justify="center",
        text_color="default",
        active_text_color=None,
        fill="default",
        active_fill="default",
        border="default",
        border_width=0,
        image=None,
        active_image=None,
        hover_image=None,
        hover_image_active=None,
        bounds_type="default",
        command=None,
        command_off=None,
        state=False,
        mode="standard",
    ):
        """NebulaTk Button widget.

        Args:
            root (nebulatk.Window, optional): Root Window. Defaults to None.

            width (int, optional): width. Defaults to 0.
            height (int, optional): height. Defaults to 0.

            text (str, optional): text. Defaults to "".
            font (_type_, optional): Font. Font name, or font tuple. Defaults to None.
            justify (str, optional): Justification for text. Defaults to None.

            text_color (str, color): text color. Defaults to "default".
            active_text_color (color, optional): color. Defaults to None.

            fill (color, optional): Fill color. Defaults to "white".
            active_fill (color, optional): Active fill color

            border (color, optional): Border color. Defaults to "black".
            border_width (int, optional): Border width. Defaults to 0.

            image (str, optional): Image path. Defaults to None.
            active_image (str, optional): Image path. Defaults to None.
            hover_image (str, optional): Image path. Defaults to None.
            hover_image_active (str, optional): Image path. Defaults to None.

            bounds_type (str, optional): Defaults to "box" if image is not provided, or "nonstandard" otherwise.

            command (function, optional): Defaults to None.
            command_off (function, optional): Defaults to None.

            state (bool, optional): _description_. Defaults to False.
            mode (str, optional): _description_. Defaults to "standard".
        """

        # mode = "toggle" is equivalent to a tkinter checkbutton

        # Load most initial variables
        initialize.load_initial(
            self,
            root,
            width,
            height,
            border_width,
            justify,
            state,
            mode,
            command,
            command_off,
        )

        # Load our bounds type
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
            self, fill, active_fill, border, text_color, active_text_color
        )

        # Convert all of our colors to hexadecimal
        initialize.convert_all_colors(self)

    # Utilize our standard methods to manage hovering
    def hovered(self):
        if self.mode == "toggle":
            standard_methods.hovered_toggle(self)
        elif self.mode == "standard":
            standard_methods.hovered_standard(self)
        self.hovering = True

    def hover_end(self):
        standard_methods.hover_end(self)
        self.hovering = False

    # Utilize our standard methods to manage clicking
    def clicked(self):
        if self.mode == "toggle":
            standard_methods.clicked_toggle(self)

        elif self.mode == "standard":
            standard_methods.clicked_standard(self)

    # No standard method for releasing, most other widgets don't use this method
    def release(self):
        # We only need to do something if this == a standard button, and not a toggle button
        if self.mode == "standard":
            # Toggle state
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
        # We will be using self.entire_text, not self.text, as self.configure will change self.text to be the d==played slice of self.entire_text
        # Backspace character
        if character == "\x08":
            self.entire_text = self.entire_text[0:-1]

        # If the character == a v==ible character
        elif character in fonts_manager.ALPHANUMERIC_PLUS:
            self.entire_text = self.entire_text + character

        # Move end of d==play to the end of the text
        self.end = len(self.entire_text)

        # Get maximum length of characters we can fit in the widget
        max_length = fonts_manager.get_max_length(
            self.master, self.entire_text, self.font, self.width, self.end
        )

        # Configure d==play text to be the slice of text that we can fit in the widget
        self.master.configure(
            self.text_object, text=self.entire_text[self.end - max_length : self.end]
        )


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

        # Load most initial variables
        initialize.load_initial(self, root, width, height, border_width)

        # Load our bounds type
        initialize.load_bounds_type(self, bounds_type)

        # Load all of our images
        initialize.load_bulk_images(self, image=image)

        # Load all of our colors
        initialize.load_all_colors(self, fill=fill, border=border)

        # Convert all of our colors to hexadecimal
        initialize.convert_all_colors(self)


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
        return self.canvas.create_image(x, y, image=image, anchor="nw", state=state)

    # Wrapper for canvas.create_rectangle method
    def create_rectangle(
        self, x, y, widt, height=0, fill=0, border_width=0, outline=None, state="normal"
    ):
        # To support transparency with RGBA, we need to check whether the rectangle includes transparency
        if fill is not None:
            if len(fill) > 7:
                # If it ==, we need to create an image with transparency instead of a normal rectangle
                bg_image = image_manager.create_image(
                    fill, widt, height, outline, border_width
                )
                self.images.append(bg_image)
                return self.create_image(x, y, bg_image, state=state)
            
        # Otherwise we can continue with creating the rectangle
        return self.canvas.create_rectangle(
            x+border_width/2,
            y+border_width/2,
            widt-border_width/2,
            height-border_width/2,
            fill=fill,
            width=border_width,
            outline=outline,
            state=state,
        )

    # Wrapper for canvas.create_text method
    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal"
    ):
        return self.canvas.create_text(
            x, y, text=text, font=font, fill=fill, anchor=anchor, state=state
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
            self.root.quit()
        except Exception as e:
            print("exception" + e)
        if self.closing_command is not None:
            self.closing_command()

    # Add in window.place() to simplify tcl's root.geometry method
    def place(self, x=0, y=0):
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        return self
    
    # Wrapper for root.bind() method, in future, add global keypress handling
    def bind(self, key, command):
        self.root.bind(key,command)

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

        def close():
            self.running = False
            try:
                self.root.quit()
            except Exception as e:
                print("exception" + e)
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

    if type(resizable) == bool:
        resizable = (resizable, resizable)

    canvas = _window_internal(
        width, height, title, canvas_width, canvas_height, closing_command, resizable
    )

    # Start window thread
    canvas.start()

    # Wait for window to be created, as it == in a separate thread and not blocking this thread
    while canvas.root == None:
        sleep(0.1)

    # Return the window
    return canvas


# NOTE: EXAMPLE WINDOW
def __main__():
    canvas = Window()
    Frame(
        canvas,
        image="Images/background.png",
        width=500,
        height=500,
    ).place(0, 0)

    slider = Slider(
        canvas,
        height=50,
        width=20,
        fill=[67, 67, 67, 255],
        border_width=5,
    ).place(100, 60)

    """Button(
        canvas,
        text="hillo",
        fill=[255, 66, 66, 55],
        image="Images/main_button_inactive.png",
        active_image="Images/main_button_inactive2.png",
        hover_image="Images/main_button_active.png",
        hover_image_active="Images/main_button_active2.png",
        mode="toggle",
        command=lambda: slider.show(),
        command_off=lambda: slider.hide(),
    ).place(0, 0)"""

    Entry(
        canvas,
        text="sample entry widget",
        font=("Helvetica", 20),
        width=300,
        height=50,
        justify="right",
        fill=[0, 100, 0, 50],
        border_width=1,
        text_color="cobaltgreen",
    ).place(100, 0)

    Frame(canvas, 30, 30, border="green", fill=[0, 255, 0, 50]).place(160, 470)
    # FileDialog(canvas)


if __name__ == "__main__":
    __main__()
