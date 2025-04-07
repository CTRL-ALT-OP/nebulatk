import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import nebulatk
import nebulatk as ntk


class TestFileDialog:
    """Tests for FileDialog functionality."""

    @pytest.fixture
    def app(self):
        """Create a test application window."""
        window = ntk.Window(title="File Dialog Test", width=800, height=600)
        yield window
        window.close()

    @patch("tkinter.filedialog.askopenfile")
    def test_file_dialog_basic(self, mock_askopenfile, app):
        """Test basic file dialog functionality."""
        # Mock file object
        mock_file = MagicMock()
        mock_askopenfile.return_value = mock_file

        # Call FileDialog
        result = ntk.FileDialog(app)

        # Check that the dialog was opened with default parameters
        mock_askopenfile.assert_called_once_with(
            initialdir=None, mode="r", filetypes=(("All files", "*"))
        )

        # Check that the result is the mocked file
        assert result == mock_file

    @patch("tkinter.filedialog.askopenfile")
    def test_file_dialog_custom_params(self, mock_askopenfile, app):
        """Test file dialog with custom parameters."""
        # Mock file object
        mock_file = MagicMock()
        mock_askopenfile.return_value = mock_file

        # Custom parameters
        initialdir = "/tmp"
        mode = "rb"
        filetypes = [
            ("Text files", "*.txt"),
            ("Python files", "*.py"),
            ("All files", "*"),
        ]

        # Call FileDialog with custom parameters
        result = ntk.FileDialog(
            app, initialdir=initialdir, mode=mode, filetypes=filetypes
        )

        # Check that the dialog was opened with custom parameters
        mock_askopenfile.assert_called_once_with(
            initialdir=initialdir, mode=mode, filetypes=filetypes
        )

        # Check that the result is the mocked file
        assert result == mock_file

    @patch("tkinter.filedialog.askopenfile")
    def test_file_dialog_cancel(self, mock_askopenfile, app):
        """Test file dialog when user cancels."""
        # Mock cancellation (returns None)
        mock_askopenfile.return_value = None

        # Call FileDialog
        result = ntk.FileDialog(app)

        # Check that the dialog was opened
        mock_askopenfile.assert_called_once()

        # Check that the result is None
        assert result is None

    @patch("tkinter.filedialog.askopenfile")
    def test_file_dialog_with_window_state(self, mock_askopenfile, app):
        """Test file dialog interaction with window state."""
        # Mock file object
        mock_file = MagicMock()
        mock_askopenfile.return_value = mock_file

        # Mock window leave_window method
        app.leave_window = MagicMock()

        # Call FileDialog
        result = ntk.FileDialog(app)

        # Check that leave_window was called twice (before and after dialog)
        assert app.leave_window.call_count == 2

        # Check that the result is the mocked file
        assert result == mock_file
