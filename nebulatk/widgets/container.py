from .base import Component

# Import modules needed for widget management
try:
    from .. import bounds_manager
except ImportError:
    import bounds_manager


class Container(Component):
    def __init__(
        self, root, width, height, fill=None, border=None, border_width=0, **kwargs
    ):
        self.initialized = False
        super().__init__(width, height)

        self._root = root
        self._window = self._resolve_window(root)
        self.master = self

        self._container_x = 0
        self._container_y = 0
        self._orientation = 0
        self.bounds_type = "default"
        self.state = False
        self.hovering = False
        self.visible = True
        self.can_focus = True
        self.can_hover = True
        self.can_click = True

        self._root.children.append(self)
        self.children = []
        self.bounds = {}
        self.active = None
        self.down = None
        self.hovered_child = None
        self.updates_all = False
        self.defaults = self._window.defaults

        self.maps = {}
        self._image_render_mode = True
        self.canvas = None

        self.initialized = True

    def _resolve_window(self, root):
        candidate = root
        if hasattr(candidate, "_window"):
            candidate = candidate._window
        while hasattr(candidate, "_window"):
            candidate = candidate._window
        return candidate

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        if self._root is not None:
            self._root.children.remove(self)
        self._root = root
        self._window = self._resolve_window(root)
        if root is not None:
            root.children.append(self)

    @property
    def x(self):
        return self._container_x

    @x.setter
    def x(self, x):
        self._container_x = x

    @property
    def y(self):
        return self._container_y

    @y.setter
    def y(self, y):
        self._container_y = y

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation

    @property
    def window(self):
        return self._window

    def _bind_events(self):
        return

    def click(self, event):
        x = int(event.x)
        y = int(event.y)

        active_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )

        if active_new is not self.active:
            if self.active is not None:
                self.active.change_active()
            self.active = active_new

        if active_new is not self.down:
            self.down = active_new
            if active_new is not None:
                active_new.clicked(x, y)

    def click_up(self, event):
        if self.down:
            self.down.release()
            self.down = None

    def hover(self, event):
        x = int(event.x)
        y = int(event.y)
        if self.down is not None:
            self.down.dragging(x, y)

        hovered_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )

        if hovered_new is not self.hovered_child:
            if self.hovered_child is not None:
                self.hovered_child.hover_end()
            self.hovered_child = hovered_new
            if hovered_new is not None:
                hovered_new.hovered()

    def leave_container(self, event):
        if self.hovered_child is not None:
            self.hovered_child.hover_end()
            self.hovered_child = None

    def typing(self, event):
        if self.active is not None and self.active.can_type:
            self.active.typed(event)

    def typing_up(self, event):
        pass

    def request_redraw(self):
        self._window.request_redraw()

    def configure(self, _object=None, **kwargs):
        if _object is not None:
            return
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.request_redraw()

    def replicate_object(self, child):
        return

    def _show(self, root):
        pass

    def _hide(self, root):
        pass

    def place(self, x, y):
        self._container_x = x
        self._container_y = y
        self.request_redraw()
        return self

    def _update_background_positions(self):
        return

    def hovered(self):
        self.hovering = True

    def hover_end(self):
        self.hovering = False

    def clicked(self, x=None, y=None):
        pass

    def release(self):
        pass

    def dragging(self, x, y):
        pass

    def change_active(self):
        pass

    def _ensure_proper_layering(self):
        return

    def begin_render_batch(self):
        if hasattr(self._window, "begin_render_batch"):
            self._window.begin_render_batch()

    def end_render_batch(self):
        if hasattr(self._window, "end_render_batch"):
            self._window.end_render_batch()
