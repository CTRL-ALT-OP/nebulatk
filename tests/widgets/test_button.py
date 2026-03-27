from unittest.mock import MagicMock, patch

import nebulatk as ntk


def test_button_properties(canvas: ntk.Window) -> None:
    """Test Button widget properties and functionality."""
    button = ntk.Button(
        canvas,
        text="Test Button",
        width=100,
        height=30,
        fill="blue",
        text_color="white",
    ).place()

    assert button.text == "Test Button"
    assert button.width == 100
    assert button.height == 30
    assert button.fill == "#0000ffff"
    assert button.text_color == "#ffffff"

    assert not button.state
    button.state = True
    assert button.state


def test_image_button_functionality(canvas: ntk.Window) -> None:
    """Test image-backed button behavior."""
    with patch("nebulatk.image_manager.load_image", return_value=MagicMock()):
        image_button = ntk.Button(
            canvas,
            image="nebulatk/examples/Images/main_button_inactive.png",
            width=100,
            height=50,
        ).place()

        assert image_button.width == 100
        assert image_button.height == 50
        assert not image_button.state

        image_button.state = True
        assert image_button.state
        image_button.state = False
        assert not image_button.state
