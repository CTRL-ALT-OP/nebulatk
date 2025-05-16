import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import the colors_manager module
import colors_manager


def test_color_name_to_hex():
    """Test converting color names to hex values."""
    assert colors_manager.convert_to_hex("red1") == "#ff0000ff"
    assert colors_manager.convert_to_hex("blue") == "#0000ffff"
    assert colors_manager.convert_to_hex("green") == "#008000ff"
    assert colors_manager.convert_to_hex("yellow1") == "#ffff00ff"
    assert colors_manager.convert_to_hex("black") == "#000000ff"
    assert colors_manager.convert_to_hex("white") == "#ffffffff"


def test_color_name_to_hex_with_fallback():
    """Test handling of invalid color names."""
    # Test with invalid color name, should return the input if it looks like a hex value
    assert colors_manager.convert_to_hex("#12AB34") == "#12AB34"
    # Test with completely invalid input, should return default (black)
    with pytest.raises(KeyError):
        colors_manager.convert_to_hex("not_a_color")


def test_rgb_to_hex():
    """Test converting RGB tuples to hex values."""
    assert colors_manager.convert_to_hex((255, 0, 0)) == "#ff0000ff"
    assert colors_manager.convert_to_hex((0, 255, 0)) == "#00ff00ff"
    assert colors_manager.convert_to_hex((0, 0, 255)) == "#0000ffff"
    assert colors_manager.convert_to_hex((128, 128, 128)) == "#808080ff"
    assert colors_manager.convert_to_hex((0, 0, 0)) == "#000000ff"
    assert colors_manager.convert_to_hex((255, 255, 255)) == "#ffffffff"


def test_hex_to_rgb():
    """Test converting hex values to RGB tuples."""
    assert colors_manager.convert_to_rgb("#FF0000") == (255, 0, 0, 255)
    assert colors_manager.convert_to_rgb("#00FF00") == (0, 255, 0, 255)
    assert colors_manager.convert_to_rgb("#0000FF") == (0, 0, 255, 255)
    assert colors_manager.convert_to_rgb("#808080aa") == (128, 128, 128, 170)
    assert colors_manager.convert_to_rgb("#000000") == (0, 0, 0, 255)
    assert colors_manager.convert_to_rgb("#FFFFFF") == (255, 255, 255, 255)

    # Test with lowercase hex and without '#'
    assert colors_manager.convert_to_rgb("ff0000") == (255, 0, 0, 255)
    assert colors_manager.convert_to_rgb("00ff00") == (0, 255, 0, 255)


def test_darken_color():
    """Test darkening colors."""
    # Test darkening red by 5
    assert colors_manager.Color("#FF0000").darken(5).color == "#fa0000ff"
    # Test darkening black (should remain black)
    assert colors_manager.Color("#000000").darken(5).color == "#000000ff"


def test_brighten_color():
    """Test brightening colors."""
    # Test brightening red by 5
    assert colors_manager.Color("#FF0000").brighten(5).color == "#ff0505ff"
    # Test brightening white (should remain white)
    assert colors_manager.Color("#FFFFFF").brighten(5).color == "#ffffffff"
