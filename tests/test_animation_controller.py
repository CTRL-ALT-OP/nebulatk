from typing import Any, List, Optional, TYPE_CHECKING
import sys
import os
import pytest
import time
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import animation controller
import animation_controller
import nebulatk as ntk


@pytest.fixture
def canvas() -> ntk.Window:
    """
    Create a test window for animation testing.

    Returns:
        ntk.Window: A window instance for testing animations.
    """
    window = ntk.Window(title="Test Window", width=800, height=500)
    yield window
    window.close()


def test_animation_with_real_widget(canvas):
    """Test animation with a real widget."""
    button = ntk.Button(canvas, text="Test Button", width=100, height=50).place(
        x=0, y=100
    )

    animation_controller.animate(
        widget=button,
        target_x=100,
        target_y=50,
    )

    assert button.x == 100
    assert button.y == 50
