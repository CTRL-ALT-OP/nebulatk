"""Backwards-compatible facade for rendering implementation modules."""

import threading

try:
    from . import native_gl_window as _native
    from . import opengl_image_display as _opengl
    from . import pil_image_renderer as _pil
    from . import widget_appearance
except ImportError:
    import native_gl_window as _native
    import opengl_image_display as _opengl
    import pil_image_renderer as _pil
    import widget_appearance


time = _pil.time
glfw = _native.glfw
GL = _native.GL


def _glfw_key_name(key):
    if glfw is None:
        return ""

    special = {
        getattr(glfw, glfw_name): key_name
        for glfw_name, key_name in _native._GLFW_SPECIAL_KEY_NAMES.items()
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
    return _native._is_text_input_char(value)


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


def _to_rgba(color):
    return widget_appearance.to_rgba(color)


class PILImageRenderer(_pil.PILImageRenderer):
    pass


class NativeEvent(_native.NativeEvent):
    pass


class NativeGLWindow(_native.NativeGLWindow):
    # Keep compatibility with monkeypatching rendering.glfw in tests.
    def _key_name(self, key):
        return _glfw_key_name(key)

    def _on_key(self, _window, key, scancode, action, mods):
        keysym = self._key_name(key)
        char = glfw.get_key_name(key, scancode) or ""
        with self._event_lock:
            event = NativeEvent(
                x=self._mouse_x, y=self._mouse_y, keysym=keysym, char=char
            )
        if action in (glfw.PRESS, glfw.REPEAT):
            if _should_dispatch_keypress_event(keysym, char, mods):
                self._dispatch("<Key>", event)
        elif action == glfw.RELEASE:
            self._dispatch("<KeyRelease>", event)

    def _on_char(self, _window, codepoint):
        try:
            char = chr(int(codepoint))
        except (TypeError, ValueError):
            return
        if not _is_text_input_char(char):
            return
        keysym = char.lower() if char.isalpha() else char
        with self._event_lock:
            event = NativeEvent(
                x=self._mouse_x, y=self._mouse_y, keysym=keysym, char=char
            )
        self._dispatch("<Key>", event)

    def _on_mouse_button(self, _window, button, action, _mods):
        with self._event_lock:
            event = NativeEvent(x=self._mouse_x, y=self._mouse_y)
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self._dispatch("<Button-1>", event)
        elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
            self._dispatch("<ButtonRelease-1>", event)

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

    def _on_close_requested(self, _window):
        callback = self._protocol_handlers.get("WM_DELETE_WINDOW")
        if callback is not None:
            callback()
        else:
            self.quit()


class OpenGLImageDisplay(_opengl.OpenGLImageDisplay):
    pass


def _native_window_process_key_name(key):
    return _glfw_key_name(key)


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
    _native.glfw = glfw
    _native.GL = GL
    _native._native_window_process_main(
        width,
        height,
        title,
        resizable,
        override,
        window_id,
        command_queue,
        event_queue,
        response_queue,
    )
