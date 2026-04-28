from .base import Component

# Import modules needed for widget management
try:
    from .. import bounds_manager, standard_methods
except ImportError:
    import bounds_manager
    import standard_methods


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

        self._root.children.insert(0, self)
        self.children = []
        self.bounds = {}
        self.active = None
        self.down = None
        self.hovered_child = None
        self.updates_all = False
        self.defaults = self._window.defaults

        # Render pipeline marker: containers are composited as their own layers.
        self._is_container_layer = True

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
            root.children.insert(0, self)

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
        abs_x, abs_y = self._event_position_to_abs(x, y)

        active_new = self._find_deepest_hit(self.children, abs_x, abs_y)

        if active_new is not self.active:
            if self.active is not None:
                self.active.change_active()
            self.active = active_new

        if active_new is not self.down:
            self.down = active_new
            if active_new is not None:
                active_new.clicked(abs_x, abs_y)

    def click_up(self, event):
        if self.down:
            self.down.release()
            self.down = None

    def hover(self, event):
        x = int(event.x)
        y = int(event.y)
        abs_x, abs_y = self._event_position_to_abs(x, y)
        if self.down is not None:
            self.down.dragging(abs_x, abs_y)

        hovered_new = self._find_deepest_hit(self.children, abs_x, abs_y)

        if hovered_new is not self.hovered_child:
            if self.hovered_child is not None:
                self.hovered_child.hover_end()
            self.hovered_child = hovered_new
            if hovered_new is not None:
                hovered_new.hovered()

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

    def _show(self, root):
        pass

    def _hide(self, root):
        pass

    def place(self, x, y):
        self._container_x = x
        self._container_y = y
        self.request_redraw()
        return self

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

    def _event_position_to_abs(self, x, y):
        return standard_methods.rel_position_to_abs(self, self.x + x, self.y + y)

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

    def _iter_destroy_targets(self):
        for child in list(self.children):
            yield child
            yield from self._iter_child_destroy_targets(child)

    def _iter_child_destroy_targets(self, child):
        for nested_child in list(getattr(child, "children", [])):
            yield nested_child
            yield from self._iter_child_destroy_targets(nested_child)

    def _clear_interaction_targets(self, owner, targets):
        for attr in ("active", "down", "hovered", "hovered_child"):
            if getattr(owner, attr, None) in targets:
                setattr(owner, attr, None)

    def destroy(self):
        targets = {self, *self._iter_destroy_targets()}

        self._clear_interaction_targets(self, targets)
        self._clear_interaction_targets(self._window, targets)

        for child in list(self.children):
            child.destroy()
        self.children.clear()

        if hasattr(self._root, "children") and self in self._root.children:
            self._root.children.remove(self)

        self.request_redraw()

    def begin_render_batch(self):
        if hasattr(self._window, "begin_render_batch"):
            self._window.begin_render_batch()

    def end_render_batch(self):
        if hasattr(self._window, "end_render_batch"):
            self._window.end_render_batch()
