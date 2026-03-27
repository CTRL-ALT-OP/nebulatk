import nebulatk as ntk


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
