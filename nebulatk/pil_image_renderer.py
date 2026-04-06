import time

from PIL import Image as PILImage
from PIL import ImageDraw

try:
    from . import fonts_manager, widget_appearance
except ImportError:
    import fonts_manager
    import widget_appearance


class PILImageRenderer:
    def __init__(self, window, width, height, fps=60):
        self.window = window
        self.width = int(width)
        self.height = int(height)
        self.fps = max(1, int(fps))
        self.frame_interval = 1.0 / self.fps
        self._last_render = 0.0
        self._last_frame = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self._redraw_requested = True

    def request_redraw(self):
        self._redraw_requested = True

    def _safe_attr(self, obj, name, default=None):
        return widget_appearance.safe_getattr(obj, name, default)

    def _is_widget_visible(self, widget, parent_visible=True):
        return widget_appearance.is_widget_visible(widget, parent_visible=parent_visible)

    def _is_container_layer_widget(self, widget):
        if self._safe_attr(widget, "_is_container_layer", False):
            return True
        return getattr(widget.__class__, "__name__", "") == "Container"

    def _composite_image(self, frame, source, dest_x, dest_y, clip_rect=None):
        if source is None:
            return
        source_width, source_height = source.size
        if source_width <= 0 or source_height <= 0:
            return

        dest_x = int(dest_x)
        dest_y = int(dest_y)

        clip_left, clip_top = 0, 0
        clip_right, clip_bottom = frame.size
        if clip_rect is not None:
            clip_left = max(clip_left, int(clip_rect[0]))
            clip_top = max(clip_top, int(clip_rect[1]))
            clip_right = min(clip_right, int(clip_rect[2]))
            clip_bottom = min(clip_bottom, int(clip_rect[3]))

        draw_left = max(dest_x, clip_left)
        draw_top = max(dest_y, clip_top)
        draw_right = min(dest_x + source_width, clip_right)
        draw_bottom = min(dest_y + source_height, clip_bottom)
        if draw_right <= draw_left or draw_bottom <= draw_top:
            return

        crop_left = draw_left - dest_x
        crop_top = draw_top - dest_y
        crop_right = crop_left + (draw_right - draw_left)
        crop_bottom = crop_top + (draw_bottom - draw_top)
        cropped = source.crop((crop_left, crop_top, crop_right, crop_bottom))
        frame.alpha_composite(cropped, (draw_left, draw_top))

    def _is_fully_opaque_color(self, color):
        if color is None:
            return False
        if isinstance(color, (tuple, list)):
            if len(color) == 4:
                return int(color[3]) >= 255
            if len(color) == 3:
                return True
            return False
        if isinstance(color, str):
            value = color.strip().lstrip("#")
            if len(value) == 6:
                return True
            if len(value) == 8:
                try:
                    return int(value[6:8], 16) >= 255
                except ValueError:
                    return False
            # Named color strings are opaque in PIL.
            return True
        return True

    def _intersects_clip(self, x, y, width, height, clip_rect):
        if clip_rect is None:
            return True
        if width <= 0 or height <= 0:
            return True
        left, top, right, bottom = (
            int(clip_rect[0]),
            int(clip_rect[1]),
            int(clip_rect[2]),
            int(clip_rect[3]),
        )
        return not (
            (x + width) <= left
            or x >= right
            or (y + height) <= top
            or y >= bottom
        )

    def _resolve_image(self, widget):
        return widget_appearance.resolve_image(widget)

    def _resolve_fill(self, widget):
        return widget_appearance.to_rgba(widget_appearance.resolve_fill(widget))

    def _resolve_text_fill(self, widget):
        return widget_appearance.to_rgba(widget_appearance.resolve_text_fill(widget))

    def _alpha_draw_rectangle(self, frame, bounds, fill=None, outline=None, width=0):
        """Draw rectangle via alpha compositing so transparent colors blend."""
        if self._is_fully_opaque_color(fill) and (
            outline is None or self._is_fully_opaque_color(outline)
        ):
            draw_ctx = ImageDraw.Draw(frame, "RGBA")
            draw_ctx.rectangle(bounds, fill=fill, outline=outline, width=width)
            return
        layer = PILImage.new("RGBA", frame.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")
        layer_draw.rectangle(bounds, fill=fill, outline=outline, width=width)
        frame.alpha_composite(layer)

    def _alpha_draw_text(self, frame, position, text, fill, font, anchor):
        """Draw text via alpha compositing for correct transparency behavior."""
        if self._is_fully_opaque_color(fill):
            draw_ctx = ImageDraw.Draw(frame, "RGBA")
            draw_ctx.text(position, text, fill=fill, font=font, anchor=anchor)
            return
        layer = PILImage.new("RGBA", frame.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")
        layer_draw.text(position, text, fill=fill, font=font, anchor=anchor)
        frame.alpha_composite(layer)

    def resolve_widget_font_debug(self, widget):
        """Return renderer-relevant font diagnostics for a text widget."""
        text = self._safe_attr(widget, "text", "")
        font_spec = self._safe_attr(widget, "font", None)
        if text in ("", None) or font_spec is None:
            return None
        info = fonts_manager.get_font_debug_info(font_spec)
        info["text_preview"] = str(text)[:40]
        info["text_length"] = len(str(text))
        return info

    def _draw_widget_body(self, frame, widget, abs_x, abs_y, clip_rect=None):
        width = int(self._safe_attr(widget, "width", 0) or 0)
        height = int(self._safe_attr(widget, "height", 0) or 0)
        border_width = int(self._safe_attr(widget, "border_width", 0) or 0)
        outline = widget_appearance.to_rgba(self._safe_attr(widget, "border", None))

        fill = self._resolve_fill(widget)
        if (
            width > 0
            and height > 0
            and (fill is not None or (outline is not None and border_width > 0))
        ):
            self._alpha_draw_rectangle(
                frame,
                [abs_x, abs_y, abs_x + width, abs_y + height],
                fill=fill,
                outline=outline,
                width=border_width,
            )

        img = self._resolve_image(widget)
        if img is not None:
            if getattr(img, "mode", None) != "RGBA":
                img = img.convert("RGBA")
            self._composite_image(
                frame,
                img,
                abs_x + border_width,
                abs_y + border_width,
                clip_rect=clip_rect,
            )

        text = self._safe_attr(widget, "text", "")
        font_spec = self._safe_attr(widget, "font", None)
        if text not in ("", None) and font_spec is not None:
            text_font = fonts_manager.resolve_draw_font(font_spec)
            justify = self._safe_attr(widget, "justify", "center")
            if justify == "left":
                text_x = abs_x
                anchor = "lm"
            elif justify == "right":
                text_x = abs_x + width
                anchor = "rm"
            else:
                text_x = abs_x + (width / 2)
                anchor = "mm"
            text_y = abs_y + (height / 2)
            self._alpha_draw_text(
                frame,
                (text_x, text_y),
                text,
                self._resolve_text_fill(widget),
                text_font,
                anchor,
            )

    def _draw_widget(
        self, frame, draw_ctx, widget, parent_x, parent_y, parent_visible=True
    ):
        if not self._is_widget_visible(widget, parent_visible=parent_visible):
            return
        abs_x = parent_x + int(self._safe_attr(widget, "x", 0) or 0)
        abs_y = parent_y + int(self._safe_attr(widget, "y", 0) or 0)
        self._draw_widget_body(frame, widget, abs_x, abs_y)

    def _render_container_layer(self, widget):
        width = int(self._safe_attr(widget, "width", 0) or 0)
        height = int(self._safe_attr(widget, "height", 0) or 0)
        if width <= 0 or height <= 0:
            return None

        container_layer = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_ctx = ImageDraw.Draw(container_layer, "RGBA")
        self._draw_widget_body(container_layer, widget, 0, 0)
        self._render_children(
            container_layer,
            draw_ctx,
            self._safe_attr(widget, "children", []),
            parent_x=0,
            parent_y=0,
            parent_visible=True,
            clip_rect=(0, 0, width, height),
        )
        return container_layer

    def _render_children(
        self,
        frame,
        draw_ctx,
        children,
        parent_x=0,
        parent_y=0,
        parent_visible=True,
        clip_rect=None,
    ):
        # Widget lists are kept front-to-back for hit testing (index 0 is topmost).
        # Rendering must be back-to-front so lower layers are painted first.
        for child in reversed(children):
            child_visible = self._is_widget_visible(child, parent_visible=parent_visible)
            if not child_visible:
                continue

            child_x = parent_x + int(self._safe_attr(child, "x", 0) or 0)
            child_y = parent_y + int(self._safe_attr(child, "y", 0) or 0)
            child_width = int(self._safe_attr(child, "width", 0) or 0)
            child_height = int(self._safe_attr(child, "height", 0) or 0)
            child_children = self._safe_attr(child, "children", [])
            if (
                clip_rect is not None
                and not self._intersects_clip(
                    child_x, child_y, child_width, child_height, clip_rect
                )
                and not child_children
            ):
                continue
            if self._is_container_layer_widget(child):
                container_layer = self._render_container_layer(child)
                if container_layer is not None:
                    self._composite_image(
                        frame,
                        container_layer,
                        child_x,
                        child_y,
                        clip_rect=clip_rect,
                    )
                    continue

            self._draw_widget_body(frame, child, child_x, child_y, clip_rect=clip_rect)
            if child_children:
                self._render_children(
                    frame,
                    draw_ctx,
                    child_children,
                    child_x,
                    child_y,
                    parent_visible=child_visible,
                    clip_rect=clip_rect,
                )

    def render_if_due(self):
        now = time.time()
        if now - self._last_render < self.frame_interval:
            return None
        if not self._redraw_requested:
            self._last_render = now
            return None

        frame = PILImage.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw_ctx = ImageDraw.Draw(frame, "RGBA")
        self._render_children(
            frame,
            draw_ctx,
            self.window.children,
            parent_x=0,
            parent_y=0,
            parent_visible=True,
        )
        self._last_render = now
        self._last_frame = frame
        self._redraw_requested = False
        return frame

    @property
    def last_frame(self):
        return self._last_frame
