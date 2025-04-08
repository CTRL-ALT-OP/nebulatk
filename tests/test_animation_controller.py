import sys
import os
import pytest

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


def test_basic_animation(canvas: ntk.Window) -> None:
    """
    Test animation with a real widget using multiple attributes.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50).place(
        x=0, y=100
    )

    # Test animation with multiple attributes (x, y, and width)
    target_attributes = {"x": 100.0, "y": 50.0, "width": 150.0}

    animation = animation_controller.Animation(
        widget=button, target_attributes=target_attributes, duration=0.1, steps=10
    )
    animation.start()
    animation.join()  # Wait for animation to complete

    # Verify all animated attributes
    for attr, target in target_attributes.items():
        assert (
            getattr(button, attr) == target
        ), f"Attribute {attr} did not reach target value"


def test_invalid_animation(canvas: ntk.Window) -> None:
    """
    Test animation with a real widget using multiple attributes.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50).place(
        x=100, y=0
    )

    # Test animation with invalid attributes (x, y, and width)
    target_attributes = {
        "x": 0.0,
        "y": 50.0,
        "width": "hi",
        "image": 50,
        "not_an_attr": 50,
    }
    actual_attributes = {"x": 0.0, "y": 50.0}

    with pytest.warns(Warning, match="not_an_attr"):
        with pytest.warns(Warning, match="width"):
            with pytest.warns(Warning, match="image"):
                animation = animation_controller.Animation(
                    widget=button,
                    target_attributes=target_attributes,
                    duration=0.1,
                    steps=10,
                )
    animation.start()
    animation.join()  # Wait for animation to complete

    # Verify all animated attributes
    for attr, target in actual_attributes.items():
        assert (
            getattr(button, attr) == target
        ), f"Attribute {attr} did not reach target value"


def test_stop_animation(canvas: ntk.Window) -> None:
    """
    Test stopping an animation.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50).place(
        x=0, y=100
    )

    animation = animation_controller.Animation(
        widget=button, target_attributes={"x": 100.0, "y": 50.0}, duration=0.1, steps=10
    )
    animation.start()
    animation.stop()
    animation.join()
    assert button.x == 0
    assert button.y == 100


def test_easing_functions(canvas: ntk.Window) -> None:
    """
    Test easing functions.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)

    for curve in dir(animation_controller.Curves):
        if curve.startswith("__"):
            continue
        if not callable(getattr(animation_controller.Curves, curve)):
            continue
        button.place(x=0, y=100)
        animation = animation_controller.Animation(
            widget=button,
            target_attributes={"x": 100.0, "y": 50.0},
            duration=0.1,
            steps=10,
            curve=getattr(animation_controller.Curves, curve),
        )
        animation.start()
        animation.join()
        assert button.x == 100
        assert button.y == 50
