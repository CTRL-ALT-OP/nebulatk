import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Now import your package/module
import nebulatk as ntk


@pytest.fixture
def canvas() -> ntk.Window:
    """
    Create a test window for widget testing.

    Returns:
        ntk.Window: A window instance for testing widgets.
    """
    window = ntk.Window(title="Test Window", width=800, height=500)
    yield window
    window.close()


def test_children(canvas: ntk.Window) -> None:
    """
    Test widget children management in the window.

    Args:
        canvas: The test window fixture.
    """
    button = ntk.Button(canvas, text="Button").place()
    assert len(canvas.children) == 1
    button.destroy()
    assert len(canvas.children) == 0


def test_button_properties(canvas: ntk.Window) -> None:
    """
    Test Button widget properties and functionality.

    Args:
        canvas: The test window fixture.
    """
    # Test button creation with various properties
    button = ntk.Button(
        canvas,
        text="Test Button",
        width=100,
        height=30,
        fill="blue",
        text_color="white",
    ).place()

    assert button.text == "Test Button"
    assert button.width == 100
    assert button.height == 30
    assert button.fill == "#0000FF"
    assert button.text_color == "#FFFFFF"

    # Test button state changes
    assert not button.state  # Default state should be False
    button.state = True
    assert button.state


def test_label_properties(canvas: ntk.Window) -> None:
    """
    Test Label widget properties and functionality.

    Args:
        canvas: The test window fixture.
    """
    label = ntk.Label(
        canvas,
        text="Test Label",
        width=150,
        height=40,
        text_color="red1",
        fill="yellow1",
    ).place()

    assert label.text == "Test Label"
    assert label.width == 150
    assert label.height == 40
    assert label.text_color == "#FF0000"
    assert label.fill == "#FFFF00"


def test_slider_functionality(canvas: ntk.Window) -> None:
    """
    Test Slider widget functionality.

    Args:
        canvas: The test window fixture.
    """
    slider = ntk.Slider(
        canvas, width=200, height=30, slider_width=20, slider_height=30
    ).place()

    # Test initial position
    initial_x = slider.button.x

    # Simulate dragging by calling the internal _dragging method
    slider._dragging(initial_x + 50, slider.button.y)

    # Button should have moved
    assert slider.button.x > initial_x

    # Test clamping at boundaries
    # Drag beyond right edge
    slider._dragging(slider.width + 100, slider.button.y)
    assert slider.button.x <= slider.width - slider.button.width

    # Drag beyond left edge
    slider._dragging(-100, slider.button.y)
    assert slider.button.x >= 0
