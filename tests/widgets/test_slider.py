import nebulatk as ntk
import pytest


def test_slider_functionality(canvas: ntk.Window) -> None:
    """Test Slider widget functionality."""
    slider = ntk.Slider(
        canvas, width=200, height=30, slider_width=20, slider_height=30
    ).place()

    initial_x = slider.button.x

    slider._dragging(initial_x + 50, slider.button.y)
    assert slider.button.x > initial_x

    slider._dragging(slider.width + 100, slider.button.y)
    assert slider.button.x <= slider.width - slider.button.width

    slider._dragging(-100, slider.button.y)
    assert slider.button.x >= 0


def test_vertical_slider_dragging(canvas: ntk.Window) -> None:
    """Test vertical Slider movement and clamping."""
    slider = ntk.Slider(
        canvas,
        width=30,
        height=200,
        slider_width=30,
        slider_height=20,
        direction="vertical",
    ).place()

    initial_y = slider.button.y
    slider._dragging(slider.button.x, initial_y + 80)
    assert slider.button.y > initial_y

    slider._dragging(slider.button.x, slider.height + 100)
    assert slider.button.y <= slider.height - slider.button.height

    slider._dragging(slider.button.x, -100)
    assert slider.button.y >= 0


def test_scrollbar_alias_and_direction_validation(canvas: ntk.Window) -> None:
    """Test Scrollbar alias and invalid direction handling."""
    scrollbar = ntk.Scrollbar(canvas, direction="vertical").place()
    assert scrollbar.direction == "vertical"

    with pytest.raises(ValueError):
        ntk.Scrollbar(canvas, direction="diagonal")
