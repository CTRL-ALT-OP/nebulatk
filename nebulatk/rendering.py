import heapq
import itertools
import multiprocessing as mp
import queue as std_queue
import re
import threading
import time
import traceback
import ctypes
from dataclasses import dataclass

from PIL import Image as PILImage
from PIL import ImageDraw
from PIL import ImageFont

try:
    import glfw
    from OpenGL import GL
except Exception:
    glfw = None
    GL = None


def _to_rgba(color):
    if color is None:
        return None
    if isinstance(color, tuple):
        if len(color) == 4:
            return color
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
    if isinstance(color, str):
        value = color.strip().lstrip("#")
        if len(value) == 6:
            return (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                255,
            )
        if len(value) == 8:
            return (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                int(value[6:8], 16),
            )
    return color


@dataclass
class RenderObject:
    kind: str
    data: dict
    state: str = "normal"


class PILSurface:
    def __init__(self, width, height, x=0, y=0):
        self.width = int(width)
        self.height = int(height)
        self.x = int(x)
        self.y = int(y)
        self.objects = {}
        self._next_id = 1
        self._z_order = []
        self.dirty = True

    def _new_id(self):
        _id = self._next_id
        self._next_id += 1
        return _id

    def create_image(self, x, y, image, state="normal"):
        pil_image = getattr(image, "image", image)
        if pil_image is not None and getattr(pil_image, "mode", None) != "RGBA":
            pil_image = pil_image.convert("RGBA")
        _id = self._new_id()
        self.objects[_id] = RenderObject(
            kind="image",
            data={"x": int(x), "y": int(y), "image": pil_image},
            state=state,
        )
        self._z_order.append(_id)
        self.dirty = True
        return _id, image

    def create_rectangle(
        self,
        x,
        y,
        width,
        height=0,
        fill=None,
        border_width=0,
        outline=None,
        state="normal",
    ):
        _id = self._new_id()
        self.objects[_id] = RenderObject(
            kind="rectangle",
            data={
                "x1": int(x),
                "y1": int(y),
                "x2": int(width),
                "y2": int(height),
                "fill": _to_rgba(fill),
                "outline": _to_rgba(outline),
                "border_width": int(border_width or 0),
            },
            state=state,
        )
        self._z_order.append(_id)
        self.dirty = True
        return _id, None

    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal", angle=0
    ):
        _id = self._new_id()
        self.objects[_id] = RenderObject(
            kind="text",
            data={
                "x": int(x),
                "y": int(y),
                "text": text,
                "font": font,
                "fill": _to_rgba(fill),
                "anchor": anchor,
                "angle": angle,
            },
            state=state,
        )
        self._z_order.append(_id)
        self.dirty = True
        return _id, None

    def move(self, _object, x, y):
        if _object in self.objects:
            data = self.objects[_object].data
            for k in ("x", "x1", "x2"):
                if k in data:
                    data[k] += int(x)
            for k in ("y", "y1", "y2"):
                if k in data:
                    data[k] += int(y)
            self.dirty = True

    def object_place(self, _object, x, y):
        if _object in self.objects:
            obj = self.objects[_object]
            data = obj.data
            if obj.kind == "rectangle":
                w = data["x2"] - data["x1"]
                h = data["y2"] - data["y1"]
                data["x1"] = int(x)
                data["y1"] = int(y)
                data["x2"] = int(x) + w
                data["y2"] = int(y) + h
            else:
                data["x"] = int(x)
                data["y"] = int(y)
            self.dirty = True

    def delete(self, _object):
        if _object in self.objects:
            del self.objects[_object]
            if _object in self._z_order:
                self._z_order.remove(_object)
            self.dirty = True

    def change_state(self, _object, state):
        if _object in self.objects:
            self.objects[_object].state = state
            self.dirty = True

    def configure(self, _object, **kwargs):
        if _object in self.objects:
            obj = self.objects[_object]
            if obj.kind == "image" and "image" in kwargs:
                new_image = getattr(kwargs["image"], "image", kwargs["image"])
                if new_image is not None and getattr(new_image, "mode", None) != "RGBA":
                    new_image = new_image.convert("RGBA")
                kwargs["image"] = new_image
            self.objects[_object].data.update(kwargs)
            self.dirty = True

    def render(self):
        frame = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        for _id in self._z_order:
            obj = self.objects.get(_id)
            if obj is None or obj.state == "hidden":
                continue
            if obj.kind == "image":
                img = obj.data["image"]
                if img is not None:
                    x = obj.data["x"]
                    y = obj.data["y"]
                    frame.alpha_composite(img, (x, y))
            elif obj.kind == "rectangle":
                # Draw shapes/text on an intermediate transparent layer, then
                # alpha composite it. Drawing directly onto RGBA can replace
                # destination pixels instead of blending with them.
                layer = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                layer_draw = ImageDraw.Draw(layer)
                layer_draw.rectangle(
                    [obj.data["x1"], obj.data["y1"], obj.data["x2"], obj.data["y2"]],
                    fill=obj.data["fill"],
                    outline=obj.data["outline"],
                    width=obj.data["border_width"],
                )
                frame.alpha_composite(layer)
            elif obj.kind == "text":
                layer = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                layer_draw = ImageDraw.Draw(layer)
                try:
                    font_size = max(1, int(obj.data["font"][1]))
                    text_font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    text_font = ImageFont.load_default()
                layer_draw.text(
                    (obj.data["x"], obj.data["y"]),
                    obj.data["text"],
                    fill=obj.data["fill"],
                    font=text_font,
                    anchor={"center": "mm", "w": "lm", "e": "rm"}.get(
                        obj.data["anchor"], "mm"
                    ),
                )
                frame.alpha_composite(layer)
        self.dirty = False
        return frame


class PILImageRenderer:
    def __init__(self, width, height, fps=60):
        self.width = int(width)
        self.height = int(height)
        self.fps = max(1, int(fps))
        self.frame_interval = 1.0 / self.fps
        self.root_surface = PILSurface(self.width, self.height)
        self.container_surfaces = {}
        self._next_surface_id = 1
        self._last_render = 0.0
        self._last_frame = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self.dirty = True

    def create_container_surface(self, width, height, x=0, y=0):
        surface_id = self._next_surface_id
        self._next_surface_id += 1
        self.container_surfaces[surface_id] = PILSurface(width, height, x, y)
        self.dirty = True
        return surface_id

    def update_container_surface(
        self, surface_id, x=None, y=None, width=None, height=None
    ):
        surface = self.container_surfaces.get(surface_id)
        if not surface:
            return
        if x is not None:
            surface.x = int(x)
        if y is not None:
            surface.y = int(y)
        if width is not None and height is not None:
            if surface.width != int(width) or surface.height != int(height):
                surface.width = int(width)
                surface.height = int(height)
                surface.dirty = True
        self.dirty = True

    def remove_container_surface(self, surface_id):
        if surface_id in self.container_surfaces:
            del self.container_surfaces[surface_id]
            self.dirty = True

    def needs_redraw(self):
        if self.dirty or self.root_surface.dirty:
            return True
        return any(surface.dirty for surface in self.container_surfaces.values())

    def render_if_due(self):
        now = time.time()
        if now - self._last_render < self.frame_interval:
            return None
        if not self.needs_redraw():
            self._last_render = now
            return None

        frame = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        frame.alpha_composite(self.root_surface.render(), (0, 0))
        for surface in self.container_surfaces.values():
            frame.alpha_composite(surface.render(), (surface.x, surface.y))
        self._last_render = now
        self._last_frame = frame
        self.dirty = False
        return frame

    @property
    def last_frame(self):
        return self._last_frame


@dataclass
class NativeEvent:
    x: int = 0
    y: int = 0
    char: str = ""
    keysym: str = ""


_GLFW_LOCK = threading.Lock()
_GLFW_REFCOUNT = 0
_GLFW_API_LOCK = threading.RLock()


def _glfw_init_ref():
    global _GLFW_REFCOUNT
    with _GLFW_LOCK:
        if _GLFW_REFCOUNT == 0:
            if glfw is None or not glfw.init():
                return False
        _GLFW_REFCOUNT += 1
        return True


def _glfw_terminate_ref():
    global _GLFW_REFCOUNT
    with _GLFW_LOCK:
        if _GLFW_REFCOUNT <= 0:
            return
        _GLFW_REFCOUNT -= 1
        if _GLFW_REFCOUNT == 0 and glfw is not None:
            glfw.terminate()


class NativeGLWindow:
    """Process-backed GLFW window exposing a tkinter-like scheduling/event API."""

    def __init__(
        self, width, height, title="ntk", resizable=(True, True), override=False
    ):
        if glfw is None or GL is None:
            raise RuntimeError(
                "OpenGL backend unavailable. Install/enable glfw + PyOpenGL."
            )
        self._closed = False
        self._running = False
        self._bindings = {}
        self._protocol_handlers = {}
        self._draw_callback = None
        self._timers = []
        self._timer_counter = itertools.count()
        self._cancelled_timers = set()
        self._timers_lock = threading.Lock()
        self._clipboard_fallback = ""
        self._event_lock = threading.Lock()
        self._mouse_x = 0
        self._mouse_y = 0
        self._resizable = tuple(resizable)
        self._owner_thread_id = threading.get_ident()
        self._window = object()
        self._window_id = f"native-{id(self)}"
        self._sync_lock = threading.Lock()
        self._ctx = mp.get_context("spawn")
        self._command_queue = self._ctx.Queue()
        self._event_queue = self._ctx.Queue()
        self._response_queue = self._ctx.Queue()
        self._hwnd = 0
        self._process = self._ctx.Process(
            target=_native_window_process_main,
            args=(
                int(width),
                int(height),
                str(title),
                tuple(self._resizable),
                bool(override),
                self._window_id,
                self._command_queue,
                self._event_queue,
                self._response_queue,
            ),
            daemon=True,
        )
        self._process.start()
        self._wait_for_process_ready()

    @property
    def handle(self):
        return self._window

    def bind(self, key, command):
        self._bindings.setdefault(key, []).append(command)
        return command

    def protocol(self, name, command):
        self._protocol_handlers[name] = command

    def set_draw_callback(self, callback):
        self._draw_callback = callback

    def _dispatch(self, key, event):
        for callback in self._bindings.get(key, []):
            callback(event)

    def _is_owner_thread(self):
        return threading.get_ident() == self._owner_thread_id

    def _run_window_op(self, op):
        if self._window is None:
            return
        self._send_native_command(op)

    def _wait_for_process_ready(self):
        deadline = time.time() + 5.0
        while time.time() < deadline:
            self._process_events()
            if self._hwnd:
                return
            if not self._process.is_alive():
                break
            time.sleep(0.01)
        raise RuntimeError("Failed to initialize native window process.")

    def _send_native_command(self, command, expect_response=False, timeout=2.0):
        if self._window is None:
            return None
        payload = {"type": "command", "window_id": self._window_id, "command": command}
        if not expect_response:
            self._command_queue.put(payload)
            return None
        request_id = f"req-{next(self._timer_counter)}-{time.time_ns()}"
        payload["request_id"] = request_id
        with self._sync_lock:
            self._command_queue.put(payload)
            deadline = time.time() + timeout
            while time.time() < deadline:
                remaining = max(0.01, min(0.25, deadline - time.time()))
                try:
                    message = self._response_queue.get(timeout=remaining)
                except std_queue.Empty:
                    self._process_events()
                    continue
                if (
                    message.get("type") == "response"
                    and message.get("window_id") == self._window_id
                    and message.get("request_id") == request_id
                ):
                    return message.get("value")
                # Preserve unrelated async messages by routing through event handler.
                self._handle_process_message(message)
        return None

    def _handle_process_message(self, message):
        if not isinstance(message, dict):
            return
        msg_type = message.get("type")
        if msg_type == "ready" and message.get("window_id") == self._window_id:
            self._hwnd = int(message.get("hwnd") or 0)
            return
        if msg_type == "event" and message.get("window_id") == self._window_id:
            name = message.get("name")
            event = NativeEvent(
                x=int(message.get("x", 0)),
                y=int(message.get("y", 0)),
                keysym=str(message.get("keysym", "")),
                char=str(message.get("char", "")),
            )
            with self._event_lock:
                self._mouse_x, self._mouse_y = event.x, event.y
            self._dispatch(name, event)
            return
        if msg_type == "protocol" and message.get("window_id") == self._window_id:
            callback = self._protocol_handlers.get(message.get("name"))
            if callback is not None:
                callback()
            return
        if (
            msg_type == "closed"
            and message.get("window_id") == self._window_id
            and self._running
        ):
            self._running = False

    def _process_events(self):
        while True:
            try:
                message = self._event_queue.get_nowait()
            except std_queue.Empty:
                break
            self._handle_process_message(message)

    def _on_close_requested(self, _window):
        callback = self._protocol_handlers.get("WM_DELETE_WINDOW")
        if callback is not None:
            callback()
        else:
            self.quit()

    def _on_cursor_pos(self, _window, x, y):
        with self._event_lock:
            self._mouse_x, self._mouse_y = int(x), int(y)
            event = NativeEvent(x=int(x), y=int(y))
        self._dispatch("<Motion>", event)

    def _on_cursor_enter(self, _window, entered):
        if not entered:
            with self._event_lock:
                event = NativeEvent(x=self._mouse_x, y=self._mouse_y)
            self._dispatch("<Leave>", event)

    def _on_mouse_button(self, _window, button, action, _mods):
        with self._event_lock:
            event = NativeEvent(x=self._mouse_x, y=self._mouse_y)
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self._dispatch("<Button-1>", event)
        elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
            self._dispatch("<ButtonRelease-1>", event)

    def _on_char(self, _window, codepoint):
        # Character callback is kept for future direct text handling.
        self._clipboard_fallback = self._clipboard_fallback

    def _key_name(self, key):
        special = {
            glfw.KEY_BACKSPACE: "BackSpace",
            glfw.KEY_DELETE: "Delete",
            glfw.KEY_LEFT: "Left",
            glfw.KEY_RIGHT: "Right",
            glfw.KEY_HOME: "Home",
            glfw.KEY_END: "End",
            glfw.KEY_LEFT_SHIFT: "Shift_L",
            glfw.KEY_RIGHT_SHIFT: "Shift_R",
            glfw.KEY_LEFT_CONTROL: "Control_L",
            glfw.KEY_RIGHT_CONTROL: "Control_R",
            glfw.KEY_LEFT_SUPER: "Meta_L",
            glfw.KEY_RIGHT_SUPER: "Meta_R",
        }
        if key in special:
            return special[key]
        if glfw.KEY_A <= key <= glfw.KEY_Z:
            return chr(ord("a") + (key - glfw.KEY_A))
        name = glfw.get_key_name(key, 0)
        return name if name is not None else ""

    def _on_key(self, _window, key, scancode, action, _mods):
        keysym = self._key_name(key)
        char = glfw.get_key_name(key, scancode) or ""
        with self._event_lock:
            event = NativeEvent(x=self._mouse_x, y=self._mouse_y, keysym=keysym, char=char)
        if action in (glfw.PRESS, glfw.REPEAT):
            self._dispatch("<Key>", event)
        elif action == glfw.RELEASE:
            self._dispatch("<KeyRelease>", event)

    @property
    def available(self):
        return self._window is not None

    def after(self, ms, callback):
        timer_id = f"after#{next(self._timer_counter)}"
        due = time.time() + (max(0, int(ms)) / 1000.0)
        with self._timers_lock:
            heapq.heappush(self._timers, (due, next(self._timer_counter), timer_id, callback))
        self._send_native_command({"op": "wake"})
        return timer_id

    def after_cancel(self, timer_id):
        with self._timers_lock:
            self._cancelled_timers.add(timer_id)

    def _process_timers(self):
        now = time.time()
        ready = []
        with self._timers_lock:
            while self._timers and self._timers[0][0] <= now:
                ready.append(heapq.heappop(self._timers))
        for _, _, timer_id, callback in ready:
            if timer_id in self._cancelled_timers:
                self._cancelled_timers.discard(timer_id)
                continue
            try:
                callback()
            except Exception:
                traceback.print_exc()

    def geometry(self, geometry):
        if self._window is None:
            return
        match = re.match(r"^\s*(\d+)x(\d+)(?:\+(-?\d+)\+(-?\d+))?\s*$", geometry)
        if not match:
            return
        width = int(match.group(1))
        height = int(match.group(2))
        pos_x = int(match.group(3)) if match.group(3) is not None else None
        pos_y = int(match.group(4)) if match.group(4) is not None else None

        self._send_native_command(
            {
                "op": "geometry",
                "width": width,
                "height": height,
                "x": pos_x,
                "y": pos_y,
            }
        )

    def title(self, value):
        self._send_native_command({"op": "title", "value": str(value)})

    def resizable(self, can_resize_x, can_resize_y):
        self._resizable = (bool(can_resize_x), bool(can_resize_y))
        self._send_native_command(
            {
                "op": "resizable",
                "x": self._resizable[0],
                "y": self._resizable[1],
            }
        )

    def overrideredirect(self, override):
        self._send_native_command({"op": "override", "value": bool(override)})

    def wm_attributes(self, *_args, **_kwargs):
        return None

    def lift(self):
        self._send_native_command({"op": "focus"})

    def update(self):
        if self._window is None:
            return
        self._send_native_command({"op": "wake"})
        self._process_events()
        self._process_timers()

    def update_idletasks(self):
        self._process_timers()

    def withdraw(self):
        self._send_native_command({"op": "withdraw"})

    def deiconify(self):
        self._send_native_command({"op": "deiconify"})

    def clipboard_clear(self):
        self._clipboard_fallback = ""
        self._send_native_command({"op": "clipboard_set", "value": ""})

    def clipboard_append(self, value):
        text = str(value)
        self._clipboard_fallback = text
        self._send_native_command({"op": "clipboard_set", "value": text})

    def clipboard_get(self):
        if self._window is None:
            return self._clipboard_fallback
        value = self._send_native_command(
            {"op": "clipboard_get"}, expect_response=True, timeout=1.0
        )
        if value is None:
            if self._clipboard_fallback == "":
                raise RuntimeError("Clipboard is empty")
            return self._clipboard_fallback
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="ignore")
        return value

    def winfo_id(self):
        if self._window is None:
            return 0
        return int(self._hwnd or 0)

    def submit_frame(self, frame_rgba, width, height):
        if self._window is None:
            return
        self._send_native_command(
            {
                "op": "frame",
                "width": int(width),
                "height": int(height),
                "frame_rgba": frame_rgba,
            }
        )

    def mainloop(self):
        if self._window is None:
            return
        self._running = True
        while self._running:
            if self._window is None:
                break
            self._process_events()
            self._process_timers()
            time.sleep(0.001)
        self.destroy()

    def quit(self):
        self._running = False
        if self._window is not None:
            self._send_native_command({"op": "quit"})

    def destroy(self):
        if self._closed:
            return
        self._closed = True
        if self._window is not None:
            try:
                self._send_native_command({"op": "quit"})
            except Exception:
                pass
            if self._process is not None:
                self._process.join(timeout=1.0)
                if self._process.is_alive():
                    self._process.terminate()
                    self._process.join(timeout=1.0)
            self._window = None


def _native_window_process_key_name(key):
    special = {
        glfw.KEY_BACKSPACE: "BackSpace",
        glfw.KEY_DELETE: "Delete",
        glfw.KEY_LEFT: "Left",
        glfw.KEY_RIGHT: "Right",
        glfw.KEY_HOME: "Home",
        glfw.KEY_END: "End",
        glfw.KEY_LEFT_SHIFT: "Shift_L",
        glfw.KEY_RIGHT_SHIFT: "Shift_R",
        glfw.KEY_LEFT_CONTROL: "Control_L",
        glfw.KEY_RIGHT_CONTROL: "Control_R",
        glfw.KEY_LEFT_SUPER: "Meta_L",
        glfw.KEY_RIGHT_SUPER: "Meta_R",
    }
    if key in special:
        return special[key]
    if glfw.KEY_A <= key <= glfw.KEY_Z:
        return chr(ord("a") + (key - glfw.KEY_A))
    name = glfw.get_key_name(key, 0)
    return name if name is not None else ""


def _native_window_process_main(
    width,
    height,
    title,
    resizable,
    override,
    window_id,
    command_queue,
    event_queue,
    response_queue,
):
    if glfw is None or GL is None:
        return
    if not glfw.init():
        return

    try:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE if (resizable[0] or resizable[1]) else glfw.FALSE)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE if override else glfw.TRUE)

        window = glfw.create_window(int(width), int(height), str(title), None, None)
        if not window:
            return
        glfw.make_context_current(window)
        glfw.swap_interval(0)

        class _RootHandle:
            def __init__(self, handle):
                self.handle = handle

        display = OpenGLImageDisplay(_RootHandle(window), width, height)
        clipboard_fallback = ""
        mouse_state = {"x": 0, "y": 0}
        running = True

        def send_event(name, x=0, y=0, keysym="", char=""):
            event_queue.put(
                {
                    "type": "event",
                    "window_id": window_id,
                    "name": name,
                    "x": int(x),
                    "y": int(y),
                    "keysym": keysym,
                    "char": char,
                }
            )

        def on_close_requested(_window):
            event_queue.put(
                {
                    "type": "protocol",
                    "window_id": window_id,
                    "name": "WM_DELETE_WINDOW",
                }
            )
            glfw.set_window_should_close(_window, False)

        def on_cursor_pos(_window, x, y):
            mouse_state["x"], mouse_state["y"] = int(x), int(y)
            send_event("<Motion>", x, y)

        def on_cursor_enter(_window, entered):
            if not entered:
                send_event("<Leave>", mouse_state["x"], mouse_state["y"])

        def on_mouse_button(_window, button, action, _mods):
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                send_event("<Button-1>", mouse_state["x"], mouse_state["y"])
            elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
                send_event("<ButtonRelease-1>", mouse_state["x"], mouse_state["y"])

        def on_key(_window, key, scancode, action, _mods):
            keysym = _native_window_process_key_name(key)
            char = glfw.get_key_name(key, scancode) or ""
            if action in (glfw.PRESS, glfw.REPEAT):
                send_event("<Key>", mouse_state["x"], mouse_state["y"], keysym, char)
            elif action == glfw.RELEASE:
                send_event("<KeyRelease>", mouse_state["x"], mouse_state["y"], keysym, char)

        glfw.set_window_close_callback(window, on_close_requested)
        glfw.set_cursor_pos_callback(window, on_cursor_pos)
        glfw.set_cursor_enter_callback(window, on_cursor_enter)
        glfw.set_mouse_button_callback(window, on_mouse_button)
        glfw.set_key_callback(window, on_key)

        hwnd = glfw.get_win32_window(window) if hasattr(glfw, "get_win32_window") else 0
        event_queue.put({"type": "ready", "window_id": window_id, "hwnd": int(hwnd or 0)})

        while running and not glfw.window_should_close(window):
            glfw.poll_events()

            while True:
                try:
                    message = command_queue.get_nowait()
                except std_queue.Empty:
                    break

                if not isinstance(message, dict):
                    continue
                if message.get("window_id") != window_id:
                    continue
                command = message.get("command") or {}
                op = command.get("op")
                request_id = message.get("request_id")

                if op == "quit":
                    running = False
                    glfw.set_window_should_close(window, True)
                elif op == "wake":
                    pass
                elif op == "geometry":
                    glfw.set_window_size(
                        window, int(command.get("width", width)), int(command.get("height", height))
                    )
                    if command.get("x") is not None and command.get("y") is not None:
                        glfw.set_window_pos(window, int(command["x"]), int(command["y"]))
                elif op == "title":
                    glfw.set_window_title(window, str(command.get("value", "")))
                elif op == "resizable":
                    can_resize = bool(command.get("x")) or bool(command.get("y"))
                    glfw.set_window_attrib(
                        window, glfw.RESIZABLE, glfw.TRUE if can_resize else glfw.FALSE
                    )
                elif op == "override":
                    glfw.set_window_attrib(
                        window,
                        glfw.DECORATED,
                        glfw.FALSE if bool(command.get("value")) else glfw.TRUE,
                    )
                elif op == "withdraw":
                    glfw.hide_window(window)
                elif op == "deiconify":
                    glfw.show_window(window)
                elif op == "focus":
                    glfw.focus_window(window)
                elif op == "frame":
                    display.show_frame_bytes(
                        command.get("frame_rgba"),
                        int(command.get("width", width)),
                        int(command.get("height", height)),
                    )
                elif op == "clipboard_set":
                    clipboard_fallback = str(command.get("value", ""))
                    glfw.set_clipboard_string(window, clipboard_fallback)
                elif op == "clipboard_get":
                    value = glfw.get_clipboard_string(window)
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="ignore")
                    if value is None:
                        value = clipboard_fallback
                    response_queue.put(
                        {
                            "type": "response",
                            "window_id": window_id,
                            "request_id": request_id,
                            "value": value,
                        }
                    )

            try:
                display.draw()
                glfw.swap_buffers(window)
            except Exception:
                traceback.print_exc()
            time.sleep(0.001)
    finally:
        try:
            event_queue.put({"type": "closed", "window_id": window_id})
        except Exception:
            pass
        try:
            glfw.terminate()
        except Exception:
            pass


class OpenGLImageDisplay:
    def __init__(self, root, width, height):
        self._proxy_mode = hasattr(root, "submit_frame")
        self._enabled = glfw is not None and GL is not None
        self._texture_id = None
        self._program_id = None
        self._vbo_id = None
        self._vao_id = None
        self._pos_loc = -1
        self._uv_loc = -1
        self._sampler_loc = -1
        self._frame_rgba = None
        self._needs_texture_upload = False
        self._texture_size = (0, 0)
        self.width = int(width)
        self.height = int(height)
        self.root = root
        self.canvas = root

        if self._proxy_mode:
            return
        if not self._enabled:
            raise RuntimeError(
                "OpenGL backend unavailable. Install/enable glfw + PyOpenGL."
            )
        self._init_gl()

    def _init_gl(self):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self._texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        self._program_id = self._build_program()
        self._setup_fullscreen_quad()

    def _compile_shader(self, shader_type, source):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
            log = GL.glGetShaderInfoLog(shader)
            GL.glDeleteShader(shader)
            raise RuntimeError(f"OpenGL shader compile failed: {log}")
        return shader

    def _build_program(self):
        vertex_src_330 = """
        #version 330 core
        layout (location = 0) in vec2 a_pos;
        layout (location = 1) in vec2 a_uv;
        out vec2 v_uv;
        void main() {
            v_uv = a_uv;
            gl_Position = vec4(a_pos, 0.0, 1.0);
        }
        """
        fragment_src_330 = """
        #version 330 core
        in vec2 v_uv;
        out vec4 FragColor;
        uniform sampler2D u_texture;
        void main() {
            FragColor = texture(u_texture, v_uv);
        }
        """
        vertex_src_120 = """
        #version 120
        attribute vec2 a_pos;
        attribute vec2 a_uv;
        varying vec2 v_uv;
        void main() {
            v_uv = a_uv;
            gl_Position = vec4(a_pos, 0.0, 1.0);
        }
        """
        fragment_src_120 = """
        #version 120
        varying vec2 v_uv;
        uniform sampler2D u_texture;
        void main() {
            gl_FragColor = texture2D(u_texture, v_uv);
        }
        """

        variants = [
            (vertex_src_330, fragment_src_330, True),
            (vertex_src_120, fragment_src_120, False),
        ]
        last_error = None

        for vertex_src, fragment_src, explicit_locations in variants:
            program = None
            vertex = None
            fragment = None
            try:
                vertex = self._compile_shader(GL.GL_VERTEX_SHADER, vertex_src)
                fragment = self._compile_shader(GL.GL_FRAGMENT_SHADER, fragment_src)
                program = GL.glCreateProgram()
                GL.glAttachShader(program, vertex)
                GL.glAttachShader(program, fragment)
                if not explicit_locations:
                    GL.glBindAttribLocation(program, 0, "a_pos")
                    GL.glBindAttribLocation(program, 1, "a_uv")
                GL.glLinkProgram(program)
                if GL.glGetProgramiv(program, GL.GL_LINK_STATUS) != GL.GL_TRUE:
                    log = GL.glGetProgramInfoLog(program)
                    raise RuntimeError(f"OpenGL program link failed: {log}")
                GL.glDeleteShader(vertex)
                GL.glDeleteShader(fragment)
                self._pos_loc = GL.glGetAttribLocation(program, "a_pos")
                self._uv_loc = GL.glGetAttribLocation(program, "a_uv")
                self._sampler_loc = GL.glGetUniformLocation(program, "u_texture")
                return program
            except Exception as exc:
                last_error = exc
                if program is not None:
                    GL.glDeleteProgram(program)
                if vertex is not None:
                    GL.glDeleteShader(vertex)
                if fragment is not None:
                    GL.glDeleteShader(fragment)
                continue

        raise RuntimeError(f"Failed to initialize OpenGL shader pipeline: {last_error}")

    def _setup_fullscreen_quad(self):
        vertex_data = (
            -1.0,
            -1.0,
            0.0,
            1.0,
            1.0,
            -1.0,
            1.0,
            1.0,
            -1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
        )
        vertices = (ctypes.c_float * len(vertex_data))(*vertex_data)
        self._vbo_id = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo_id)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            ctypes.sizeof(vertices),
            vertices,
            GL.GL_STATIC_DRAW,
        )

        # Core profiles require a VAO; compatibility profiles can draw without one.
        if hasattr(GL, "glGenVertexArrays"):
            try:
                self._vao_id = GL.glGenVertexArrays(1)
                GL.glBindVertexArray(self._vao_id)
            except Exception:
                self._vao_id = None

        stride = 4 * 4
        if self._pos_loc >= 0:
            GL.glEnableVertexAttribArray(self._pos_loc)
            GL.glVertexAttribPointer(self._pos_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(0))
        if self._uv_loc >= 0:
            GL.glEnableVertexAttribArray(self._uv_loc)
            GL.glVertexAttribPointer(
                self._uv_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(8)
            )

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        if self._vao_id is not None:
            GL.glBindVertexArray(0)

    def show_frame(self, frame):
        rgba = frame.convert("RGBA")
        self.width, self.height = rgba.size
        frame_rgba = rgba.tobytes("raw", "RGBA")
        if self._proxy_mode:
            self.root.submit_frame(frame_rgba, self.width, self.height)
            return
        self._frame_rgba = frame_rgba
        self._needs_texture_upload = True

    def show_frame_bytes(self, frame_rgba, width, height):
        self.width = int(width)
        self.height = int(height)
        self._frame_rgba = frame_rgba
        self._needs_texture_upload = True

    def draw(self):
        if self._proxy_mode:
            return
        framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(self.root.handle)
        if framebuffer_width <= 0 or framebuffer_height <= 0:
            return
        # Keep content at a fixed pixel size and anchor to top-left.
        # Window resizing should change only the visible/canvas area, not scale content.
        viewport_x = 0
        viewport_y = framebuffer_height - self.height
        GL.glViewport(viewport_x, viewport_y, self.width, self.height)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if self._frame_rgba is None or self._texture_id is None:
            return

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        if self._needs_texture_upload:
            if self._texture_size != (self.width, self.height):
                GL.glTexImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    GL.GL_RGBA,
                    self.width,
                    self.height,
                    0,
                    GL.GL_RGBA,
                    GL.GL_UNSIGNED_BYTE,
                    self._frame_rgba,
                )
                self._texture_size = (self.width, self.height)
            else:
                GL.glTexSubImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    0,
                    0,
                    self.width,
                    self.height,
                    GL.GL_RGBA,
                    GL.GL_UNSIGNED_BYTE,
                    self._frame_rgba,
                )
            self._needs_texture_upload = False

        GL.glUseProgram(self._program_id)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        if self._sampler_loc >= 0:
            GL.glUniform1i(self._sampler_loc, 0)

        if self._vao_id is not None:
            GL.glBindVertexArray(self._vao_id)
        else:
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo_id)
            stride = 4 * 4
            if self._pos_loc >= 0:
                GL.glEnableVertexAttribArray(self._pos_loc)
                GL.glVertexAttribPointer(
                    self._pos_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(0)
                )
            if self._uv_loc >= 0:
                GL.glEnableVertexAttribArray(self._uv_loc)
                GL.glVertexAttribPointer(
                    self._uv_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(8)
                )

        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

        if self._vao_id is not None:
            GL.glBindVertexArray(0)
        else:
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            if self._pos_loc >= 0:
                GL.glDisableVertexAttribArray(self._pos_loc)
            if self._uv_loc >= 0:
                GL.glDisableVertexAttribArray(self._uv_loc)

        GL.glUseProgram(0)

    def configure(self, width=None, height=None):
        if width is not None:
            self.width = int(width)
        if height is not None:
            self.height = int(height)
