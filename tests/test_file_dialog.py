import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import file_manager


class TestFileDialog:
    """Tests for FileDialog functionality."""

    @pytest.fixture
    def app(self):
        window = MagicMock()
        window.leave_window = MagicMock()
        return window

    @patch("nebulatk.file_manager._open_with_windows_native")
    @patch("nebulatk.file_manager.sys.platform", "win32")
    def test_file_dialog_windows(self, mock_windows_dialog, app):
        """Uses native Windows backend."""
        mock_file = MagicMock()
        mock_windows_dialog.return_value = mock_file

        result = file_manager.FileDialog(
            app, initialdir=None, mode="r", filetypes=(("All files", "*"),)
        )

        mock_windows_dialog.assert_called_once_with(
            None, "r", (("All files", "*"),)
        )
        assert result == mock_file
        assert app.leave_window.call_count == 2

    @patch("nebulatk.file_manager._open_with_macos_native")
    @patch("nebulatk.file_manager.sys.platform", "darwin")
    def test_file_dialog_macos(self, mock_macos_dialog, app):
        """Uses native macOS backend."""
        mock_file = MagicMock()
        mock_macos_dialog.return_value = mock_file

        result = file_manager.FileDialog(app, initialdir="/tmp", mode="rb", filetypes=[])

        mock_macos_dialog.assert_called_once_with("/tmp", "rb", [])
        assert result == mock_file
        assert app.leave_window.call_count == 2

    @patch("nebulatk.file_manager._open_with_linux_native")
    @patch("nebulatk.file_manager.sys.platform", "linux")
    def test_file_dialog_linux_cancel(self, mock_linux_dialog, app):
        """Returns None when Linux picker is cancelled."""
        mock_linux_dialog.return_value = None

        result = file_manager.FileDialog(app)

        mock_linux_dialog.assert_called_once_with(None, "r", (("All files", "*"),))
        assert result is None
        assert app.leave_window.call_count == 2

    @patch("nebulatk.file_manager._open_with_linux_native")
    @patch("nebulatk.file_manager.sys.platform", "linux")
    def test_file_dialog_always_restores_window_state(self, mock_linux_dialog, app):
        """Ensures leave_window runs even on backend errors."""
        mock_linux_dialog.side_effect = RuntimeError("dialog failed")

        result = file_manager.FileDialog(app)

        assert result is None
        assert app.leave_window.call_count == 2
