import ctypes
from dataclasses import dataclass
import heapq
import itertools
import logging
import multiprocessing as mp
import os
import queue as std_queue
import re
import threading
import time
import traceback

try:
    import glfw
    from OpenGL import GL
except Exception:
    glfw = None
    GL = None

try:
    from .opengl_image_display import OpenGLImageDisplay
except ImportError:
    from opengl_image_display import OpenGLImageDisplay

logger = logging.getLogger(__name__)

_GLFW_SPECIAL_KEY_NAMES = {
    "KEY_BACKSPACE": "BackSpace",
    "KEY_DELETE": "Delete",
    "KEY_LEFT": "Left",
    "KEY_RIGHT": "Right",
    "KEY_HOME": "Home",
    "KEY_END": "End",
    "KEY_LEFT_SHIFT": "Shift_L",
    "KEY_RIGHT_SHIFT": "Shift_R",
    "KEY_LEFT_CONTROL": "Control_L",
    "KEY_RIGHT_CONTROL": "Control_R",
    "KEY_LEFT_SUPER": "Meta_L",
    "KEY_RIGHT_SUPER": "Meta_R",
}


def _glfw_key_name(key):
    if glfw is None:
        return ""

    special = {
        getattr(glfw, glfw_name): key_name
        for glfw_name, key_name in _GLFW_SPECIAL_KEY_NAMES.items()
        if hasattr(glfw, glfw_name)
    }
    if key in special:
        return special[key]
    if (
        hasattr(glfw, "KEY_A")
        and hasattr(glfw, "KEY_Z")
        and glfw.KEY_A <= key <= glfw.KEY_Z
    ):
        return chr(ord("a") + (key - glfw.KEY_A))
    name = glfw.get_key_name(key, 0)
    return name if name is not None else ""


def _is_text_input_char(value):
    if not isinstance(value, str) or len(value) != 1:
        return False
    if value in ("\n", "\r", "\t"):
        return False
    return value.isprintable()


def _uses_text_shortcut_modifiers(mods):
    if glfw is None:
        return False
    modifier_mask = 0
    for attr in ("MOD_CONTROL", "MOD_ALT", "MOD_SUPER"):
        if hasattr(glfw, attr):
            modifier_mask |= getattr(glfw, attr)
    return bool(mods & modifier_mask)


def _should_dispatch_keypress_event(keysym, char, mods):
    if _uses_text_shortcut_modifiers(mods):
        return True
    candidate = char or keysym
    return not _is_text_input_char(candidate)


def _native_window_process_key_name(key):
    return _glfw_key_name(key)


@dataclass
class NativeEvent:
    x: int = 0
    y: int = 0
    char: str = ""
    keysym: str = ""
    delta: int = 0
    delta_x: int = 0
    delta_y: int = 0
    num: int = 0


def _build_key_event(mouse_x, mouse_y, key=None, scancode=0):
    keysym = _glfw_key_name(key) if key is not None else ""
    char = ""
    if key is not None and glfw is not None:
        char = glfw.get_key_name(key, scancode) or ""
    return NativeEvent(x=int(mouse_x), y=int(mouse_y), keysym=keysym, char=char)


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
        self._startup_error = None
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
        deadline = time.time() + 10.0
        while time.time() < deadline:
            self._process_events()
            if self._hwnd:
                return
            if self._startup_error is not None:
                raise RuntimeError(
                    f"Failed to initialize native window process: {self._startup_error}"
                )
            if not self._process.is_alive():
                break
            time.sleep(0.01)
        if self._startup_error is not None:
            raise RuntimeError(
                f"Failed to initialize native window process: {self._startup_error}"
            )
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
        if msg_type == "error" and message.get("window_id") == self._window_id:
            self._startup_error = str(message.get("reason") or "unknown native error")
            return
        if msg_type == "event" and message.get("window_id") == self._window_id:
            name = message.get("name")
            event = NativeEvent(
                x=int(message.get("x", 0)),
                y=int(message.get("y", 0)),
                keysym=str(message.get("keysym", "")),
                char=str(message.get("char", "")),
                delta=int(message.get("delta", 0) or 0),
                delta_x=int(message.get("delta_x", 0) or 0),
                delta_y=int(message.get("delta_y", 0) or 0),
                num=int(message.get("num", 0) or 0),
            )
            with self._event_lock:
                self._mouse_x, self._mouse_y = event.x, event.y
            self._dispatch(name, event)
            return
        if msg_type == "protocol" and message.get("window_id") == self._window_id:
            callback = self._protocol_handlers.get(message.get("name"))
            if callback is not None:
                callback()
            # Acknowledge close-protocol delivery so the native process can
            # distinguish "owner handled this" from "owner thread disappeared".
            if message.get("name") == "WM_DELETE_WINDOW":
                self._send_native_command({"op": "close_request_handled"})
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

    def _key_name(self, key):
        return _glfw_key_name(key)

    @property
    def available(self):
        return self._window is not None

    def after(self, ms, callback):
        timer_id = f"after#{next(self._timer_counter)}"
        due = time.time() + (max(0, int(ms)) / 1000.0)
        with self._timers_lock:
            heapq.heappush(
                self._timers, (due, next(self._timer_counter), timer_id, callback)
            )
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

    def iconbitmap(self, value):
        if value is None:
            return
        icon_path = os.path.abspath(str(value))
        self._send_native_command({"op": "iconbitmap", "value": icon_path})

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

    def winfo_width(self):
        if self._window is None:
            return 0
        size = self._send_native_command(
            {"op": "get_size"}, expect_response=True, timeout=1.0
        )
        if not size:
            return 0
        return int(size.get("width", 0))

    def winfo_height(self):
        if self._window is None:
            return 0
        size = self._send_native_command(
            {"op": "get_size"}, expect_response=True, timeout=1.0
        )
        if not size:
            return 0
        return int(size.get("height", 0))

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
                logger.exception("Failed sending quit to native window process.")
            if self._process is not None:
                self._process.join(timeout=1.0)
                if self._process.is_alive():
                    self._process.terminate()
                    self._process.join(timeout=1.0)
            self._window = None


def _set_windows_window_icon(hwnd, icon_path):
    """Set a Win32 window icon from an .ico file path."""
    if not hwnd or not icon_path or os.name != "nt":
        return False
    try:
        user32 = ctypes.windll.user32
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1
        icon_size_small = 16
        icon_size_big = 32

        abs_path = os.path.abspath(str(icon_path))
        if not os.path.exists(abs_path):
            return False

        big_icon = user32.LoadImageW(
            0,
            abs_path,
            IMAGE_ICON,
            icon_size_big,
            icon_size_big,
            LR_LOADFROMFILE | LR_DEFAULTSIZE,
        )
        small_icon = user32.LoadImageW(
            0,
            abs_path,
            IMAGE_ICON,
            icon_size_small,
            icon_size_small,
            LR_LOADFROMFILE | LR_DEFAULTSIZE,
        )
        if not big_icon and not small_icon:
            return False

        if big_icon:
            user32.SendMessageW(int(hwnd), WM_SETICON, ICON_BIG, int(big_icon))
        if small_icon:
            user32.SendMessageW(int(hwnd), WM_SETICON, ICON_SMALL, int(small_icon))
        return True
    except Exception:
        return False


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
    def report_startup_error(reason):
        try:
            event_queue.put(
                {
                    "type": "error",
                    "window_id": window_id,
                    "reason": str(reason),
                }
            )
        except Exception:
            pass

    if glfw is None or GL is None:
        report_startup_error(
            "OpenGL backend unavailable (glfw or OpenGL module missing)."
        )
        return
    if not glfw.init():
        report_startup_error("glfw.init() failed.")
        return

    try:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
        glfw.window_hint(
            glfw.RESIZABLE, glfw.TRUE if (resizable[0] or resizable[1]) else glfw.FALSE
        )
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE if override else glfw.TRUE)

        window = glfw.create_window(int(width), int(height), str(title), None, None)
        if not window:
            report_startup_error("glfw.create_window() failed.")
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
        needs_present = True
        close_request_deadline = None

        def send_event(
            name,
            x=0,
            y=0,
            keysym="",
            char="",
            delta=0,
            delta_x=0,
            delta_y=0,
            num=0,
        ):
            event_queue.put(
                {
                    "type": "event",
                    "window_id": window_id,
                    "name": name,
                    "x": int(x),
                    "y": int(y),
                    "keysym": keysym,
                    "char": char,
                    "delta": int(delta),
                    "delta_x": int(delta_x),
                    "delta_y": int(delta_y),
                    "num": int(num),
                }
            )

        def send_response(request_id, value):
            if request_id is None:
                return
            response_queue.put(
                {
                    "type": "response",
                    "window_id": window_id,
                    "request_id": request_id,
                    "value": value,
                }
            )

        def on_close_requested(_window):
            nonlocal close_request_deadline
            event_queue.put(
                {
                    "type": "protocol",
                    "window_id": window_id,
                    "name": "WM_DELETE_WINDOW",
                }
            )
            # Keep the window open while the owner thread handles WM_DELETE_WINDOW.
            # If the owner is gone and never acknowledges, close anyway shortly
            # after to avoid a permanently stuck window.
            close_request_deadline = time.time() + 1.0
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

        def on_scroll(_window, xoffset, yoffset):
            # Match tkinter-style MouseWheel semantics (positive == scroll up).
            send_event(
                "<MouseWheel>",
                mouse_state["x"],
                mouse_state["y"],
                delta=int(round(float(yoffset) * 120.0)),
                delta_x=int(round(float(xoffset) * 120.0)),
                delta_y=int(round(float(yoffset) * 120.0)),
            )

        def on_key(_window, key, scancode, action, mods):
            event = _build_key_event(mouse_state["x"], mouse_state["y"], key, scancode)
            if action in (glfw.PRESS, glfw.REPEAT):
                if _should_dispatch_keypress_event(event.keysym, event.char, mods):
                    send_event("<Key>", event.x, event.y, event.keysym, event.char)
            elif action == glfw.RELEASE:
                send_event("<KeyRelease>", event.x, event.y, event.keysym, event.char)

        def on_char(_window, codepoint):
            try:
                char = chr(int(codepoint))
            except (TypeError, ValueError):
                return
            if not _is_text_input_char(char):
                return
            keysym = char.lower() if char.isalpha() else char
            send_event("<Key>", mouse_state["x"], mouse_state["y"], keysym, char)

        def on_window_refresh(_window):
            nonlocal needs_present
            needs_present = True

        def on_window_size(_window, _w, _h):
            nonlocal needs_present
            needs_present = True

        def on_framebuffer_size(_window, _w, _h):
            nonlocal needs_present
            needs_present = True

        glfw.set_window_close_callback(window, on_close_requested)
        glfw.set_cursor_pos_callback(window, on_cursor_pos)
        glfw.set_cursor_enter_callback(window, on_cursor_enter)
        glfw.set_mouse_button_callback(window, on_mouse_button)
        glfw.set_scroll_callback(window, on_scroll)
        glfw.set_key_callback(window, on_key)
        glfw.set_char_callback(window, on_char)
        glfw.set_window_refresh_callback(window, on_window_refresh)
        glfw.set_window_size_callback(window, on_window_size)
        glfw.set_framebuffer_size_callback(window, on_framebuffer_size)

        hwnd = glfw.get_win32_window(window) if hasattr(glfw, "get_win32_window") else 0
        event_queue.put(
            {"type": "ready", "window_id": window_id, "hwnd": int(hwnd or 0)}
        )

        def handle_quit(command, _request_id):
            nonlocal running
            running = False
            glfw.set_window_should_close(window, True)

        def handle_close_request_handled(command, _request_id):
            nonlocal close_request_deadline
            close_request_deadline = None

        def handle_wake(command, _request_id):
            nonlocal needs_present
            needs_present = True

        def handle_geometry(command, _request_id):
            nonlocal needs_present
            glfw.set_window_size(
                window,
                int(command.get("width", width)),
                int(command.get("height", height)),
            )
            if command.get("x") is not None and command.get("y") is not None:
                glfw.set_window_pos(window, int(command["x"]), int(command["y"]))
            needs_present = True

        def handle_title(command, _request_id):
            glfw.set_window_title(window, str(command.get("value", "")))

        def handle_resizable(command, _request_id):
            can_resize = bool(command.get("x")) or bool(command.get("y"))
            glfw.set_window_attrib(
                window, glfw.RESIZABLE, glfw.TRUE if can_resize else glfw.FALSE
            )

        def handle_override(command, _request_id):
            glfw.set_window_attrib(
                window,
                glfw.DECORATED,
                glfw.FALSE if bool(command.get("value")) else glfw.TRUE,
            )

        def handle_withdraw(command, _request_id):
            glfw.hide_window(window)

        def handle_deiconify(command, _request_id):
            nonlocal needs_present
            glfw.show_window(window)
            needs_present = True

        def handle_iconbitmap(command, _request_id):
            _set_windows_window_icon(hwnd, command.get("value"))

        def handle_focus(command, _request_id):
            glfw.focus_window(window)

        def handle_frame(command, _request_id):
            nonlocal needs_present
            display.show_frame_bytes(
                command.get("frame_rgba"),
                int(command.get("width", width)),
                int(command.get("height", height)),
            )
            needs_present = True

        def handle_clipboard_set(command, _request_id):
            nonlocal clipboard_fallback
            clipboard_fallback = str(command.get("value", ""))
            glfw.set_clipboard_string(window, clipboard_fallback)

        def handle_clipboard_get(command, request_id):
            value = glfw.get_clipboard_string(window)
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")
            if value is None:
                value = clipboard_fallback
            send_response(request_id, value)

        def handle_get_size(command, request_id):
            width_now, height_now = glfw.get_window_size(window)
            send_response(
                request_id,
                {
                    "width": int(width_now),
                    "height": int(height_now),
                },
            )

        command_handlers = {
            "quit": handle_quit,
            "close_request_handled": handle_close_request_handled,
            "wake": handle_wake,
            "geometry": handle_geometry,
            "title": handle_title,
            "resizable": handle_resizable,
            "override": handle_override,
            "withdraw": handle_withdraw,
            "deiconify": handle_deiconify,
            "iconbitmap": handle_iconbitmap,
            "focus": handle_focus,
            "frame": handle_frame,
            "clipboard_set": handle_clipboard_set,
            "clipboard_get": handle_clipboard_get,
            "get_size": handle_get_size,
        }

        while running and not glfw.window_should_close(window):
            had_commands = False
            while True:
                try:
                    message = command_queue.get_nowait()
                except std_queue.Empty:
                    break
                had_commands = True

                if not isinstance(message, dict):
                    continue
                if message.get("window_id") != window_id:
                    continue
                command = message.get("command") or {}
                op = command.get("op")
                request_id = message.get("request_id")

                handler = command_handlers.get(op)
                if handler is not None:
                    handler(command, request_id)

            if needs_present:
                glfw.poll_events()
                try:
                    display.draw()
                    glfw.swap_buffers(window)
                    needs_present = False
                except Exception:
                    traceback.print_exc()
            elif not had_commands:
                # Keep idle CPU low while avoiding frame-command wake latency.
                # A short timeout prevents visible stutter when animation frames
                # are submitted from the owner process while no GLFW events fire.
                glfw.wait_events_timeout(0.002)
            else:
                glfw.poll_events()
            if (
                close_request_deadline is not None
                and time.time() >= close_request_deadline
            ):
                running = False
                glfw.set_window_should_close(window, True)
    except Exception as exc:
        report_startup_error(f"Native window process exception: {exc}")
        traceback.print_exc()
    finally:
        try:
            event_queue.put({"type": "closed", "window_id": window_id})
        except Exception:
            pass
        try:
            glfw.terminate()
        except Exception:
            pass
