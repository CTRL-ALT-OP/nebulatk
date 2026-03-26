import os
import sys
import time
from statistics import mean, pstdev
from unittest.mock import patch

from PIL import Image as PILImage
from PIL import ImageDraw

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk


def _log_perf(label, **metrics):
    metric_blob = ", ".join(f"{key}={value}" for key, value in metrics.items())
    print(f"[perf] {label}: {metric_blob}")


def _close_window_safe(window):
    try:
        window.close()
    except RuntimeError as exc:
        _log_perf("window close warning", error=repr(exc))


def _wait_for_renderer(window, timeout_s=2.0):
    deadline = time.perf_counter() + timeout_s
    while window.renderer is None and time.perf_counter() < deadline:
        time.sleep(0.01)
    assert window.renderer is not None


def _wait_for_frame(window, timeout_s=0.8):
    deadline = time.perf_counter() + timeout_s
    frame = None
    while frame is None and time.perf_counter() < deadline:
        frame = window.renderer.render_if_due()
        if frame is None:
            time.sleep(window.renderer.frame_interval)
    return frame if frame is not None else window.renderer.last_frame


def _count_visible_pixels(frame):
    rgba = frame.convert("RGBA").getdata()
    return sum(1 for px in rgba if px[3] > 0)


def _build_button_grid(window, rows=10, cols=10):
    buttons = []
    for row in range(rows):
        for col in range(cols):
            button = ntk.Button(
                window,
                width=60,
                height=28,
                fill="#2d2d2d",
                text_color="#ffffff",
                text="",
            ).place(col * 62, row * 30)
            buttons.append(button)
    return buttons


def _create_button_variant_images():
    size = (56, 24)
    variants = {
        "image": ("#3355cc", "#aac0ff"),
        "hover_image": ("#3a8f3a", "#bde8bd"),
        "active_image": ("#b13f3f", "#f2c3c3"),
        "active_hover_image": ("#6e3ca8", "#d7c3f1"),
    }

    pil_variants = {}
    for key, (fill, outline) in variants.items():
        img = PILImage.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [0, 0, size[0] - 1, size[1] - 1],
            radius=6,
            fill=fill,
            outline=outline,
            width=2,
        )
        pil_variants[key] = img
    return pil_variants


def _build_image_button_grid(window, pil_variants, rows=10, cols=10):
    image = ntk.image_manager.Image(pil_variants["image"].copy())
    hover_image = ntk.image_manager.Image(pil_variants["hover_image"].copy())
    active_image = ntk.image_manager.Image(pil_variants["active_image"].copy())
    active_hover_image = ntk.image_manager.Image(pil_variants["active_hover_image"].copy())

    buttons = []
    for row in range(rows):
        for col in range(cols):
            button = ntk.Button(
                window,
                width=60,
                height=28,
                image=image,
                hover_image=hover_image,
                active_image=active_image,
                active_hover_image=active_hover_image,
                mode="toggle",
            ).place(col * 62, row * 30)
            buttons.append(button)
    return buttons


def _measure_build_and_first_render_time(window, builder):
    start = time.perf_counter()
    widgets = builder(window)
    frame = _wait_for_frame(window)
    end = time.perf_counter()
    assert frame is not None
    return widgets, frame, end - start


def test_render_100_button_grid_outputs_frame_pixels():
    window = ntk.Window(
        title="Render output test",
        width=700,
        height=360,
        render_mode="image_gl",
        fps=1000,
    )
    try:
        _wait_for_renderer(window)
        widgets, frame, elapsed = _measure_build_and_first_render_time(
            window, _build_button_grid
        )
        visible_pixels = _count_visible_pixels(frame)
        object_count = len(window.renderer.root_surface.objects)
        _log_perf(
            "100 solid buttons first render",
            elapsed_s=f"{elapsed:.6f}",
            object_count=object_count,
            visible_pixels=visible_pixels,
        )
        assert len(widgets) == 100
        assert elapsed > 0

        # Data-structure assertion: OpenGL path stores drawables in root surface.
        assert object_count >= 300

        # Rendered-image assertion: frame should contain many visible pixels.
        assert visible_pixels > 30000
    finally:
        _close_window_safe(window)


def test_render_100_image_button_grid_has_image_objects_and_pixels():
    pil_variants = _create_button_variant_images()
    window = ntk.Window(
        title="Image render output test",
        width=700,
        height=360,
        render_mode="image_gl",
        fps=1000,
    )
    try:
        _wait_for_renderer(window)
        widgets, frame, _ = _measure_build_and_first_render_time(
            window,
            lambda w: _build_image_button_grid(w, pil_variants, rows=10, cols=10),
        )
        visible_pixels = _count_visible_pixels(frame)
        assert len(widgets) == 100

        kinds = [obj.kind for obj in window.renderer.root_surface.objects.values()]
        _log_perf(
            "100 image buttons first render",
            object_count=len(kinds),
            image_object_count=kinds.count("image"),
            visible_pixels=visible_pixels,
        )
        assert "image" in kinds
        assert visible_pixels > 20000
    finally:
        _close_window_safe(window)


def test_image_gl_first_render_time_stable_over_runs():
    times = []
    for run_idx in range(5):
        window = ntk.Window(
            title="ImageGL timing",
            width=700,
            height=360,
            render_mode="image_gl",
            fps=1000,
        )
        try:
            _wait_for_renderer(window)
            _, _, elapsed = _measure_build_and_first_render_time(window, _build_button_grid)
            times.append(elapsed)
            _log_perf("first render run", run=run_idx + 1, elapsed_s=f"{elapsed:.6f}")
        finally:
            _close_window_safe(window)

    _log_perf(
        "first render summary",
        runs=len(times),
        min_s=f"{min(times):.6f}",
        max_s=f"{max(times):.6f}",
        avg_s=f"{mean(times):.6f}",
        stddev_s=f"{pstdev(times):.6f}",
    )

    assert len(times) == 5
    assert min(times) > 0
    # Keep this loose to avoid machine-specific flakes while still catching regressions.
    assert mean(times) < 2.0


def test_image_gl_creation_skips_tk_image_conversion():
    """
    Ensure image_gl mode does not perform tkinter PhotoImage conversion when
    creating image-backed widgets.
    """
    pil_variants = _create_button_variant_images()

    with patch("nebulatk.image_manager.convert_image") as convert_mock:
        window = ntk.Window(
            title="ImageGL conversion trim test",
            width=320,
            height=180,
            render_mode="image_gl",
            fps=60,
        )
        try:
            _wait_for_renderer(window)
            buttons = _build_image_button_grid(window, pil_variants, rows=2, cols=2)
            _log_perf(
                "image conversion bypass",
                button_count=len(buttons),
                convert_call_count=convert_mock.call_count,
            )
            assert len(buttons) == 4
        finally:
            _close_window_safe(window)

    assert convert_mock.call_count == 0
