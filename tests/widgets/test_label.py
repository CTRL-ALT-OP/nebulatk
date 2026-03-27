import nebulatk as ntk


def test_label_properties(canvas: ntk.Window) -> None:
    """Test Label widget properties and functionality."""
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
    assert label.text_color == "#ff0000"
    assert label.fill == "#ffff00ff"


def test_widget_common_operations(canvas: ntk.Window) -> None:
    """Test common widget operations like visibility and destruction."""
    baseline_count = len(canvas.children)
    label = ntk.Label(canvas, text="Test Label").place()
    assert label.visible

    label.hide()
    assert not label.visible

    label.show()
    assert label.visible

    button = ntk.Button(canvas, text="Test Button").place()
    assert len(canvas.children) == baseline_count + 2

    button.destroy()
    assert len(canvas.children) == baseline_count + 1

    label.destroy()
    assert len(canvas.children) == baseline_count
