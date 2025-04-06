from typing import Any, List, Optional, TYPE_CHECKING
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

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


def test_entry_functionality(canvas: ntk.Window) -> None:
    """
    Test entry widget properties and functionality.

    Args:
        canvas: The test window fixture.
    """
    # Test entry creation
    entry = ntk.Entry(
        canvas,
        text="Initial text",
        width=200,
        height=40,
        text_color="blue",
        fill="white",
    ).place()

    assert entry.text == "Initial text"
    assert entry.width == 200
    assert entry.height == 40
    assert entry.text_color == "#0000FF"
    assert entry.fill == "#FFFFFF"

    # Test changing text
    for _ in range(len("Initial text")):
        entry.typed("\x08")
    assert entry.text == ""
    for char in "Updated text":
        entry.typed(char)
    assert entry.get() == "Updated text"


def test_image_button_functionality(canvas: ntk.Window) -> None:
    """
    Test ImageButton widget properties and functionality.

    Args:
        canvas: The test window fixture.
    """
    # Mock the image loading functionality
    with patch("nebulatk.image_manager.load_image", return_value=MagicMock()):
        # Test image button creation
        image_button = ntk.Button(
            canvas,
            image="nebulatk/examples/Images/main_button_inactive.png",
            width=100,
            height=50,
        ).place()

        assert image_button.width == 100
        assert image_button.height == 50
        assert not image_button.state  # Default state is False

        # Test button state changes
        image_button.state = True
        assert image_button.state
        image_button.state = False
        assert not image_button.state


def test_widget_visibility(canvas: ntk.Window) -> None:
    """
    Test widget visibility functionality.

    Args:
        canvas: The test window fixture.
    """
    label = ntk.Label(canvas, text="Test Label").place()
    assert label.visible  # Should be visible by default

    # Hide the label
    label.hide()
    assert not label.visible

    # Show the label
    label.show()
    assert label.visible


def test_widget_destroy(canvas: ntk.Window) -> None:
    """
    Test widget destruction functionality.

    Args:
        canvas: The test window fixture.
    """
    button = ntk.Button(canvas, text="Test Button").place()
    assert len(canvas.children) == 1

    button.destroy()
    assert len(canvas.children) == 0
