import sys
import os
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
    window = ntk.Window(title="Test Window", width=800, height=500)
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


def test_window_position(window: ntk.Window) -> None:
    """
    Test window position functionality.

    Args:
        window: The test window fixture.
    """
    # Test setting position
    new_x = 100
    new_y = 200
    window.place(new_x, new_y)
    assert window.root.geometry() == f"800x500+{new_x}+{new_y}"


def test_window_title_change(window: ntk.Window) -> None:
    """
    Test window title change functionality.

    Args:
        window: The test window fixture.
    """
    # Test changing title
    new_title = "New Test Title"
    window.title = new_title
    assert window.title == new_title
