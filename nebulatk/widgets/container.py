from .base import Component
from tkinter import Canvas
import tkinter as tk


class Container(Component):

    def __init__(
        self, root, width, height, fill=None, border=None, border_width=0, **kwargs
    ):
        pass

    def _bind_events(self):
        """Bind event handlers for mouse and keyboard events"""
        pass

    def click(self, event):
        pass

    def click_up(self, event):
        pass

    def hover(self, event):
        pass

    def leave_container(self, event):
        pass

    def typing(self, event):
        pass

    def typing_up(self, event):
        pass

    def move(self, _object, x, y):
        pass

    def object_place(self, _object, x, y):
        pass

    def delete(self, _object):
        pass

    def replicate_object(self, child):
        pass

    def _show(self, root):
        pass

    def _hide(self, root):
        pass

    def place(self, x, y):
        return self

    def _update_background_positions(self):
        pass

    # Event handler methods that widgets are expected to have
    def hovered(self):
        pass

    def hover_end(self):
        pass

    def clicked(self, x=None, y=None):
        pass

    def release(self):
        pass

    def dragging(self, x, y):
        pass

    def change_active(self):
        pass

    def _ensure_proper_layering(self):
        pass
