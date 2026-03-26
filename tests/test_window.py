import sys
import os
import time
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Now import your package/module
import nebulatk as ntk


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

    rect_id, _ = image_gl_window.create_rectangle(
        10,
        10,
        100,
        80,
        fill="#ff0000ff",
        border_width=0,
        outline="#ff0000ff",
    )
    assert rect_id is not None
    assert image_gl_window.renderer.needs_redraw() is True

    frame = image_gl_window.renderer.render_if_due()
    assert frame is not None
    assert frame.size == (image_gl_window.width, image_gl_window.height)


def test_window_image_gl_resize_updates_renderer(image_gl_window: ntk.Window) -> None:
    """Test resizing updates renderer dimensions in image_gl mode."""
    image_gl_window.resize(410, 290)
    assert image_gl_window.renderer.width == 410
    assert image_gl_window.renderer.height == 290
    assert image_gl_window.renderer.root_surface.width == 410
    assert image_gl_window.renderer.root_surface.height == 290
