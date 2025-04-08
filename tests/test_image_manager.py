import sys
import os
import pytest
from unittest.mock import MagicMock
from PIL import Image as PILImage, ImageTk

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import image_manager module
import image_manager


# Create a small test image
def create_test_image(path, size=(100, 100)):
    img = PILImage.new("RGB", size, color="red")
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


@pytest.fixture
def test_with_distinguish():
    # Create a temporary test image
    original = PILImage.new("RGB", (100, 50), color="red")
    # Add a distinguishing feature to detect flip
    original.putpixel((0, 0), (0, 255, 0))  # green pixel at left corner
    yield original


def test_load_image(test_image_path):
    """Test loading an image."""

    # Test loading a valid image
    image = image_manager.Image(test_image_path)
    assert image.image is not None
    assert isinstance(image.image, PILImage.Image)

    # Test loading with specific dimensions
    mock_widget = MagicMock()
    mock_widget.width = 50
    mock_widget.height = 75
    mock_widget.border_width = 0


def test_load_nonexistent_image():
    """Test loading a non-existent image."""

    # Should return None for non-existent image
    image = image_manager.Image(None)
    assert image.image is None


def test_resize_image(test_image_path):
    """Test resizing an image."""
    # Load original image
    original = PILImage.open(test_image_path)
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
    pil_image = PILImage.new("RGB", (100, 100), color="red")

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
    transparent_img = PILImage.new(
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


def test_load_image_generic():
    """Test loading image without resizing."""
    path = create_test_image("temp_test.png", size=(100, 100))

    # Mock window object
    mock_window = MagicMock()
    mock_window.root = MagicMock()

    # Test without return_both
    tk_image = image_manager.load_image_generic(mock_window, path)
    assert isinstance(tk_image, ImageTk.PhotoImage)

    # Test with return_both
    tk_image, pil_image = image_manager.load_image_generic(
        mock_window, path, return_both=True
    )
    assert isinstance(tk_image, ImageTk.PhotoImage)
    assert isinstance(pil_image, PILImage.Image)
    assert pil_image.width == 100
    assert pil_image.height == 100

    # Clean up
    os.remove("temp_test.png")


def test_image_constructor_with_image_instance(test_image_path):
    """Test creating an Image from another Image instance."""
    original_img = image_manager.Image("test_image.png")
    new_img = image_manager.Image(original_img)

    assert new_img.image is not None
    assert new_img.image == original_img.image


def test_image_constructor_with_object_dimensions():
    """Test resizing an image based on object dimensions."""
    mock_object = MagicMock()
    mock_object.width = 50
    mock_object.height = 75
    mock_object.border_width = 2
    mock_object.master = MagicMock()
    mock_object.master.root = MagicMock()

    # Test with string path
    path = create_test_image("temp_test.png", size=(100, 100))
    img = image_manager.Image(path, mock_object)

    # Check final dimensions after border adjustment (50-2*2, 75-2*2)
    assert img.image.width == 46
    assert img.image.height == 71

    # Clean up
    os.remove("temp_test.png")


def test_flip_horizontal(test_with_distinguish):
    """Test flipping image horizontally."""

    img = image_manager.Image(test_with_distinguish)
    flipped = img.flip("horizontal")

    # After horizontal flip, green pixel should be at the right corner
    assert flipped.image.getpixel((99, 0)) == (0, 255, 0)
    assert flipped.image.getpixel((0, 0)) == (255, 0, 0)  # original corner is now red


def test_flip_vertical(test_with_distinguish):
    """Test flipping image vertically."""

    img = image_manager.Image(test_with_distinguish)
    flipped = img.flip("vertical")

    # After vertical flip, green pixel should be at the bottom-left corner
    assert flipped.image.getpixel((0, 49)) == (0, 255, 0)
    assert flipped.image.getpixel((0, 0)) == (255, 0, 0)  # original corner is now red


def test_rotate(test_with_distinguish):
    """Test rotating image."""
    img = image_manager.Image(test_with_distinguish)
    rotated = img.rotate(90)

    # After 90-degree rotation, dimensions should be swapped
    assert rotated.image.width == 50  # original height
    assert rotated.image.height == 100  # original width

    # Green pixel should now be at bottom-left
    assert rotated.image.getpixel((0, 99)) == (0, 255, 0)


def test_recolor(test_with_distinguish):
    """Test recoloring an image."""
    img = image_manager.Image(test_with_distinguish)
    recolored = img.recolor("#00FF00")  # Change to green

    # Sample multiple pixels to ensure recoloring worked
    pixels = [recolored.image.getpixel((x, y)) for x, y in [(0, 0), (50, 25)]]

    # All pixels should now be green with full opacity
    for pixel in pixels:
        assert pixel == (0, 255, 0, 255)


def test_set_transparency():
    """Test setting transparency of an image."""
    original = PILImage.new(
        "RGBA", (100, 50), color=(255, 0, 0, 255)
    )  # Red with full opacity

    img = image_manager.Image(original)
    transparent = img.set_transparency(128)  # Set transparency to half

    # Sample multiple pixels to ensure transparency was set

    pixels = [transparent.image.getpixel((x, y)) for x, y in [(0, 0), (50, 25)]]

    # All pixels should remain red but with half opacity
    for pixel in pixels:
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0
        assert pixel[3] == 128


def test_increment_transparency():
    """Test incrementing transparency of an image."""
    original = PILImage.new(
        "RGBA", (100, 50), color=(255, 0, 0, 200)
    )  # Red with some opacity

    img = image_manager.Image(original)
    more_transparent = img.increment_transparency(50)  # Decrease opacity by 50

    # Sample multiple pixels to ensure transparency was increased

    pixels = [more_transparent.image.getpixel((x, y)) for x, y in [(0, 0), (50, 25)]]

    # All pixels should remain red but with decreased opacity (200-50=150)
    for pixel in pixels:
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0
        assert pixel[3] == 150


def test_set_relative_transparency_linear():
    """Test setting relative transparency with linear curve."""
    original = PILImage.new(
        "RGBA", (100, 50), color=(255, 0, 0, 200)
    )  # Red with 200 opacity

    img = image_manager.Image(original)
    adjusted = img.set_relative_transparency(
        100, curve="lin"
    )  # Max transparency of 100

    # Linear scaling: new_opacity = 100 * (200 / 255)
    expected_opacity = int(100 * (200 / 255))

    pixels = [adjusted.image.getpixel((x, y)) for x, y in [(0, 0), (50, 25)]]
    for pixel in pixels:
        assert pixel[3] == expected_opacity


def test_set_relative_transparency_exp():
    """Test setting relative transparency with exponential curve."""
    original = PILImage.new(
        "RGBA", (100, 50), color=(255, 0, 0, 200)
    )  # Red with 200 opacity

    img = image_manager.Image(original)
    adjusted = img.set_relative_transparency(100, curve="exp", exponent=2)

    # Exponential scaling with power 2
    expected_opacity = int(((100 ** (1 / 2) / 255 * 200) ** 2))

    pixels = [adjusted.image.getpixel((x, y)) for x, y in [(0, 0), (50, 25)]]
    for pixel in pixels:
        assert pixel[3] == expected_opacity


def test_set_relative_transparency_other_curves():
    """Test setting relative transparency with other curve types."""
    original = PILImage.new("RGBA", (100, 50), color=(255, 0, 0, 200))
    img = image_manager.Image(original)

    # Test all other curves
    curves = ["sqrt", "quad", "cubic", "log"]
    for curve in curves:
        adjusted = img.set_relative_transparency(100, curve=curve)
        assert adjusted.image is not None
        assert isinstance(adjusted.image, PILImage.Image)


def test_tk_image():
    """Test getting tkinter-compatible image."""
    path = create_test_image("temp_test.png", size=(100, 100))

    mock_object = MagicMock()
    mock_object.width = 100
    mock_object.height = 100
    mock_object.border_width = 0
    mock_object.master = MagicMock()
    mock_object.master.root = MagicMock()

    img = image_manager.Image(path, mock_object)

    # First access creates the tk_image
    tk_img = img.tk_image(mock_object)
    assert isinstance(tk_img, ImageTk.PhotoImage)

    # Second access should return the cached image
    second_tk_img = img.tk_image(mock_object)
    assert second_tk_img is tk_img

    # Clean up
    os.remove("temp_test.png")


def test_create_image_function():
    """Test creating an image programmatically."""
    mock_master = MagicMock()
    mock_master.master = MagicMock()
    mock_master.master.root = MagicMock()

    # Test creating an image with fill, border, etc.
    img = image_manager.create_image(
        fill="#FF0000",  # Red fill
        width=100,
        height=50,
        border="#000000",  # Black border
        border_width=2,
        master=mock_master,
    )

    assert isinstance(img, image_manager.Image)
    assert img.image is not None
    assert img.image.width == 100
    assert img.image.height == 50

    # Check border and fill colors by sampling pixels
    center_pixel = img.image.getpixel((50, 25))
    assert center_pixel[:3] == (255, 0, 0)  # Red fill

    border_pixel = img.image.getpixel((1, 1))
    assert border_pixel[:3] == (0, 0, 0)  # Black border
