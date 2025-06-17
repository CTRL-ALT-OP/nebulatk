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
        standard_methods,
        defaults,
        animation_controller,
        taskbar_manager,
    )

    # Import Component and _widget classes from widgets.base
    from .widgets.base import Component, _widget, _widget_properties

    # Import widget classes from widgets module
    from .widgets import Button, Label, Entry, Frame, Slider, Container

except ImportError:
    import bounds_manager
    import fonts_manager
    import colors_manager
    import image_manager
    import standard_methods
    import defaults
    import animation_controller
    import taskbar_manager

    # Import Component and _widget classes from widgets.base
    from widgets.base import Component, _widget, _widget_properties

    # Import widget classes from widgets module
    from widgets import Button, Label, Entry, Frame, Slider, Container


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

        self._taskbar_manager = None

    @property
    def taskbar_manager(self):
        if (
            self._taskbar_manager is None
            and sys.platform == "win32"
            and self.root is not None
        ):
            self._taskbar_manager = taskbar_manager.TaskbarManager(self)
        return self._taskbar_manager

    @taskbar_manager.setter
    def taskbar_manager(self, value):
        return "Cannot set taskbar_manager"

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
            x,
            y,
            image=image.tk_image(self),
            anchor="nw",
            state=state,
        )
        for child_canvas in self.children:
            if type(child_canvas).__name__ == "Container" and child_canvas.initialized:
                child_canvas.replicate_object(img)
                # Ensure background items stay behind container widgets
                child_canvas.canvas.tag_lower("background_item")
                if child_canvas.canvas.find_withtag("fg_item"):
                    child_canvas.canvas.tag_raise("fg_item")
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

        rect = self.canvas.create_rectangle(
            x + border_width / 2,
            y + border_width / 2,
            widt - border_width / 2,
            height - border_width / 2,
            fill=fill[:7],
            width=border_width,
            outline=outline[:7],
            state=state,
        )

        for child_canvas in self.children:
            if type(child_canvas).__name__ == "Container" and child_canvas.initialized:
                child_canvas.replicate_object(rect)
                # Ensure background items stay behind container widgets
                child_canvas.canvas.tag_lower("background_item")
                if child_canvas.canvas.find_withtag("fg_item"):
                    child_canvas.canvas.tag_raise("fg_item")
        return (rect, None)

    # Wrapper for canvas.create_text method
    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal", angle=0
    ):

        text_id = self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            fill=fill,
            anchor=anchor,
            state=state,
            angle=angle,
        )

        for child_canvas in self.children:
            if type(child_canvas).__name__ == "Container" and child_canvas.initialized:
                child_canvas.replicate_object(text_id)
                # Ensure background items stay behind container widgets
                child_canvas.canvas.tag_lower("background_item")
                if child_canvas.canvas.find_withtag("fg_item"):
                    child_canvas.canvas.tag_raise("fg_item")
        return (text_id, None)

    # Wrapper for canvas.move method
    def move(self, _object, x, y):
        if _object is not None:
            self.canvas.move(_object, x, y)
            for child_canvas in self.children:
                if (
                    type(child_canvas).__name__ == "Container"
                    and child_canvas.initialized
                ):
                    if _object in child_canvas.maps:
                        child_id = child_canvas.maps[_object]
                        child_canvas.canvas.move(child_id, x, y)
                    else:
                        # Only try to replicate if the object exists and is valid
                        try:
                            if _object in self.canvas.find_all():
                                child_canvas.replicate_object(_object)
                        except (tk.TclError, AttributeError):
                            # Object is invalid or doesn't exist, skip replication
                            pass

                        child_canvas.canvas.tag_lower("background_item")
                        if child_canvas.canvas.find_withtag("fg_item"):
                            child_canvas.canvas.tag_raise("fg_item")

    def object_place(self, _object, x, y):
        if _object is not None:
            coords = self.canvas.coords(_object)
            self.move(_object, x - coords[0], y - coords[1])

    # Wrapper for canvas.delete method
    def delete(self, _object):
        self.canvas.delete(_object)
        for child_canvas in self.children:
            if type(child_canvas).__name__ == "Container" and child_canvas.initialized:
                if _object in child_canvas.maps:
                    child_id = child_canvas.maps[_object]
                    child_canvas.canvas.delete(child_id)

    # Wrapper for canvas.change_state method
    def change_state(self, _object, state):
        self.canvas.itemconfigure(_object, state=state)
        for child_canvas in self.children:
            if type(child_canvas).__name__ == "Container" and child_canvas.initialized:
                if _object in child_canvas.maps:
                    child_id = child_canvas.maps[_object]
                    child_canvas.canvas.itemconfigure(child_id, state=state)
                else:
                    # Only try to replicate if the object exists and is valid
                    try:
                        if _object in self.canvas.find_all():
                            child_canvas.replicate_object(_object)
                    except (tk.TclError, AttributeError):
                        # Object is invalid or doesn't exist, skip replication
                        pass
                child_canvas.canvas.tag_lower("background_item")
                if child_canvas.canvas.find_withtag("fg_item"):
                    child_canvas.canvas.tag_raise("fg_item")

    # NOTE: Other methods

    # Handle window closing

    def close(self):
        # signal the poller → mainloop quits on next tick
        self.running = False

        # stop any running animations
        self.close_animations()

        self.root.after(200, self.root.quit)

        # wait up to a second for the thread to finish
        self.join(timeout=0.1)

        if self.closing_command:
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
                anim.thread.join(timeout=1)

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
        self.bind("<Button-1>", self.click)
        self.bind("<ButtonRelease-1>", self.click_up)
        self.bind("<Key>", self.typing)
        self.bind("<KeyRelease>", self.typing_up)
        self.root.protocol("WM_DELETE_WINDOW", close)
        self.bind("<Motion>", self.hover)
        self.bind("<Leave>", self.leave_window)

        self.root.mainloop()

        # schedule a periodic check of `self.running`,
        # so that close() can break us out cleanly:
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

    container = Container(window, width=200, height=50, fill="#FF0000")
    container.place(20, 10)
    print(container.maps)

    button5 = Button(container, text="hello", width=100, height=100, fill="#FF0000")
    button5.place(0, 0)

    window.taskbar_manager.SetProgress(20)


if __name__ == "__main__":
    __main__()
