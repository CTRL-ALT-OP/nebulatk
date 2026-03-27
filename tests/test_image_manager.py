import os
import sys
from unittest.mock import MagicMock

import pytest
from PIL import Image as PILImage

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import image_manager


def create_test_image(path, size=(100, 100)):
    img = PILImage.new("RGB", size, color="red")
    img.save(path)
    return path


@pytest.fixture
def test_image_path(tmp_path):
    path = tmp_path / "test_image.png"
    create_test_image(path)
    yield str(path)


def test_load_image(test_image_path):
    image = image_manager.Image(test_image_path)
    assert image.image is not None
    assert isinstance(image.image, PILImage.Image)


def test_load_nonexistent_image():
    image = image_manager.Image(None)
    assert image.image is None


def test_resize_image(test_image_path):
    original = PILImage.open(test_image_path)
    img = image_manager.Image(original)
    resized = img.resize(width=50, height=75)
    assert resized.image.size == (50, 75)


def test_convert_image_returns_pil():
    pil_image = PILImage.new("RGB", (100, 100), color="red")
    converted = image_manager.convert_image(MagicMock(), pil_image)
    assert converted is pil_image
    assert isinstance(converted, PILImage.Image)


def test_load_image_generic_returns_none_for_image_gl(test_image_path):
    mock_window = MagicMock()
    mock_window.render_mode = "image_gl"
    mock_window.master = None

    converted = image_manager.load_image_generic(mock_window, test_image_path)
    assert converted is None

    converted, pil_image = image_manager.load_image_generic(
        mock_window, test_image_path, return_both=True
    )
    assert converted is None
    assert isinstance(pil_image, PILImage.Image)
    pil_image.close()


def test_image_constructor_with_object_dimensions():
    mock_object = MagicMock()
    mock_object.width = 50
    mock_object.height = 75
    mock_object.border_width = 2
    mock_object.master = MagicMock()
    mock_object.master.render_mode = "image_gl"

    path = create_test_image("temp_test.png", size=(100, 100))
    img = image_manager.Image(path, mock_object)
    assert img.image.size == (46, 71)
    os.remove("temp_test.png")


def test_flip_rotate_and_transparency_ops():
    original = PILImage.new("RGBA", (100, 50), color=(255, 0, 0, 200))
    original.putpixel((0, 0), (0, 255, 0, 200))

    img = image_manager.Image(original.copy())
    flipped_h = img.flip("horizontal")
    assert flipped_h.image.getpixel((99, 0))[:3] == (0, 255, 0)

    img = image_manager.Image(original.copy())
    flipped_v = img.flip("vertical")
    assert flipped_v.image.getpixel((0, 49))[:3] == (0, 255, 0)

    img = image_manager.Image(original.copy())
    rotated = img.rotate(90)
    assert rotated.image.size == (50, 100)

    img = image_manager.Image(original.copy())
    recolored = img.recolor("#00FF00")
    assert recolored.image.getpixel((20, 20))[:3] == (0, 255, 0)

    img = image_manager.Image(original.copy())
    transparent = img.set_transparency(128)
    assert transparent.image.getpixel((20, 20))[3] == 128

    img = image_manager.Image(original.copy())
    decreased = img.increment_transparency(50)
    assert decreased.image.getpixel((20, 20))[3] == 150

