import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import nebulatk modules
from nebulatk import _window_internal


@pytest.fixture
def mock_event():
    mock = MagicMock()
    mock.x, mock.y = 100, 100
    mock.char = "a"
    return mock


class TestWindowInternal:

    def test_initialization(self):
        """Test proper initialization of _window_internal class."""
        window = _window_internal(
            width=800,
            height=600,
            title="Test Window",
            canvas_width=800,
            canvas_height=600,
            closing_command=lambda: None,
            resizable=(True, False),
            override=True,
        )

        # Test basic properties
        assert window.width == 800
        assert window.height == 600
        assert window.title == "Test Window"
        assert window.canvas_width == 800
        assert window.canvas_height == 600
        assert window.resizable == (True, False)
        assert window.override is True
        assert window.root is None  # Root isn't initialized until thread starts
        assert window.children == []
        assert window.bounds == {}
        assert window.running is True
        assert callable(window.closing_command)

    @patch("tkinter.Tk")
    def test_create_image(self, mock_tk):
        """Test create_image method."""
        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()
        window.canvas.create_image.return_value = 123

        # Create mock image
        mock_image = MagicMock()
        mock_image.tk_image.return_value = "tk_image_object"

        # Call create_image
        image_id, image_obj = window.create_image(100, 100, mock_image)

        assert image_id == 123
        assert image_obj is mock_image
        window.canvas.create_image.assert_called_once_with(
            100, 100, image="tk_image_object", anchor="nw", state="normal"
        )
        mock_image.tk_image.assert_called_once_with(window)

    @patch("tkinter.Tk")
    @patch("PIL.ImageTk.PhotoImage")
    @patch("nebulatk.image_manager.create_image")
    def test_create_rectangle(self, mock_create_image, mock_photo_image, mock_tk):
        """Test create_rectangle method."""
        # Setup mock for Tk instance
        mock_tk_instance = MagicMock()
        mock_tk.return_value = mock_tk_instance

        # Setup mock for PIL PhotoImage
        mock_photo_instance = MagicMock()
        mock_photo_image.return_value = mock_photo_instance

        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()
        window.canvas.create_rectangle.return_value = 456
        window.root = MagicMock()  # Add mock for root

        # Ensure the fill color doesn't have transparency
        fill_color = "#FF0000ff"  # Fully opaque red

        # Test with opaque fill color
        rect_id, _ = window.create_rectangle(
            10, 10, 110, 60, fill=fill_color, border_width=2, outline="#000000ff"
        )

        assert rect_id == 456
        window.canvas.create_rectangle.assert_called_once_with(
            11.0,
            11.0,
            109.0,
            59.0,
            fill="#FF0000",
            width=2,
            outline="#000000",
            state="normal",
        )

    @patch("tkinter.Tk")
    @patch("PIL.ImageTk.PhotoImage")
    def test_create_rectangle_with_transparency(self, mock_photo_image, mock_tk):
        """Test create_rectangle method with transparent fill."""
        # Setup mock for Tk instance
        mock_tk_instance = MagicMock()
        mock_tk.return_value = mock_tk_instance

        # Setup mock for PIL PhotoImage
        mock_photo_instance = MagicMock()
        mock_photo_image.return_value = mock_photo_instance

        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()
        window.canvas.create_image.return_value = 789
        window.root = MagicMock()  # Add mock for root

        # Test with transparent fill color (RGBA)
        with patch("nebulatk.image_manager.create_image") as mock_create_image:
            mock_bg_image = MagicMock()
            mock_create_image.return_value = mock_bg_image
            mock_bg_image.tk_image.return_value = "transparent_image_object"

            rect_id, image = window.create_rectangle(
                10, 10, 110, 60, fill="#FF000088", border_width=2, outline="#000000"
            )

            assert rect_id == 789
            assert image is mock_bg_image
            mock_create_image.assert_called_once()
            window.canvas.create_image.assert_called_once_with(
                10, 10, image="transparent_image_object", state="normal", anchor="nw"
            )

    @patch("tkinter.Tk")
    def test_create_text(self, mock_tk):
        """Test create_text method."""
        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()
        window.canvas.create_text.return_value = 321

        text_id, _ = window.create_text(
            100,
            50,
            "Test Text",
            font=("Arial", 12),
            fill="blue",
            anchor="center",
            angle=45,
        )

        assert text_id == 321
        window.canvas.create_text.assert_called_once_with(
            100,
            50,
            text="Test Text",
            font=("Arial", 12),
            fill="blue",
            anchor="center",
            state="normal",
            angle=45,
        )

    @patch("tkinter.Tk")
    def test_move_and_object_place(self, mock_tk):
        """Test move and object_place methods."""
        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()
        window.canvas.coords.return_value = [20, 30]  # Original coordinates

        # Test move method
        window.move(123, 50, 25)
        window.canvas.move.assert_called_once_with(123, 50, 25)

        # Reset mock for object_place test
        window.canvas.move.reset_mock()

        # Test object_place method
        window.object_place(123, 100, 80)
        # Should move from current position (20, 30) to target (100, 80)
        window.canvas.move.assert_called_once_with(123, 80, 50)

        # Test with None object
        window.canvas.move.reset_mock()
        window.move(None, 10, 10)
        window.canvas.move.assert_not_called()

    @patch("tkinter.Tk")
    def test_delete_and_change_state(self, mock_tk):
        """Test delete and change_state methods."""
        window = _window_internal(width=800, height=600)
        window.canvas = MagicMock()

        # Test delete method
        window.delete(123)
        window.canvas.delete.assert_called_once_with(123)

        # Test change_state method
        window.change_state(456, "hidden")
        window.canvas.itemconfigure.assert_called_once_with(456, state="hidden")

    @patch("tkinter.Tk")
    def test_place(self, mock_tk):
        """Test place method."""
        window = _window_internal(width=800, height=600)
        window.root = MagicMock()

        window.place(100, 200)
        window.root.geometry.assert_called_once_with("800x600+100+200")

    @patch("tkinter.Tk")
    def test_bind(self, mock_tk):
        """Test bind method."""
        window = _window_internal(width=800, height=600)
        window.root = MagicMock()

        def callback(event):
            pass

        window.bind("<Key>", callback)

        window.root.bind.assert_called_once_with("<Key>", callback)

    @patch("tkinter.Tk")
    @patch("tkinter.Canvas")
    def test_click_and_click_up(self, mock_canvas, mock_tk):
        """Test click and click_up methods."""
        window = _window_internal(width=800, height=600)

        # Create mock event and widget
        mock_event = MagicMock()
        mock_event.x, mock_event.y = 100, 100

        mock_widget = MagicMock()
        mock_widget.clicked = MagicMock()
        mock_widget.release = MagicMock()

        with patch("nebulatk.bounds_manager.check_hit", return_value=True):
            # Add mock widget to children
            window.children = [mock_widget]

            # Test click
            window.click(mock_event)
            assert window.active is mock_widget
            assert window.down is mock_widget
            mock_widget.clicked.assert_called_once()

            # Test click_up
            window.click_up(mock_event)
            assert window.down is None
            mock_widget.release.assert_called_once()

    @patch("tkinter.Tk")
    @patch("tkinter.Canvas")
    def test_hover_and_leave_window(self, mock_canvas, mock_tk, mock_event):
        """Test hover and leave_window methods."""
        window = _window_internal(width=800, height=600)

        # Create mock widgets
        mock_widget = MagicMock()
        mock_widget.hovered = MagicMock()
        mock_widget.hover_end = MagicMock()
        mock_widget.dragging = MagicMock()

        # Add mock widget to children
        window.children = [mock_widget]

        with patch("nebulatk.bounds_manager.check_hit", return_value=True):
            # Test hover
            window.hover(mock_event)
            assert window.hovered is mock_widget
            mock_widget.hovered.assert_called_once()

            # Test leave_window
            window.leave_window(None)
            assert window.hovered is None
            mock_widget.hover_end.assert_called_once()

    @patch("tkinter.Tk")
    def test_typing(self, mock_tk, mock_event):
        """Test typing method."""
        window = _window_internal(width=800, height=600)

        # Create mock active widget
        mock_active = MagicMock()
        mock_active.typed = MagicMock()
        window.active = mock_active

        # Test typing
        window.typing(mock_event)
        mock_active.typed.assert_called_once_with(mock_event)

        # Test typing with no active widget
        mock_active.typed.reset_mock()
        window.active = None
        window.typing(mock_event)
        mock_active.typed.assert_not_called()

    @patch("tkinter.Tk")
    def test_resize(self, mock_tk):
        """Test resize method."""
        window = _window_internal(width=800, height=600)
        window.root = MagicMock()
        window.canvas = MagicMock()
        window._update_children = MagicMock()

        # Test resize with new dimensions
        window.resize(1000, 800)

        assert window.width == 1000
        assert window.height == 800
        window.root.geometry.assert_called_once_with("1000x800")
        window._update_children.assert_called_once()

        # Test resize with default canvas dimensions
        window.canvas_width = "default"
        window.canvas_height = "default"
        window.resize(1200, 900)

        assert window.canvas_width == 1200
        assert window.canvas_height == 900
        window.canvas.configure.assert_any_call(width=1200)
        window.canvas.configure.assert_any_call(height=900)

    @patch("tkinter.Tk")
    def test_show_and_hide(self, mock_tk):
        """Test _show and _hide methods."""
        window = _window_internal(width=800, height=600)
        window.root = MagicMock()
        window.update = MagicMock()

        # Test show method
        window._show(None)
        window.root.deiconify.assert_called_once()
        window.update.assert_called_once()

        # Test hide method
        window._hide(None)
        window.root.withdraw.assert_called_once()

    @patch("tkinter.Tk")
    def test_configure(self, mock_tk):
        """Test configure method."""
        window = _window_internal(width=800, height=600)
        window.root = MagicMock()
        window.resize = MagicMock()

        # Test configure with width and height
        window.configure(width=1000, height=800)
        window.resize.assert_called_once_with(1000, 800)

        # Test configure with title
        window.configure(title="New Title")
        assert window.title == "New Title"
        window.root.title.assert_called_once_with("New Title")

        # Test configure with resizable
        window.configure(resizable=False)
        assert window.resizable == (False, False)
        window.root.resizable.assert_called_once_with(False, False)

        # Test configure with canvas object
        window.canvas = MagicMock()
        obj_id = 123
        window.configure(obj_id, fill="red", width=2)
        window.canvas.itemconfigure.assert_called_once_with(
            obj_id, {"fill": "red", "width": 2}
        )

    @patch("tkinter.Tk")
    def test_close(self, mock_tk):
        """Test close method."""
        mock_closing_command = MagicMock()
        window = _window_internal(
            width=800, height=600, closing_command=mock_closing_command
        )
        window.root = MagicMock()
        window.join = MagicMock()

        window.close()

        assert window.running is False
        window.root.update.assert_called_once()
        window.root.quit.assert_called_once()
        window.join.assert_called_once()
        mock_closing_command.assert_called_once()

        # Test destroy method (it just calls close)
        window.root.reset_mock()
        window.join.reset_mock()
        mock_closing_command.reset_mock()

        window.destroy()
        window.root.update.assert_called_once()
        window.root.quit.assert_called_once()
        window.join.assert_called_once()
        mock_closing_command.assert_called_once()
