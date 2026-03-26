import time
import tkinter as tk
from dataclasses import dataclass

from PIL import Image as PILImage
from PIL import ImageDraw
from PIL import ImageFont

try:
    from pyopengltk import OpenGLFrame
    from OpenGL import GL
except Exception:
    OpenGLFrame = None
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
        self, x, y, width, height=0, fill=None, border_width=0, outline=None, state="normal"
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
        draw = ImageDraw.Draw(frame)
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
                draw.rectangle(
                    [obj.data["x1"], obj.data["y1"], obj.data["x2"], obj.data["y2"]],
                    fill=obj.data["fill"],
                    outline=obj.data["outline"],
                    width=obj.data["border_width"],
                )
            elif obj.kind == "text":
                try:
                    font_size = max(1, int(obj.data["font"][1]))
                    text_font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    text_font = ImageFont.load_default()
                draw.text(
                    (obj.data["x"], obj.data["y"]),
                    obj.data["text"],
                    fill=obj.data["fill"],
                    font=text_font,
                    anchor={"center": "mm", "w": "lm", "e": "rm"}.get(
                        obj.data["anchor"], "mm"
                    ),
                )
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

    def update_container_surface(self, surface_id, x=None, y=None, width=None, height=None):
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


class OpenGLImageDisplay:
    def __init__(self, root, width, height):
        self._enabled = OpenGLFrame is not None and GL is not None
        self._texture_id = None
        self._frame_rgba = None
        self.width = int(width)
        self.height = int(height)

        if not self._enabled:
            raise RuntimeError(
                "OpenGL backend unavailable. Install/enable PyOpenGL and pyopengltk."
            )

        parent = self

        class _Frame(OpenGLFrame):
            def initgl(self_inner):
                GL.glDisable(GL.GL_DEPTH_TEST)
                GL.glEnable(GL.GL_TEXTURE_2D)
                parent._texture_id = GL.glGenTextures(1)
                GL.glBindTexture(GL.GL_TEXTURE_2D, parent._texture_id)
                GL.glTexParameteri(
                    GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR
                )
                GL.glTexParameteri(
                    GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR
                )

            def redraw(self_inner):
                GL.glViewport(0, 0, parent.width, parent.height)
                GL.glClearColor(0, 0, 0, 0)
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)
                if parent._frame_rgba is None:
                    return
                GL.glBindTexture(GL.GL_TEXTURE_2D, parent._texture_id)
                GL.glTexImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    GL.GL_RGBA,
                    parent.width,
                    parent.height,
                    0,
                    GL.GL_RGBA,
                    GL.GL_UNSIGNED_BYTE,
                    parent._frame_rgba,
                )
                GL.glBegin(GL.GL_QUADS)
                GL.glTexCoord2f(0, 1)
                GL.glVertex2f(-1, -1)
                GL.glTexCoord2f(1, 1)
                GL.glVertex2f(1, -1)
                GL.glTexCoord2f(1, 0)
                GL.glVertex2f(1, 1)
                GL.glTexCoord2f(0, 0)
                GL.glVertex2f(-1, 1)
                GL.glEnd()

        self.frame = _Frame(root, width=width, height=height)
        self.frame.pack(fill="both", expand=True)
        self.canvas = self.frame

    @property
    def available(self):
        return self._enabled

    def show_frame(self, frame):
        self._frame_rgba = frame.convert("RGBA").tobytes("raw", "RGBA")
        # Use the frame display pipeline so the GL context is made current
        # before invoking user redraw logic.
        if getattr(self.frame, "context_created", False):
            self.frame.after(0, self.frame._display)

    def configure(self, width=None, height=None):
        if width is not None:
            self.width = int(width)
            self.frame.configure(width=self.width)
        if height is not None:
            self.height = int(height)
            self.frame.configure(height=self.height)

