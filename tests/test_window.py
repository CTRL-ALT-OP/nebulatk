import sys
import os
import time
from types import SimpleNamespace
import pytest
from PIL import Image as PILImage

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Now import your package/module
import nebulatk as ntk
import rendering


def _wait_for_frame(window: ntk.Window, timeout_s: float = 1.0):
    deadline = time.time() + timeout_s
    frame = None
    while frame is None and time.time() < deadline:
        frame = window.renderer.render_if_due()
        if frame is None:
            time.sleep(window.renderer.frame_interval)
    return frame if frame is not None else window.renderer.last_frame


@pytest.fixture
def window() -> ntk.Window:
    """
    Create a test window for window testing.

    Returns:
        ntk.Window: A window instance for testing.
    """
    window = ntk.Window(title="Test Window", width=800, height=500, render_mode="image_gl", fps=30)
    yield window
    window.close()


@pytest.fixture
def image_gl_window() -> ntk.Window:
    """Create a test window using the image/OpenGL render mode."""
    window = ntk.Window(title="ImageGL Test Window", width=320, height=240, render_mode="image_gl", fps=30)
    yield window
    window.close()


def test_window_defaults() -> None:
    """
    Test default properties of the Window class.

    Args:
        window: The test window fixture.
    """
    # Test default values when not specified
    default_window = ntk.Window()
    assert default_window.width == 500
    assert default_window.height == 500
    assert default_window.title == "ntk"
    default_window.close()


def test_window_custom_properties(window: ntk.Window) -> None:
    """
    Test custom properties of the Window class.

    Args:
        window: The test window fixture.
    """
    # Test custom values
    assert window.width == 800
    assert window.height == 500
    assert window.title == "Test Window"


def test_window_image_gl_initialization(image_gl_window: ntk.Window) -> None:
    """Test image_gl mode initializes renderer/display correctly."""
    timeout_at = time.time() + 1.0
    while image_gl_window.renderer is None and time.time() < timeout_at:
        time.sleep(0.01)

    assert image_gl_window.render_mode == "image_gl"
    assert image_gl_window.renderer is not None
    assert image_gl_window.display is not None
    assert image_gl_window.renderer.width == 320
    assert image_gl_window.renderer.height == 240


def test_window_image_gl_render_cycle(image_gl_window: ntk.Window) -> None:
    """Test that dirty updates produce a rendered frame in image_gl mode."""
    timeout_at = time.time() + 1.0
    while image_gl_window.renderer is None and time.time() < timeout_at:
        time.sleep(0.01)

    widget = ntk.Frame(image_gl_window, width=90, height=70, fill="#e31234ff").place(10, 10)
    assert widget in image_gl_window.children

    frame = _wait_for_frame(image_gl_window)
    assert frame is not None
    assert frame.size == (image_gl_window.width, image_gl_window.height)

    inside = frame.getpixel((20, 20))
    outside = frame.getpixel((150, 150))
    assert inside[0] > 200
    assert inside[1] < 80
    assert inside[2] < 100
    assert inside[3] > 0
    assert outside != inside


def test_window_image_gl_resize_updates_renderer(image_gl_window: ntk.Window) -> None:
    """Test resizing updates renderer dimensions in image_gl mode."""
    image_gl_window.resize(410, 290)
    assert image_gl_window.renderer.width == 410
    assert image_gl_window.renderer.height == 290
    assert image_gl_window.canvas_width == 410
    assert image_gl_window.canvas_height == 290


def test_final_composited_frame_bytes_match_expected_pixels(monkeypatch) -> None:
    class RootProxy:
        def __init__(self):
            self.submissions = []

        def submit_frame(self, frame_rgba, width, height):
            self.submissions.append((frame_rgba, width, height))

    class Container:
        pass

    def make_widget(x, y, width, height, fill, visible=True):
        return SimpleNamespace(
            x=x,
            y=y,
            width=width,
            height=height,
            fill=fill,
            visible=visible,
            _render_visible=True,
            border_width=0,
            border=None,
            text="",
            font=None,
            children=[],
        )

    container = Container()
    container.x = 2
    container.y = 2
    container.width = 10
    container.height = 10
    container.fill = None
    container.visible = True
    container._render_visible = True
    container.border_width = 0
    container.border = None
    container.text = ""
    container.font = None
    container.children = [make_widget(-4, 1, 8, 8, "#ff0000ff")]

    background = make_widget(0, 0, 20, 20, "#0000ffff")
    renderer = rendering.PILImageRenderer(
        window=SimpleNamespace(children=[container, background]),
        width=20,
        height=20,
        fps=1,
    )

    now = [70.0]
    monkeypatch.setattr(rendering.time, "time", lambda: now[0])
    renderer._last_render = 0.0
    renderer._redraw_requested = True
    frame = renderer.render_if_due()
    assert frame is not None

    proxy = RootProxy()
    display = rendering.OpenGLImageDisplay(proxy, width=20, height=20)
    display.show_frame(frame)

    assert len(proxy.submissions) == 1
    frame_rgba, width, height = proxy.submissions[0]
    assert (width, height) == (20, 20)

    submitted = PILImage.frombytes("RGBA", (width, height), frame_rgba, "raw", "RGBA")
    assert submitted.getpixel((3, 4)) == (255, 0, 0, 255)
    assert submitted.getpixel((7, 4)) == (0, 0, 255, 255)
    assert submitted.getpixel((1, 4)) == (0, 0, 255, 255)
