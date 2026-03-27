import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import animation controller
import animation_controller
from types import SimpleNamespace


class DummyWidget:
    def __init__(self, x=0.0, y=100.0, width=100.0, height=50.0):
        self.master = SimpleNamespace(active_animations=[])
        self._position = [x, y]
        self._size = [width, height]
        self.place_calls = 0
        self.update_calls = 0

    @property
    def x(self):
        return self._position[0]

    @x.setter
    def x(self, value):
        self._position[0] = value

    @property
    def y(self):
        return self._position[1]

    @y.setter
    def y(self, value):
        self._position[1] = value

    @property
    def width(self):
        return self._size[0]

    @width.setter
    def width(self, value):
        self._size[0] = value

    @property
    def height(self):
        return self._size[1]

    @height.setter
    def height(self, value):
        self._size[1] = value

    def place(self, x, y):
        self._position = [x, y]
        self.place_calls += 1
        return self

    def update(self):
        self.update_calls += 1
        return self


@pytest.fixture
def widget():
    return DummyWidget()


def test_basic_animation(widget) -> None:
    """
    Test animation with a real widget using multiple attributes.

    Args:
        canvas: Test window fixture
    """
    # Test animation with multiple attributes (x, y, and width)
    target_attributes = {"x": 100.0, "y": 50.0, "width": 150.0}
    animation = animation_controller.Animation(
        widget=widget, target_attributes=target_attributes, duration=0.1, steps=10
    )
    animation.start()
    animation.join(timeout=1)  # Wait for animation to complete
    # Verify all animated attributes
    for attr, target in target_attributes.items():
        assert (
            getattr(widget, attr) == target
        ), f"Attribute {attr} did not reach target value"


def test_invalid_animation(widget) -> None:
    """
    Test animation with a real widget using multiple attributes.

    Args:
        canvas: Test window fixture
    """
    widget.place(x=100, y=0)

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
                    widget=widget,
                    target_attributes=target_attributes,
                    duration=0.1,
                    steps=10,
                )
    animation.start()
    animation.join(timeout=1)  # Wait for animation to complete

    # Verify all animated attributes
    for attr, target in actual_attributes.items():
        assert (
            getattr(widget, attr) == target
        ), f"Attribute {attr} did not reach target value"


def test_stop_animation(widget) -> None:
    """
    Test stopping an animation.

    Args:
        canvas: Test window fixture
    """
    animation = animation_controller.Animation(
        widget=widget, target_attributes={"x": 100.0, "y": 50.0}, duration=0.1, steps=10
    )
    animation.start()
    animation.stop()
    animation.join(timeout=1)
    assert widget.x == 0
    assert widget.y == 100


def test_easing_functions(widget) -> None:
    """
    Test easing functions.

    Args:
        canvas: Test window fixture
    """
    for curve in dir(animation_controller.Curves):
        if curve.startswith("__"):
            continue
        if not callable(getattr(animation_controller.Curves, curve)):
            continue
        widget.place(x=0, y=100)
        animation = animation_controller.Animation(
            widget=widget,
            target_attributes={"x": 100.0, "y": 50.0},
            duration=0.1,
            steps=10,
            curve=getattr(animation_controller.Curves, curve),
        )
        animation.start()
        animation.join(timeout=1)
        assert widget.x == 100
        assert widget.y == 50


def test_animation_group(widget) -> None:
    """
    Test animation group.

    Args:
        canvas: Test window fixture
    """
    widget.place(x=0, y=100)
    animation_group = animation_controller.AnimationGroup(
        widget=widget,
        keyframes=[
            (0.1, {"x": 100.0, "y": 50.0}, animation_controller.Curves.linear),
            (0.1, {"x": 0.0, "y": 0.0}, animation_controller.Curves.ease_out_quad),
        ],
        steps=10,
    )
    animation_group.start()
    animation_group.join(timeout=1)
    assert widget.x == 0
    assert widget.y == 0


def test_animation_group_with_animation_instances(widget) -> None:
    """
    Test animation group with animation instances.

    Args:
        canvas: Test window fixture
    """
    widget.place(x=0, y=100)
    animation_group = animation_controller.AnimationGroup(
        widget=widget,
        keyframes=[
            animation_controller.Animation(
                widget, {"x": 100.0, "y": 50.0}, duration=0.1, steps=10
            )
        ],
        steps=10,
    )
    animation_group.start()
    animation_group.join(timeout=1)
    assert widget.x == 100
    assert widget.y == 50


def test_animation_group_with_invalid_keyframes(widget) -> None:
    """
    Test animation group with invalid keyframes.

    Args:
        canvas: Test window fixture
    """
    widget.place(x=0, y=100)

    with pytest.warns(Warning, match="2"):
        with pytest.warns(Warning, match="4"):
            with pytest.warns(Warning, match="instance"):
                with pytest.warns(Warning, match="dictionary"):
                    animation_controller.AnimationGroup(
                        widget=widget,
                        keyframes=[1, [2], [3, 4, 5, 6, 7, 8]],
                        steps=10,
                    )


def test_animation_group_stop_is_idempotent():
    class DummyMaster:
        def __init__(self):
            self.active_animations = []

    class DummyWidget:
        def __init__(self):
            self.master = DummyMaster()

    group = animation_controller.AnimationGroup(widget=DummyWidget(), keyframes=[], steps=10)
    # Stopping before start should not raise.
    group.stop()
    group.widget.master.active_animations.append(group)
    # Stopping repeatedly should not raise and should clean up membership.
    group.stop()
    group.stop()
    assert group not in group.widget.master.active_animations
