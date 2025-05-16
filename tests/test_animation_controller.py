import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import animation controller
import animation_controller
import nebulatk as ntk


def test_place_returns_button():
    """
    Test that place() returns the button itself but does not change the stored x/y properties
    """
    window = ntk.Window(title="Test Window", width=800, height=500)
    try:
        # Create a button and place it
        button = ntk.Button(window, text="Test Button", width=100, height=50)
        returned_button = button.place(x=50, y=75)

        # Verify that place returns the button itself
        assert returned_button is button

        # Verify that the x, y properties are correctly set
        assert button.x == 50
        assert button.y == 75
    finally:
        window.close()


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
    # Create button first, then place it
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=0, y=100)

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
    # Create button first, then place it
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=100, y=0)

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
    # Create button first, then place it
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=0, y=100)

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


def test_animation_group(canvas: ntk.Window) -> None:
    """
    Test animation group.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=0, y=100)
    animation_group = animation_controller.AnimationGroup(
        widget=button,
        keyframes=[
            (0.1, {"x": 100.0, "y": 50.0}, animation_controller.Curves.linear),
            (0.1, {"x": 0.0, "y": 0.0}, animation_controller.Curves.ease_out_quad),
        ],
        steps=10,
    )
    animation_group.start()
    animation_group.join()
    assert button.x == 0
    assert button.y == 0


def test_animation_group_with_animation_instances(canvas: ntk.Window) -> None:
    """
    Test animation group with animation instances.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=0, y=100)
    animation_group = animation_controller.AnimationGroup(
        widget=button,
        keyframes=[
            animation_controller.Animation(
                button, {"x": 100.0, "y": 50.0}, duration=0.1, steps=10
            )
        ],
        steps=10,
    )
    animation_group.start()
    animation_group.join()
    assert button.x == 100
    assert button.y == 50


def test_animation_group_with_invalid_keyframes(canvas: ntk.Window) -> None:
    """
    Test animation group with invalid keyframes.

    Args:
        canvas: Test window fixture
    """
    button = ntk.Button(canvas, text="Test Button", width=100, height=50)
    button.place(x=0, y=100)

    with pytest.warns(Warning, match="2"):
        with pytest.warns(Warning, match="4"):
            with pytest.warns(Warning, match="instance"):
                with pytest.warns(Warning, match="dictionary"):
                    animation_controller.AnimationGroup(
                        widget=button,
                        keyframes=[1, [2], [3, 4, 5, 6, 7, 8]],
                        steps=10,
                    )
