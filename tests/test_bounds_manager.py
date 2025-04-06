from typing import Any, List, Optional, TYPE_CHECKING
import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import bounds_manager module
import bounds_manager
import image_manager
import nebulatk as ntk


def test_bounds_transparency():
    test_image = image_manager.create_image(
        fill="#000000",
        width=5,
        height=5,
        border="#00000000",
        border_width=1,
        master=None,
    )
    """Test bounds calculation across different scenarios."""
    # Test bounds with fixed width/height
    bounds = bounds_manager.generate_bounds_for_nonstandard_image(test_image.image)
    assert bounds == {1: [[1, 3]], 2: [[1, 3]], 3: [[1, 3]]}


def test_bounds_custom_tolerance():

    test_image = image_manager.create_image(
        fill="#000000",
        width=5,
        height=5,
        border="#000000aa",
        border_width=1,
        master=None,
    )
    """Test bounds calculation across different scenarios."""
    # Test bounds with fixed width/height
    bounds = bounds_manager.generate_bounds_for_nonstandard_image(
        test_image.image, tolerance=0.2
    )
    assert bounds == {
        0: [[0, 4]],
        1: [[0, 4]],
        2: [[0, 4]],
        3: [[0, 4]],
        4: [[0, 4]],
    }


def test_bounds_fallback():

    test_image = image_manager.create_image(
        fill="#000000aa",
        width=5,
        height=5,
        border="#000000aa",
        border_width=1,
        master=None,
    )
    """Test bounds calculation across different scenarios."""
    # Test bounds with fixed width/height
    bounds = bounds_manager.generate_bounds_for_nonstandard_image(
        test_image.image, tolerance=0.2
    )
    assert bounds == {
        0: [[0, 4]],
        1: [[0, 4]],
        2: [[0, 4]],
        3: [[0, 4]],
        4: [[0, 4]],
    }


def test_hit_bounds():
    """Test hit_bounds function."""
    window = ntk.Window()
    label = ntk.Label(window, text="hi", width=10, height=10).place()

    assert bounds_manager.check_hit(label, 1, 1) == True
    assert bounds_manager.check_hit(label, 11, 11) == False
    window.close()


def test_hit_custom():
    """Test hit_bounds function."""
    test_image = image_manager.create_image(
        fill="#000000",
        width=5,
        height=5,
        border="#000000aa",
        border_width=1,
        master=None,
    )
    window = ntk.Window()
    label = ntk.Button(window, image=test_image, width=5, height=5).place()

    assert bounds_manager.check_hit(label, 0, 0) == False
    assert bounds_manager.check_hit(label, 2, 2) == True
    window.close()
