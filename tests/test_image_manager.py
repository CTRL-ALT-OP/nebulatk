from typing import Any, List, Optional, TYPE_CHECKING
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image, ImageTk

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import image_manager module
import image_manager


# Create a small test image
def create_test_image(path, size=(100, 100)):
    img = Image.new("RGB", size, color="red")
    img.save(path)
    return path


@pytest.fixture
def test_image_path():
    # Create a temporary test image
    path = "test_image.png"
    create_test_image(path)
    yield path
    # Clean up
    if os.path.exists(path):
        os.remove(path)


def test_load_image(test_image_path):
    """Test loading an image."""

    # Test loading a valid image
    image = image_manager.Image(test_image_path)
    assert image.image is not None
    assert isinstance(image.image, Image.Image)

    # Test loading with specific dimensions
    mock_widget = MagicMock()
    mock_widget.width = 50
    mock_widget.height = 75
    mock_widget.border_width = 0
    resized_image = image_manager.Image(test_image_path, mock_widget)
    assert resized_image is not None
    assert resized_image.image.width == 50
    assert resized_image.image.height == 75
    assert resized_image.tk_image is not None


def test_load_nonexistent_image():
    """Test loading a non-existent image."""

    # Should return None for non-existent image
    image = image_manager.Image(None)
    assert image.image is None


def test_resize_image(test_image_path):
    """Test resizing an image."""
    # Load original image
    original = Image.open(test_image_path)
    assert original.width == 100
    assert original.height == 100

    img = image_manager.Image(original)
    # Resize the image
    resized = img.resize(width=50, height=75)
    assert resized.image.width == 50
    assert resized.image.height == 75


def test_convert_to_photoimage():
    """Test converting PIL Image to PhotoImage."""
    img_mgr = image_manager

    # Create a test PIL Image
    pil_image = Image.new("RGB", (100, 100), color="red")

    # Convert to PhotoImage
    photoimage = img_mgr.convert_image(MagicMock(), pil_image)

    assert photoimage is not None
    assert isinstance(photoimage, ImageTk.PhotoImage)
    assert photoimage.width() == 100
    assert photoimage.height() == 100


def test_image_manager_with_transparency():
    """Test handling images with transparency."""
    img_mgr = image_manager

    # Create a test image with transparency
    transparent_path = "transparent_image.png"
    transparent_img = Image.new(
        "RGBA", (100, 100), color=(255, 0, 0, 128)
    )  # Semi-transparent red
    transparent_img.save(transparent_path)

    # Load the transparent image
    image = img_mgr.load_image(MagicMock(), transparent_path)
    assert image is not None
    assert isinstance(image, ImageTk.PhotoImage)

    # Clean up
    if os.path.exists(transparent_path):
        os.remove(transparent_path)
