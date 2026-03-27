import nebulatk as ntk


def test_children(canvas: ntk.Window) -> None:
    """Test widget children management in the window."""
    baseline_count = len(canvas.children)
    button = ntk.Button(canvas, text="Button").place()
    assert len(canvas.children) == baseline_count + 1
    button.destroy()
    assert len(canvas.children) == baseline_count
