import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk
from nebulatk import _window_internal
from nebulatk import bounds_manager, standard_methods


@pytest.fixture
def app():
    window = _window_internal(
        title="Container Test",
        width=800,
        height=600,
        render_mode="image_gl",
        fps=30,
    )
    yield window


def test_container_initialization_matches_current_api(app):
    container = ntk.Container(app, width=300, height=200)

    assert container.width == 300
    assert container.height == 200
    assert container.visible is True
    assert container.root == app
    assert container.master == container
    assert container._window == app
    assert container.initialized is True
    assert container.children == []
    assert container.canvas is None
    assert container._image_render_mode is True


def test_container_place_and_parenting(app):
    container = ntk.Container(app, width=300, height=200).place(50, 75)
    assert container.x == 50
    assert container.y == 75
    assert container in app.children


def test_child_widget_parenting_inside_container(app):
    container = ntk.Container(app, width=300, height=200).place(50, 50)

    button = ntk.Button(container, text="Container Button", width=100, height=30).place(10, 10)
    label = ntk.Label(container, text="Container Label", width=100, height=30).place(10, 50)

    assert button.master == container
    assert label.master == container
    assert button in container.children
    assert label in container.children
    assert button not in app.children
    assert label not in app.children


def test_hit_detection_with_container_children(app):
    container = ntk.Container(app, width=300, height=200).place(50, 50)
    ntk.Button(container, text="Hit Test", width=100, height=30).place(10, 10)

    # Nested widgets are currently hit-tested using their own coordinates.
    hit = app._find_deepest_hit(app.children, 70, 70)
    miss = app._find_deepest_hit(app.children, 5, 5)
    assert hit is container
    assert miss is None


def test_position_conversion_with_container_children(app):
    container = ntk.Container(app, width=300, height=200).place(50, 50)
    button = ntk.Button(container, text="Position Test", width=100, height=30).place(10, 10)

    points = standard_methods.get_rect_points(button)
    assert len(points) == 4
    assert points[0] == (10, 10)

    abs_pos = standard_methods.rel_position_to_abs(button, 20, 30)
    rel_pos = standard_methods.abs_position_to_rel(button, abs_pos[0], abs_pos[1])
    assert abs_pos == (20, 30)
    assert rel_pos == (20, 30)


def test_container_event_handling_routes_to_child(app):
    container = ntk.Container(app, width=300, height=200).place(50, 50)
    button = ntk.Button(container, text="Event Test", width=100, height=30).place(10, 10)

    event = MagicMock()
    event.x = 20
    event.y = 20
    event.char = "a"

    container.click(event)
    assert container.active is button
    assert container.down is button

    container.hover(event)
    container.typing(event)

