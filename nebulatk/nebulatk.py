import sys
import threading
import queue as std_queue

# Import python standard packages
from time import sleep


# Importing from another file works differently than if running this file directly for some reason.
# Import all required modules from nebulatk
if __package__:
    from . import (
        bounds_manager,
        fonts_manager,
        colors_manager,
        image_manager,
        standard_methods,
        defaults,
        animation_controller,
        taskbar_manager,
        rendering,
        file_manager,
    )

    # Import Component and _widget classes from widgets.base
    from .widgets.base import Component, _widget, _widget_properties

    # Import widget classes from widgets module
    from .widgets import Button, Label, Entry, Frame, Slider, Container

else:
    import bounds_manager
    import fonts_manager
    import colors_manager
    import image_manager
    import standard_methods
    import defaults
    import animation_controller
    import taskbar_manager
    import rendering
    import file_manager

    # Import Component and _widget classes from widgets.base
    from widgets.base import Component, _widget, _widget_properties

    # Import widget classes from widgets module
    from widgets import Button, Label, Entry, Frame, Slider, Container


FileDialog = file_manager.FileDialog


# Internal window class to implement threading
# NOTE: The window loop runs in its own thread.
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
        render_mode="image_gl",
        fps=60,
        background_color="FFFFFF",
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
        self.display = None
        self.renderer = None
        self.down = None
        self.active = None
        self.hovered = None
        self.resizable = resizable
        self.override = override
        self.render_mode = render_mode
        self.fps = fps
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
        self._startup_error = None
        self.closing_command = closing_command

        self.defaults = defaults.new()

        self._taskbar_manager = None
        self._render_batch_depth = 0
        self._window_thread_id = None
        self._ui_queue = std_queue.Queue()
        self._ui_queue_signal_scheduled = False
        self._ui_queue_lock = threading.Lock()
        self._redraw_needed = True
        self._resize_reflow_active = False
        self._resize_reference_window_size = (max(1, int(width)), max(1, int(height)))
        self.background_color = self._normalize_background_color(background_color)
        self.background = None

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
        raise AttributeError("taskbar_manager is read-only")

    def _normalize_background_color(self, color):
        if color is None:
            return "#FFFFFF"
        value = str(color).strip()
        if value == "":
            return "#FFFFFF"
        if not value.startswith("#"):
            value = f"#{value}"
        return value

    # NOTE: EVENT HANDLERS

    # Handle mouse clicked down event
    def click(self, event):
        # Mouse position == a float, so convert to integer
        x = int(event.x)
        y = int(event.y)

        active_new = self._find_deepest_hit(self.children, x, y)
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

        hovered_new = self._find_deepest_hit(self.children, x, y)

        if hovered_new is not self.hovered and hovered_new is not None:
            hovered_new.hovered()
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

    def _find_deepest_hit(self, children, x, y):
        for child in children:
            if not bounds_manager.check_hit(child, x, y):
                continue
            nested_children = getattr(child, "children", [])
            if nested_children:
                nested = self._find_deepest_hit(nested_children, x, y)
                if nested is not None:
                    return nested
            if getattr(child, "can_focus", True):
                return child
        return None

    # NOTE: CREATION HANDLERS
    # These are necessary so that threading works properly with tcl

    def _is_window_thread(self):
        return threading.get_ident() == self._window_thread_id

    def _execute_in_window_thread(self, callback, wait=True):
        if self._is_window_thread() or self.root is None:
            return callback()

        done = threading.Event()
        result = {"value": None, "error": None}
        self._ui_queue.put((callback, done, result))
        self._signal_ui_queue()

        if not wait:
            return None
        done.wait()
        if result["error"] is not None:
            raise result["error"]
        return result["value"]

    def _signal_ui_queue(self):
        if self.root is None:
            return
        with self._ui_queue_lock:
            if self._ui_queue_signal_scheduled:
                return
            self._ui_queue_signal_scheduled = True
        self.root.after(0, self._drain_ui_queue)

    def _drain_ui_queue(self):
        while True:
            try:
                callback, done, result = self._ui_queue.get_nowait()
            except std_queue.Empty:
                break
            try:
                result["value"] = callback()
            except Exception as exc:
                result["error"] = exc
            finally:
                done.set()
        with self._ui_queue_lock:
            self._ui_queue_signal_scheduled = False
        if not self._ui_queue.empty() and self.root is not None:
            self._signal_ui_queue()

    def _mark_redraw_needed(self):
        self._redraw_needed = True
        if self.renderer is not None and hasattr(self.renderer, "request_redraw"):
            self.renderer.request_redraw()

    def request_redraw(self):
        self._execute_in_window_thread(self._mark_redraw_needed, wait=False)

    def _iter_widgets(self, children=None):
        if children is None:
            children = self.children
        for child in children:
            yield child
            nested_children = getattr(child, "children", [])
            if nested_children:
                yield from self._iter_widgets(nested_children)

    def debug_font_resolution(self, widget=None, print_report=True):
        """Inspect runtime font resolution used by the renderer."""
        widgets = [widget] if widget is not None else list(self._iter_widgets())
        reports = []

        for current in widgets:
            text = getattr(current, "text", "")
            font_spec = getattr(current, "font", None)
            if text in ("", None) or font_spec is None:
                continue

            if self.renderer is not None and hasattr(
                self.renderer, "resolve_widget_font_debug"
            ):
                info = self.renderer.resolve_widget_font_debug(current)
            else:
                info = fonts_manager.get_font_debug_info(font_spec)

            if info is None:
                continue

            info = dict(info)
            info["widget_type"] = type(current).__name__
            reports.append(info)

        if print_report:
            for item in reports:
                print(
                    "[font-debug]"
                    f" widget={item['widget_type']}"
                    f" family={item['requested_family']}"
                    f" style={item['requested_style']}"
                    f" size={item['requested_size']}"
                    f" selected={item['selected_candidate']}"
                    f" loaded_path={item['loaded_font_path']}"
                    f" default_fallback={item['used_default_font']}"
                )

        return reports

    def _ensure_resize_baseline(self, widget, force=False):
        if not getattr(widget, "resize", False):
            return
        if force or not hasattr(widget, "_resize_reference"):
            widget._resize_reference = {
                "window_size": (max(1, int(self.width)), max(1, int(self.height))),
                "x": int(getattr(widget, "x", 0) or 0),
                "y": int(getattr(widget, "y", 0) or 0),
                "width": int(getattr(widget, "width", 0) or 0),
                "height": int(getattr(widget, "height", 0) or 0),
            }

    def _configure_surface_size(self, width, height):
        width = max(1, int(width))
        height = max(1, int(height))
        self.canvas_width = width
        self.canvas_height = height
        if self.renderer is not None:
            self.renderer.width = width
            self.renderer.height = height
            if hasattr(self.renderer, "request_redraw"):
                self.renderer.request_redraw()
        if self.display is not None and hasattr(self.display, "configure"):
            self.display.configure(width=width, height=height)

    def _apply_resizable_widgets(self, width, height):
        width = max(1, int(width))
        height = max(1, int(height))
        if self._resize_reflow_active:
            return
        self._resize_reflow_active = True
        if hasattr(self, "begin_render_batch"):
            self.begin_render_batch()
        try:
            for widget in self._iter_widgets():
                if not getattr(widget, "resize", False):
                    continue
                self._ensure_resize_baseline(widget)
                reference = getattr(widget, "_resize_reference", None)
                if reference is None:
                    continue

                ref_window_width, ref_window_height = reference["window_size"]
                scale_x = width / max(1, int(ref_window_width))
                scale_y = height / max(1, int(ref_window_height))

                widget._position = [
                    int(round(reference["x"] * scale_x)),
                    int(round(reference["y"] * scale_y)),
                ]
                widget._size = [
                    max(0, int(round(reference["width"] * scale_x))),
                    max(0, int(round(reference["height"] * scale_y))),
                ]
                if hasattr(widget, "_resize_widget_images"):
                    widget._resize_widget_images()
                if (
                    getattr(widget, "bounds_type", None) == "non-standard"
                    and hasattr(widget, "_images")
                    and widget._images.get("image") is not None
                ):
                    widget.bounds = (
                        bounds_manager.generate_bounds_for_nonstandard_image(
                            widget._images["image"].image
                        )
                    )
                widget._update_children()
        finally:
            if hasattr(self, "end_render_batch"):
                self.end_render_batch()
            self._resize_reflow_active = False

    def _sync_resize_state(self, width, height):
        width = max(1, int(width))
        height = max(1, int(height))
        if width == self.width and height == self.height:
            return
        self._size = [width, height]
        self._configure_surface_size(width, height)
        self._apply_resizable_widgets(width, height)
        self._mark_redraw_needed()

    def _sync_window_size_from_native(self):
        if self.root is None:
            return
        if not hasattr(self.root, "winfo_width") or not hasattr(
            self.root, "winfo_height"
        ):
            return
        width = int(self.root.winfo_width() or 0)
        height = int(self.root.winfo_height() or 0)
        if width <= 0 or height <= 0:
            return
        self._sync_resize_state(width, height)

    # NOTE: Other methods

    # Handle window closing

    def close(self):
        # signal the poller → mainloop quits on next tick
        self.running = False

        # stop any running animations
        self.close_animations()

        if self.root is not None:
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
                    if self.root is not None:
                        self.root.update()
                    sleep(0.01)
                anim.thread.join(timeout=1)

    # Add in window.place() to simplify tcl's root.geometry method
    def place(self, x=0, y=0):
        self._execute_in_window_thread(
            lambda: self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        )
        return self

    # Wrapper for root.bind() method, in future, add global keypress handling
    def bind(self, key, command):
        self._execute_in_window_thread(lambda: self.root.bind(key, command))

    # Main method
    def run(self):
        try:
            self._window_thread_id = threading.get_ident()
            # Create window
            self.root = rendering.NativeGLWindow(
                self.width,
                self.height,
                title=self.title,
                resizable=self.resizable,
                override=self.override,
            )
            self.renderer = rendering.PILImageRenderer(
                self, self.canvas_width, self.canvas_height, fps=self.fps
            )
            self.display = rendering.OpenGLImageDisplay(
                self.root, self.canvas_width, self.canvas_height
            )
            self.root.set_draw_callback(self.display.draw)
            self.canvas = self.display.canvas

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

            self.root.after(0, self._drain_ui_queue)
            self._render_tick()
            self.root.mainloop()
        except Exception as exc:
            self._startup_error = exc
            self.running = False

        # schedule a periodic check of `self.running`,
        # so that close() can break us out cleanly.

    # Add resize method to change window dimensions
    def resize(self, width=None, height=None):
        """Resize the window to the specified dimensions.

        Args:
            width (int, optional): New width. If None, keeps current width.
            height (int, optional): New height. If None, keeps current height.

        Returns:
            self: Returns self for method chaining
        """
        target_width = self.width if width is None else int(width)
        target_height = self.height if height is None else int(height)

        def _apply_resize():
            # Update the window geometry
            self.root.geometry(f"{target_width}x{target_height}")
            self._sync_resize_state(target_width, target_height)

        self._execute_in_window_thread(_apply_resize)

        return self

    # Add show method similar to widget show
    def _show(self, root):
        """Show the window if it was previously hidden.

        Returns:
            self: Returns self for method chaining
        """
        # Use deiconify to make window visible if it was withdrawn
        if self.root is not None:
            self._execute_in_window_thread(self.root.deiconify)
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
            self._execute_in_window_thread(self.root.withdraw)

        return self

    # Add configure method similar to widget configure
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
        if _object is not None:
            return self

        if "width" in kwargs or "height" in kwargs:
            self.resize(kwargs.get("width"), kwargs.get("height"))

        if "title" in kwargs:
            self.title = kwargs["title"]
            if self.root is not None:
                self._execute_in_window_thread(lambda: self.root.title(self.title))

        if "resizable" in kwargs:
            self.resizable = kwargs["resizable"]
            if type(self.resizable) is bool:
                self.resizable = (self.resizable, self.resizable)
            if self.root is not None:
                self._execute_in_window_thread(
                    lambda: self.root.resizable(self.resizable[0], self.resizable[1])
                )

        background_color = kwargs.get(
            "background_color", kwargs.get("background-color")
        )
        if background_color is not None:
            self.background_color = self._normalize_background_color(background_color)
            if self.background is not None:
                self.background.fill = self.background_color

        self.request_redraw()

        return self

    def update(self):
        if self.root is not None:
            self._execute_in_window_thread(self.root.update)
        return self

    def _render_tick(self):
        if self.renderer is None or self.root is None:
            return
        self._sync_window_size_from_native()
        if self._render_batch_depth > 0:
            self.root.after(max(1, int(1000 / max(1, self.fps))), self._render_tick)
            return
        frame = self.renderer.render_if_due()
        if frame is not None:
            self.display.show_frame(frame)
            self._redraw_needed = False
        self.root.after(max(1, int(1000 / max(1, self.fps))), self._render_tick)

    def begin_render_batch(self):
        self._render_batch_depth += 1

    def end_render_batch(self):
        self._render_batch_depth = max(0, self._render_batch_depth - 1)


def Window(
    width=500,
    height=500,
    title=None,
    canvas_width="default",
    canvas_height="default",
    closing_command=None,
    resizable=(True, True),
    override=False,
    render_mode="image_gl",
    fps=60,
    background_color="FFFFFF",
    **kwargs,
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
        background_color (str, optional): Window background color. Defaults to FFFFFF.

    Returns:
        _type_: _description_
    """
    # Create window

    if type(resizable) is bool:
        resizable = (resizable, resizable)

    if "background-color" in kwargs:
        background_color = kwargs.pop("background-color")
    if kwargs:
        raise TypeError(f"Unexpected Window arguments: {', '.join(kwargs.keys())}")

    if render_mode != "image_gl":
        raise ValueError(
            "This branch only supports render_mode='image_gl'. "
            "Use master for legacy tkinter canvas rendering."
        )

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
        render_mode,
        fps,
        background_color,
    )

    # Start window thread
    canvas.start()

    # Wait for window to be created, as it == in a separate thread and not blocking this thread
    while canvas.root is None and canvas._startup_error is None and canvas.is_alive():
        sleep(0.1)

    if canvas._startup_error is not None:
        raise RuntimeError(
            f"Failed to initialize OpenGL window backend: {canvas._startup_error}"
        ) from canvas._startup_error

    if canvas.root is None:
        raise RuntimeError("Window thread exited before creating a render window.")

    background = Frame(
        canvas,
        width=canvas.width,
        height=canvas.height,
        fill=canvas.background_color,
        border=None,
        border_width=0,
    ).place(0, 0)
    background.resize = True
    background.can_focus = False
    background.can_click = False
    canvas.background = background
    canvas._ensure_resize_baseline(background, force=True)

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
    canvas = Window(
        title=None, width=800, height=500, render_mode="image_gl", fps=60
    ).place(400, 300)
    print(
        fonts_manager.loadfont(
            r"C:\Users\reube\nebulatk\examples\Fonts\HARLOWSI.TTF", private=False
        )
    )
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
            font=("Harlow Solid Italic", 50),
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
        font=("Comic Sans MS", 50),
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

    def animate_btn():
        btn6.width = 100
        btn6.height = 100
        btn6.place(0, 0)
        btn6.update()
        keyframes = [
            (
                1.0,
                {"x": 50, "y": 50},
                animation_controller.Curves.ease_in_quad,
            ),  # Move to (50, 50) in 1s
        ]
        anim_group = animation_controller.AnimationGroup(
            btn6, keyframes, steps=60, looping=True
        )
        anim_group.start()

    btn6 = Button(
        window,
        image=img,
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        command=lambda: print("clicked", btn6.width),
    )
    canvas.debug_font_resolution()
    btn6.place(0, 0)
    sleep(2)
    print("resizing window")
    window.resize(1000, 800)  # Change size
    print("configuring window")
    window.configure(title="New Title", resizable=(False, False))  # Change properties
    print("hiding window")
    window.hide()  # Hide window
    sleep(4)
    window.show()
    window.taskbar_manager._initialize_custom_thumbnails()
    animate_btn()
    sleep(30)
    window.destroy()
    canvas.destroy()
    # window = Window()


if __name__ == "__main__":
    __main__()
