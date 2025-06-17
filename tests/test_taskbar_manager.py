import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import types

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)


class MockWindow:
    """Mock window object for testing."""

    def __init__(self):
        self.root = None
        self._setup_mock_root()
        self.width = 1200
        self.height = 900

    def _setup_mock_root(self):
        """Set up mock tkinter root."""
        self.root = MagicMock()
        self.root.winfo_id.return_value = 12345
        self.root.after.return_value = "timer_id"
        self.root.after_cancel = MagicMock()


class MockCOMTypes:
    """Mock COM types for testing."""

    def __init__(self):
        self.GUID = MagicMock()
        self.CoInitialize = MagicMock()
        self.CoUninitialize = MagicMock()
        self.CoCreateInstance = MagicMock()
        self.HRESULT = MagicMock()
        self.POINTER = MagicMock()
        self.IUnknown = MagicMock()
        self.COMMETHOD = MagicMock()

        # Set up comtypes.client module mock
        self.client = MagicMock()
        self.client.CreateObject = MagicMock()

        # Configure CreateObject to return a comprehensive mock
        mock_com_object = MagicMock()
        mock_com_object.QueryInterface = MagicMock()
        mock_com_object.AddRef = MagicMock(return_value=1)
        mock_com_object.Release = MagicMock(return_value=0)

        # Mock common COM interfaces that might be requested
        mock_com_object.ITaskbarList3 = MagicMock()
        mock_com_object.ITaskbarList4 = MagicMock()

        self.client.CreateObject.return_value = mock_com_object


class MockCTypes:
    """Mock ctypes module for testing."""

    def __init__(self):
        self.windll = MagicMock()
        self.wintypes = MagicMock()
        self.CFUNCTYPE = MagicMock()
        self.c_int = int
        self.c_void_p = MagicMock
        self.c_long = int
        self.c_ulong = int  # Added missing c_ulong
        self.c_uint = int
        self.c_ulonglong = int
        self.c_int64 = int
        self.c_uint32 = int
        self.c_int32 = int
        self.c_uint16 = int
        self.c_char_p = MagicMock
        self.byref = MagicMock()
        # This will be set up later with the interface mock
        self.cast = None
        self.POINTER = MagicMock()
        self.Structure = MagicMock()
        self.WINFUNCTYPE = MagicMock()
        self.HRESULT = MagicMock()
        self.sizeof = MagicMock(return_value=8)

        # Set up OleDLL mock for COM interface creation
        mock_ole32 = MagicMock()
        mock_ole32.CoCreateInstance.return_value = 0  # S_OK
        self.OleDLL = MagicMock(return_value=mock_ole32)

        # Mock vtbl and interface for successful initialization
        mock_vtbl = MagicMock()
        mock_vtbl.HrInit.return_value = 0  # S_OK
        mock_vtbl.SetProgressState.return_value = 0
        mock_vtbl.SetProgressValue.return_value = 0
        mock_vtbl.SetOverlayIcon.return_value = 0
        mock_vtbl.SetThumbnailToolTip.return_value = 0
        mock_vtbl.SetThumbnailClip.return_value = 0

        mock_interface_contents = MagicMock()
        mock_interface_contents.lpVtbl.contents = mock_vtbl

        mock_interface = MagicMock()
        mock_interface.contents = mock_interface_contents

        self.mock_taskbar_interface = mock_interface
        self.mock_vtbl = mock_vtbl

        # Set up cast to return our mock interface
        self.cast = MagicMock(return_value=mock_interface)


@pytest.fixture
def mock_modules():
    """Set up comprehensive mocking for Windows-specific modules."""
    mock_ctypes = MockCTypes()
    mock_ctypes.wintypes.HWND = int
    mock_ctypes.wintypes.POINT = MagicMock

    # Create a proper mock RECT class that has attributes
    class MockRECT:
        def __init__(self, left=0, top=0, right=0, bottom=0):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    mock_ctypes.wintypes.RECT = MockRECT

    mock_comtypes = MockCOMTypes()

    with patch.dict(
        "sys.modules",
        {
            "comtypes": mock_comtypes,
            "comtypes.client": mock_comtypes.client,
            "ctypes": mock_ctypes,
            "ctypes.wintypes": mock_ctypes.wintypes,
        },
    ):
        yield


@pytest.fixture
def mock_window():
    """Create a mock window for testing."""
    return MockWindow()


class TestTaskbarManagerInit:
    """Test TaskbarManager initialization."""

    @pytest.mark.skipif(
        sys.platform != "win32", reason="Windows-specific functionality"
    )
    def test_init_on_windows(self, mock_modules, mock_window):
        """Test TaskbarManager initialization on Windows."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        assert manager.window is mock_window
        assert manager.auto_invalidate_enabled is True
        assert manager.debounce_delay == 50

    def test_init_cross_platform(self, mock_modules, mock_window):
        """Test TaskbarManager initialization with mocked Windows components."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        assert manager.window is mock_window
        assert manager.debounce_delay == 50
        assert manager.auto_invalidate_enabled is True


class TestTaskbarManagerFeatures:
    """Test TaskbarManager feature methods."""

    def test_set_progress_valid_range(self, mock_modules, mock_window):
        """Test setting progress with valid values and verify correct parameters."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.vtbl.SetProgressState.return_value = 0
        manager.vtbl.SetProgressValue.return_value = 0
        manager.hwnd = 12345

        # Test progress = 0 (should set NOPROGRESS state)
        result = manager.SetProgress(0)
        assert result is True
        manager.vtbl.SetProgressState.assert_called_with(
            manager.taskbar_interface, 12345, 0  # TBPF_NOPROGRESS = 0
        )

        # Reset mocks
        manager.vtbl.SetProgressState.reset_mock()
        manager.vtbl.SetProgressValue.reset_mock()

        # Test progress = 50 (should set NORMAL state and value)
        result = manager.SetProgress(50)
        assert result is True
        manager.vtbl.SetProgressState.assert_called_with(
            manager.taskbar_interface, 12345, 2  # TBPF_NORMAL = 2
        )
        manager.vtbl.SetProgressValue.assert_called_with(
            manager.taskbar_interface, 12345, 50, 100
        )

        # Reset mocks
        manager.vtbl.SetProgressState.reset_mock()
        manager.vtbl.SetProgressValue.reset_mock()

        # Test progress = 100 (should set NORMAL state and value)
        result = manager.SetProgress(100)
        assert result is True
        manager.vtbl.SetProgressState.assert_called_with(
            manager.taskbar_interface, 12345, 2  # TBPF_NORMAL = 2
        )
        manager.vtbl.SetProgressValue.assert_called_with(
            manager.taskbar_interface, 12345, 100, 100
        )

    def test_set_progress_invalid_range(self, mock_modules, mock_window):
        """Test setting progress with invalid values."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test invalid progress values
        with pytest.raises(ValueError, match="Progress must be between 0 and 100"):
            manager.SetProgress(-1)

        with pytest.raises(ValueError, match="Progress must be between 0 and 100"):
            manager.SetProgress(101)

    def test_set_progress_error_handling(self, mock_modules, mock_window):
        """Test progress setting error handling."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.hwnd = 12345

        # Test SetProgressState failure
        manager.vtbl.SetProgressState.return_value = 0x80004005  # E_FAIL
        result = manager.SetProgress(50)
        assert result is False

        # Test SetProgressValue failure
        manager.vtbl.SetProgressState.return_value = 0  # S_OK
        manager.vtbl.SetProgressValue.return_value = 0x80004005  # E_FAIL
        result = manager.SetProgress(50)
        assert result is False

    def test_set_thumbnail_notification_parameters(self, mock_modules, mock_window):
        """Test thumbnail notification with detailed parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.vtbl.SetOverlayIcon.return_value = 0
        manager.hwnd = 12345

        # Mock LoadIconW to return specific handles
        with patch("ctypes.windll.user32.LoadIconW") as mock_load_icon:
            mock_load_icon.return_value = 9999

            # Test warning icon
            result = manager.SetThumbnailNotification("warning")
            assert result is True

            # Verify LoadIconW was called with correct parameters
            mock_load_icon.assert_called_once()
            # Verify SetOverlayIcon was called with correct parameters
            manager.vtbl.SetOverlayIcon.assert_called_with(
                manager.taskbar_interface, 12345, 9999, "Warning Icon"
            )

            # Reset mocks
            mock_load_icon.reset_mock()
            manager.vtbl.SetOverlayIcon.reset_mock()

            # Test error icon
            result = manager.SetThumbnailNotification("error")
            assert result is True
            manager.vtbl.SetOverlayIcon.assert_called_with(
                manager.taskbar_interface, 12345, 9999, "Error Icon"
            )

            # Reset mocks
            mock_load_icon.reset_mock()
            manager.vtbl.SetOverlayIcon.reset_mock()

            # Test info icon
            result = manager.SetThumbnailNotification("info")
            assert result is True
            manager.vtbl.SetOverlayIcon.assert_called_with(
                manager.taskbar_interface, 12345, 9999, "Info Icon"
            )

            # Reset mocks
            mock_load_icon.reset_mock()
            manager.vtbl.SetOverlayIcon.reset_mock()

            # Test clearing icon (None)
            result = manager.SetThumbnailNotification(None)
            assert result is True
            # LoadIconW should not be called for None
            mock_load_icon.assert_not_called()
            manager.vtbl.SetOverlayIcon.assert_called_with(
                manager.taskbar_interface, 12345, None, ""
            )

    def test_set_thumbnail_notification_error_handling(self, mock_modules, mock_window):
        """Test thumbnail notification error handling."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.vtbl.SetOverlayIcon.return_value = 0x80004005  # E_FAIL
        manager.hwnd = 12345

        result = manager.SetThumbnailNotification("warning")
        assert result is False

    def test_set_thumbnail_clip_parameters(self, mock_modules, mock_window):
        """Test thumbnail clipping with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True
        manager.hwnd = 12345

        # Mock dwmapi
        with patch("ctypes.windll.dwmapi") as mock_dwmapi:
            mock_dwmapi.DwmInvalidateIconicBitmaps.return_value = 0

            # Test setting clip rectangle with specific values
            manager.SetThumbnailClip(10, 20, 300, 400)

            # Verify clip_rect is set with correct values
            assert manager.clip_rect is not None
            assert manager.clip_rect.left == 10
            assert manager.clip_rect.top == 20
            assert manager.clip_rect.right == 310  # left + width
            assert manager.clip_rect.bottom == 420  # top + height

            # Verify DwmInvalidateIconicBitmaps was called with correct hwnd
            mock_dwmapi.DwmInvalidateIconicBitmaps.assert_called_once_with(12345)

    def test_set_thumbnail_clip_validation(self, mock_modules, mock_window):
        """Test thumbnail clipping with dimension validation."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True

        # Mock dwmapi
        with patch("ctypes.windll.dwmapi") as mock_dwmapi:
            mock_dwmapi.DwmInvalidateIconicBitmaps.return_value = 0

            # Test with negative coordinates (should be clamped to 0)
            manager.SetThumbnailClip(-10, -20, 300, 400)
            assert manager.clip_rect.left == 0
            assert manager.clip_rect.top == 0
            assert manager.clip_rect.right == 300
            assert manager.clip_rect.bottom == 400

            # Test with zero dimensions (should be clamped to 1)
            manager.SetThumbnailClip(10, 20, 0, 0)
            assert manager.clip_rect.left == 10
            assert manager.clip_rect.top == 20
            assert manager.clip_rect.right == 11  # 10 + 1
            assert manager.clip_rect.bottom == 21  # 20 + 1

            # Test with oversized dimensions (should be clamped)
            manager.SetThumbnailClip(0, 0, 50000, 50000)
            assert manager.clip_rect.left == 0
            assert manager.clip_rect.top == 0
            assert manager.clip_rect.right == 32767  # MAX_DIMENSION
            assert manager.clip_rect.bottom == 32767  # MAX_DIMENSION

    def test_clear_thumbnail_clip_parameters(self, mock_modules, mock_window):
        """Test clearing thumbnail clipping rectangle with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True
        manager.hwnd = 54321

        # Set initial clip rect
        from ctypes import wintypes

        manager.clip_rect = wintypes.RECT(10, 20, 310, 420)

        # Mock dwmapi
        with patch("ctypes.windll.dwmapi") as mock_dwmapi:
            mock_dwmapi.DwmInvalidateIconicBitmaps.return_value = 0

            # Test clearing clip rectangle
            manager.ClearThumbnailClip()

            # Verify clip_rect is None
            assert manager.clip_rect is None

            # Verify DwmInvalidateIconicBitmaps was called with correct hwnd
            mock_dwmapi.DwmInvalidateIconicBitmaps.assert_called_once_with(54321)

    def test_auto_invalidation_control(self, mock_modules, mock_window):
        """Test auto-invalidation enable/disable."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test enabling auto-invalidation
        manager.SetAutoInvalidation(True)
        assert manager.IsAutoInvalidationEnabled() is True

        # Test disabling auto-invalidation
        manager.SetAutoInvalidation(False)
        assert manager.IsAutoInvalidationEnabled() is False

    def test_debounce_delay_control(self, mock_modules, mock_window):
        """Test debounce delay configuration."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test setting debounce delay
        manager.SetDebounceDelay(100)
        assert manager.GetDebounceDelay() == 100

        # Test minimum debounce delay
        manager.SetDebounceDelay(5)
        assert manager.GetDebounceDelay() == 10  # Should be clamped to minimum

        # Test chaining
        result = manager.SetDebounceDelay(200)
        assert result is manager  # Should return self for chaining


class TestTaskbarManagerValidation:
    """Test TaskbarManager validation methods."""

    def test_validate_dimensions(self, mock_modules, mock_window):
        """Test dimension validation and clamping."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test normal dimensions
        width, height = manager._validate_dimensions(800, 600)
        assert width == 800
        assert height == 600

        # Test zero/negative dimensions
        width, height = manager._validate_dimensions(0, -100)
        assert width == 1
        assert height == 1

        # Test oversized dimensions
        width, height = manager._validate_dimensions(50000, 50000)
        assert width == 32767  # MAX_DIMENSION
        assert height == 32767  # MAX_DIMENSION

    def test_validate_coordinates(self, mock_modules, mock_window):
        """Test coordinate validation and clamping."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test normal coordinates
        x, y = manager._validate_coordinates(100, 200)
        assert x == 100
        assert y == 200

        # Test negative coordinates
        x, y = manager._validate_coordinates(-50, -100)
        assert x == 0
        assert y == 0

        # Test with max bounds
        x, y = manager._validate_coordinates(1000, 2000, max_x=500, max_y=800)
        assert x == 500
        assert y == 800


class TestTaskbarManagerThumbnails:
    """Test TaskbarManager thumbnail functionality."""

    def test_thumbnail_request_delegation(self, mock_modules, mock_window):
        """Test thumbnail request delegation."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test thumbnail request delegation
        manager._delegate_thumbnail_request(12345, 200, 150)

        # Verify flags are set
        assert manager.thumbnail_request_flag is True
        assert manager.thumbnail_width == 200
        assert manager.thumbnail_height == 150

    def test_live_preview_request_delegation(self, mock_modules, mock_window):
        """Test live preview request delegation."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test live preview request delegation
        manager._delegate_live_preview_request(12345)

        # Verify flag is set
        assert manager.live_preview_request_flag is True

    def test_create_full_thumbnail(self, mock_modules, mock_window):
        """Test full thumbnail creation."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Mock _create_thumbnail_bitmap
        with patch.object(manager, "_create_thumbnail_bitmap") as mock_create:
            mock_create.return_value = 3001

            # Test full thumbnail creation
            result = manager._create_full_thumbnail(200, 150)

            # Verify bitmap creation was called
            mock_create.assert_called_once_with(0, 0, None, None, 200, 150)
            assert result == 3001

    def test_handle_thumbnail_request_safe_parameters(self, mock_modules, mock_window):
        """Test safe thumbnail request handling with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.clip_rect = None
        manager.hwnd = 12345

        # Mock bitmap creation
        with patch.object(manager, "_create_full_thumbnail") as mock_create:
            mock_create.return_value = 3001  # Mock bitmap handle

            # Mock DwmSetIconicThumbnail
            with patch("ctypes.windll.dwmapi.DwmSetIconicThumbnail") as mock_dwm:
                mock_dwm.return_value = 0

                # Mock DeleteObject
                with patch("ctypes.windll.gdi32.DeleteObject") as mock_delete:
                    mock_delete.return_value = True

                    # Test thumbnail request handling
                    manager._handle_thumbnail_request_safe(12345, 200, 150)

                    # Verify thumbnail creation was called with validated dimensions
                    mock_create.assert_called_once_with(200, 150)

                    # Verify DwmSetIconicThumbnail was called with correct parameters
                    mock_dwm.assert_called_once_with(12345, 3001, 0)

                    # Verify bitmap was cleaned up
                    mock_delete.assert_called_once_with(3001)

    def test_handle_thumbnail_request_safe_with_clipping(
        self, mock_modules, mock_window
    ):
        """Test safe thumbnail request handling with clipping enabled."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Set up clipping rectangle
        from ctypes import wintypes

        manager.clip_rect = wintypes.RECT(10, 20, 310, 420)

        # Mock bitmap creation
        with patch.object(manager, "_create_clipped_thumbnail") as mock_create:
            mock_create.return_value = 3002  # Mock bitmap handle

            # Mock DwmSetIconicThumbnail
            with patch("ctypes.windll.dwmapi.DwmSetIconicThumbnail") as mock_dwm:
                mock_dwm.return_value = 0

                # Mock DeleteObject
                with patch("ctypes.windll.gdi32.DeleteObject") as mock_delete:
                    mock_delete.return_value = True

                    # Test thumbnail request handling with clipping
                    manager._handle_thumbnail_request_safe(12345, 200, 150)

                    # Verify clipped thumbnail creation was called
                    mock_create.assert_called_once_with(200, 150)

                    # Verify DwmSetIconicThumbnail was called with correct parameters
                    mock_dwm.assert_called_once_with(12345, 3002, 0)

                    # Verify bitmap was cleaned up
                    mock_delete.assert_called_once_with(3002)

    def test_handle_live_preview_request_safe_parameters(
        self, mock_modules, mock_window
    ):
        """Test safe live preview request handling with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Mock client rect
        mock_rect = MagicMock()
        mock_rect.right = 800
        mock_rect.left = 0
        mock_rect.bottom = 600
        mock_rect.top = 0

        # Mock bitmap creation
        with patch.object(manager, "_create_live_preview_bitmap") as mock_create:
            mock_create.return_value = 3003  # Mock bitmap handle

            # Mock DwmSetIconicLivePreviewBitmap
            with patch(
                "ctypes.windll.dwmapi.DwmSetIconicLivePreviewBitmap"
            ) as mock_dwm:
                mock_dwm.return_value = 0

                # Mock GetClientRect
                with patch("ctypes.windll.user32.GetClientRect") as mock_get_rect:
                    mock_get_rect.return_value = True

                    # Mock wintypes.RECT instantiation
                    with patch("ctypes.wintypes.RECT", return_value=mock_rect):
                        # Mock DeleteObject
                        with patch("ctypes.windll.gdi32.DeleteObject") as mock_delete:
                            mock_delete.return_value = True

                            # Test live preview request handling
                            manager._handle_live_preview_request_safe(12345)

                            # Verify GetClientRect was called with correct hwnd
                            mock_get_rect.assert_called_once()

                            # Verify bitmap creation was called with client dimensions
                            mock_create.assert_called_once_with(800, 600)

                            # Verify DwmSetIconicLivePreviewBitmap was called with correct parameters
                            mock_dwm.assert_called_once_with(12345, 3003, None, 0)

                            # Verify bitmap was cleaned up
                            mock_delete.assert_called_once_with(3003)

    def test_create_clipped_thumbnail_parameters(self, mock_modules, mock_window):
        """Test clipped thumbnail creation with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Set up clipping rectangle
        from ctypes import wintypes

        manager.clip_rect = wintypes.RECT(10, 20, 310, 420)

        # Mock _create_thumbnail_bitmap
        with patch.object(manager, "_create_thumbnail_bitmap") as mock_create:
            mock_create.return_value = 3004

            # Test clipped thumbnail creation
            result = manager._create_clipped_thumbnail(200, 150)

            # Verify bitmap creation was called with correct clip parameters
            mock_create.assert_called_once_with(
                10,  # clip_rect.left
                20,  # clip_rect.top
                300,  # clip_rect.right - clip_rect.left
                400,  # clip_rect.bottom - clip_rect.top
                200,  # thumb_width
                150,  # thumb_height
            )
            assert result == 3004

    def test_create_live_preview_bitmap_parameters(self, mock_modules, mock_window):
        """Test live preview bitmap creation with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Mock client rect
        mock_rect = MagicMock()
        mock_rect.right = 1024
        mock_rect.left = 0
        mock_rect.bottom = 768
        mock_rect.top = 0

        # Mock _create_thumbnail_bitmap
        with patch.object(manager, "_create_thumbnail_bitmap") as mock_create:
            mock_create.return_value = 3005

            # Mock GetClientRect
            with patch("ctypes.windll.user32.GetClientRect") as mock_get_rect:
                mock_get_rect.return_value = True

                # Mock wintypes.RECT instantiation
                with patch("ctypes.wintypes.RECT", return_value=mock_rect):
                    # Test live preview bitmap creation
                    result = manager._create_live_preview_bitmap(400, 300)

                    # Verify GetClientRect was called with correct hwnd
                    mock_get_rect.assert_called_once()

                    # Verify bitmap creation was called with bypass_clipping=True
                    mock_create.assert_called_once_with(
                        0,  # src_x
                        0,  # src_y
                        1024,  # client_width
                        768,  # client_height
                        400,  # width
                        300,  # height
                        bypass_clipping=True,
                    )
                    assert result == 3005


class TestTaskbarManagerTooltips:
    """Test TaskbarManager tooltip functionality."""

    def test_set_thumbnail_tooltip_parameters(self, mock_modules, mock_window):
        """Test setting thumbnail tooltip with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.vtbl.SetThumbnailToolTip.return_value = 0
        manager.hwnd = 12345

        # Test setting tooltip
        result = manager._set_thumbnail_tooltip("Test Tooltip")

        # Verify SetThumbnailToolTip was called with correct parameters
        manager.vtbl.SetThumbnailToolTip.assert_called_once_with(
            manager.taskbar_interface, 12345, "Test Tooltip"
        )
        assert result is True

    def test_set_thumbnail_tooltip_error_handling(self, mock_modules, mock_window):
        """Test tooltip setting error handling."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_interface = MagicMock()
        manager.vtbl = MagicMock()
        manager.vtbl.SetThumbnailToolTip.return_value = 0x80004005  # E_FAIL
        manager.hwnd = 12345

        # Test setting tooltip with error
        result = manager._set_thumbnail_tooltip("Test Tooltip")

        # Verify error handling
        assert result is False


class TestTaskbarManagerWindowMessages:
    """Test TaskbarManager window message handling."""

    def test_taskbar_button_created_handling(self, mock_modules, mock_window):
        """Test taskbar button created message handling."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Mock _apply_taskbar_features
        with patch.object(manager, "_apply_taskbar_features") as mock_apply:
            # Test taskbar button created handling
            manager._on_taskbar_button_created()

            # Verify features were applied
            mock_apply.assert_called_once()

    def test_apply_taskbar_features_sequence(self, mock_modules, mock_window):
        """Test the sequence of taskbar feature application."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Mock the individual setup methods
        with patch.object(manager, "_setup_custom_thumbnails") as mock_setup:
            with patch.object(manager, "_set_thumbnail_tooltip") as mock_tooltip:
                with patch(
                    "ctypes.windll.dwmapi.DwmInvalidateIconicBitmaps"
                ) as mock_invalidate:
                    mock_setup.return_value = True
                    mock_tooltip.return_value = True
                    mock_invalidate.return_value = 0

                    # Test applying taskbar features
                    manager._apply_taskbar_features()

                    # Verify setup sequence
                    mock_setup.assert_called_once()
                    mock_tooltip.assert_called_once_with("TaskbarManager Demo")
                    mock_invalidate.assert_called_once_with(12345)

                    # Verify taskbar button is marked as created
                    assert manager.taskbar_button_created is True

    def test_setup_custom_thumbnails_parameters(self, mock_modules, mock_window):
        """Test custom thumbnail setup with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Mock DwmSetWindowAttribute
        with patch("ctypes.windll.dwmapi.DwmSetWindowAttribute") as mock_dwm:
            mock_dwm.return_value = 0  # S_OK

            # Test custom thumbnail setup
            result = manager._setup_custom_thumbnails()

            # Verify DwmSetWindowAttribute was called with correct parameters
            assert mock_dwm.call_count == 3  # Three different attributes

            # Check the calls were made with correct attribute constants
            calls = mock_dwm.call_args_list

            # DWMWA_FORCE_ICONIC_REPRESENTATION = 7
            assert calls[0][0][1] == 7
            # DWMWA_HAS_ICONIC_BITMAP = 10
            assert calls[1][0][1] == 10
            # DWMWA_DISALLOW_PEEK = 12
            assert calls[2][0][1] == 12

            # All calls should be for the correct window handle
            for call in calls:
                assert call[0][0] == 12345

            assert result is True

    def test_manual_apply_when_not_created(self, mock_modules, mock_window):
        """Test manual apply when taskbar button not yet created."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = False

        # Mock _apply_taskbar_features
        with patch.object(manager, "_apply_taskbar_features") as mock_apply:
            # Test manual apply
            manager.manual_apply()

            # Verify features were applied
            mock_apply.assert_called_once()

    def test_manual_apply_when_already_created(self, mock_modules, mock_window):
        """Test manual apply when taskbar button already created."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True

        # Mock _apply_taskbar_features
        with patch.object(manager, "_apply_taskbar_features") as mock_apply:
            # Test manual apply
            manager.manual_apply()

            # Verify features were NOT applied again
            mock_apply.assert_not_called()


class TestTaskbarManagerInvalidation:
    """Test TaskbarManager invalidation functionality."""

    def test_invalidate_live_preview_parameters(self, mock_modules, mock_window):
        """Test live preview invalidation with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True
        manager.hwnd = 54321

        # Mock DwmInvalidateIconicBitmaps
        with patch("ctypes.windll.dwmapi.DwmInvalidateIconicBitmaps") as mock_dwm:
            mock_dwm.return_value = 0

            # Test invalidation
            manager.InvalidateLivePreview()

            # Verify DWM API was called with correct window handle
            mock_dwm.assert_called_once_with(54321)

    def test_invalidate_live_preview_when_not_created(self, mock_modules, mock_window):
        """Test live preview invalidation when taskbar button not created."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = False

        # Mock DwmInvalidateIconicBitmaps
        with patch("ctypes.windll.dwmapi.DwmInvalidateIconicBitmaps") as mock_dwm:
            # Test invalidation
            manager.InvalidateLivePreview()

            # Verify DWM API was NOT called
            mock_dwm.assert_not_called()

    def test_auto_invalidate_thumbnails_parameters(self, mock_modules, mock_window):
        """Test automatic thumbnail invalidation with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True
        manager.debounce_delay = 50

        # Mock root.after to capture the callback
        manager.root.after = MagicMock(return_value="timer_id")
        manager.root.after_cancel = MagicMock()

        # Test auto invalidation
        manager._auto_invalidate_thumbnails()

        # Verify timer was scheduled with correct delay
        manager.root.after.assert_called_once_with(50, manager._perform_invalidation)

        # Test cancellation of previous timer
        manager._invalidate_pending = "old_timer_id"
        manager._auto_invalidate_thumbnails()

        # Verify old timer was cancelled
        manager.root.after_cancel.assert_called_with("old_timer_id")

    def test_perform_invalidation_parameters(self, mock_modules, mock_window):
        """Test actual invalidation performance with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.taskbar_button_created = True
        manager.hwnd = 98765

        # Mock DwmInvalidateIconicBitmaps
        with patch("ctypes.windll.dwmapi.DwmInvalidateIconicBitmaps") as mock_dwm:
            mock_dwm.return_value = 0

            # Set up pending invalidation attribute
            manager._invalidate_pending = "test_timer_id"

            # Test invalidation
            manager._perform_invalidation()

            # Verify DWM API was called with correct window handle
            mock_dwm.assert_called_once_with(98765)

            # Verify pending invalidation attribute was cleared
            assert not hasattr(manager, "_invalidate_pending")


class TestTaskbarManagerPolling:
    """Test TaskbarManager polling functionality with parameter verification."""

    def test_poll_for_requests_thumbnail_debouncing(self, mock_modules, mock_window):
        """Test polling for thumbnail requests with debouncing parameters."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.thumbnail_request_flag = True
        manager.thumbnail_pending_timer = "old_timer_id"
        manager.debounce_delay = 75

        # Mock root.after and after_cancel
        manager.root.after = MagicMock(return_value="new_timer_id")
        manager.root.after_cancel = MagicMock()

        # Test polling
        manager._poll_for_requests()

        # Verify old timer was cancelled
        manager.root.after_cancel.assert_called_with("old_timer_id")

        # Verify new timer was scheduled with correct delay and callback
        calls = manager.root.after.call_args_list
        assert len(calls) >= 1

        # Find the debounced thumbnail call
        thumbnail_call = None
        for call in calls:
            if call[0][0] == 75:  # debounce_delay
                thumbnail_call = call
                break

        assert thumbnail_call is not None
        assert thumbnail_call[0][0] == 75
        assert thumbnail_call[0][1] == manager._process_debounced_thumbnail

        # Verify flag was cleared
        assert manager.thumbnail_request_flag is False

    def test_poll_for_requests_live_preview_debouncing(self, mock_modules, mock_window):
        """Test polling for live preview requests with debouncing parameters."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.live_preview_request_flag = True
        manager.live_preview_pending_timer = "old_preview_timer"
        manager.debounce_delay = 100

        # Mock root.after and after_cancel
        manager.root.after = MagicMock(return_value="new_preview_timer")
        manager.root.after_cancel = MagicMock()

        # Test polling
        manager._poll_for_requests()

        # Verify old timer was cancelled
        manager.root.after_cancel.assert_called_with("old_preview_timer")

        # Verify new timer was scheduled with correct delay and callback
        calls = manager.root.after.call_args_list
        assert len(calls) >= 1

        # Find the debounced live preview call
        preview_call = None
        for call in calls:
            if call[0][0] == 100:  # debounce_delay
                preview_call = call
                break

        assert preview_call is not None
        assert preview_call[0][0] == 100
        assert preview_call[0][1] == manager._process_debounced_live_preview

        # Verify flag was cleared
        assert manager.live_preview_request_flag is False

    def test_process_debounced_thumbnail_parameters(self, mock_modules, mock_window):
        """Test debounced thumbnail processing with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 11111
        manager.thumbnail_width = 320
        manager.thumbnail_height = 240

        # Mock the actual processing method
        with patch.object(manager, "_handle_thumbnail_request_safe") as mock_handle:
            # Test debounced thumbnail processing
            manager._process_debounced_thumbnail()

            # Verify correct parameters were passed
            mock_handle.assert_called_once_with(11111, 320, 240)

            # Verify timer reference was cleared
            assert manager.thumbnail_pending_timer is None

    def test_process_debounced_live_preview_parameters(self, mock_modules, mock_window):
        """Test debounced live preview processing with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 22222

        # Mock the actual processing method
        with patch.object(manager, "_handle_live_preview_request_safe") as mock_handle:
            # Test debounced live preview processing
            manager._process_debounced_live_preview()

            # Verify correct parameters were passed
            mock_handle.assert_called_once_with(22222)

            # Verify timer reference was cleared
            assert manager.live_preview_pending_timer is None


class TestTaskbarManagerValidationEdgeCases:
    """Test TaskbarManager validation edge cases with detailed parameter verification."""

    def test_validate_dimensions_edge_cases(self, mock_modules, mock_window):
        """Test dimension validation edge cases."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test float inputs (should be converted to int)
        width, height = manager._validate_dimensions(800.7, 600.3)
        assert width == 800
        assert height == 600
        assert isinstance(width, int)
        assert isinstance(height, int)

        # Test very large negative numbers
        width, height = manager._validate_dimensions(-99999, -88888)
        assert width == 1
        assert height == 1

        # Test exact boundary values
        width, height = manager._validate_dimensions(32767, 32767)
        assert width == 32767
        assert height == 32767

        # Test just over boundary
        width, height = manager._validate_dimensions(32768, 32768)
        assert width == 32767  # Should be clamped
        assert height == 32767  # Should be clamped

    def test_validate_coordinates_edge_cases(self, mock_modules, mock_window):
        """Test coordinate validation edge cases."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test float inputs (should be converted to int)
        x, y = manager._validate_coordinates(100.9, 200.1)
        assert x == 100
        assert y == 200
        assert isinstance(x, int)
        assert isinstance(y, int)

        # Test very large negative numbers
        x, y = manager._validate_coordinates(-50000, -60000)
        assert x == 0
        assert y == 0

        # Test with max bounds as floats
        x, y = manager._validate_coordinates(1000.5, 2000.7, max_x=500.2, max_y=800.8)
        assert x == 500  # Should respect int(max_x)
        assert y == 800  # Should respect int(max_y)

        # Test exact boundary values
        x, y = manager._validate_coordinates(32767, 32767)
        assert x == 32767
        assert y == 32767

        # Test just over boundary
        x, y = manager._validate_coordinates(32768, 32768)
        assert x == 32767  # Should be clamped
        assert y == 32767  # Should be clamped

    def test_dimension_validation_with_name_parameter(self, mock_modules, mock_window):
        """Test dimension validation with custom name parameter for error messages."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)

        # Test with custom name (should not affect validation logic, just messaging)
        width, height = manager._validate_dimensions(50000, 40000, "custom region")
        assert width == 32767
        assert height == 32767

        # Test normal case with custom name
        width, height = manager._validate_dimensions(800, 600, "test area")
        assert width == 800
        assert height == 600


class TestTaskbarManagerErrorHandling:
    """Test TaskbarManager error handling scenarios."""

    def test_bitmap_creation_failure_handling(self, mock_modules, mock_window):
        """Test handling of bitmap creation failures."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.clip_rect = None

        # Mock bitmap creation to fail
        with patch.object(manager, "_create_full_thumbnail") as mock_create:
            mock_create.return_value = None  # Simulate failure

            # Mock DwmSetIconicThumbnail (should not be called)
            with patch("ctypes.windll.dwmapi.DwmSetIconicThumbnail") as mock_dwm:
                # Test thumbnail request handling with failed bitmap creation
                manager._handle_thumbnail_request_safe(12345, 200, 150)

                # Verify DwmSetIconicThumbnail was NOT called due to failed bitmap
                mock_dwm.assert_not_called()

    def test_dwm_api_error_handling(self, mock_modules, mock_window):
        """Test handling of DWM API errors."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 12345

        # Mock DwmSetWindowAttribute to fail
        with patch("ctypes.windll.dwmapi.DwmSetWindowAttribute") as mock_dwm:
            mock_dwm.return_value = 0x80004005  # E_FAIL

            # Test custom thumbnail setup with DWM error
            result = manager._setup_custom_thumbnails()

            # Verify error is handled gracefully
            assert result is False  # Should return False on error

    def test_com_interface_creation_error(self, mock_modules, mock_window):
        """Test handling of COM interface creation errors."""
        # Override the mock to simulate COM creation failure
        mock_ctypes = MockCTypes()
        mock_ole32 = MagicMock()
        mock_ole32.CoCreateInstance.return_value = 0x80004005  # E_FAIL
        mock_ctypes.OleDLL = MagicMock(return_value=mock_ole32)

        with patch.dict(
            "sys.modules",
            {
                "comtypes": MockCOMTypes(),
                "ctypes": mock_ctypes,
                "ctypes.wintypes": mock_ctypes.wintypes,
            },
        ):
            # Clear the module cache to force reimport
            if "taskbar_manager" in sys.modules:
                del sys.modules["taskbar_manager"]

            # Test that COM creation error is handled properly
            from taskbar_manager import TaskbarManager

            with pytest.raises(OSError, match="Failed to create taskbar interface"):
                TaskbarManager(mock_window)

    def test_vtbl_initialization_error(self, mock_modules, mock_window):
        """Test handling of vtbl initialization errors."""
        # Set up mock that succeeds COM creation but fails initialization
        mock_ctypes = MockCTypes()
        mock_ole32 = MagicMock()
        mock_ole32.CoCreateInstance.return_value = 0  # S_OK
        mock_ctypes.OleDLL = MagicMock(return_value=mock_ole32)

        # Mock vtbl initialization to fail
        mock_vtbl = MagicMock()
        mock_vtbl.HrInit.return_value = 0x80004005  # E_FAIL

        mock_interface_contents = MagicMock()
        mock_interface_contents.lpVtbl.contents = mock_vtbl

        mock_interface = MagicMock()
        mock_interface.contents = mock_interface_contents

        mock_ctypes.cast = MagicMock(return_value=mock_interface)

        with patch.dict(
            "sys.modules",
            {
                "comtypes": MockCOMTypes(),
                "ctypes": mock_ctypes,
                "ctypes.wintypes": mock_ctypes.wintypes,
            },
        ):
            # Clear the module cache to force reimport
            if "taskbar_manager" in sys.modules:
                del sys.modules["taskbar_manager"]

            # Test that vtbl initialization error is handled properly
            from taskbar_manager import TaskbarManager

            with pytest.raises(OSError, match="Failed to initialize taskbar interface"):
                TaskbarManager(mock_window)


class TestTaskbarManagerIntegration:
    """Integration tests for TaskbarManager."""

    def test_full_initialization_flow(self, mock_modules, mock_window):
        """Test complete TaskbarManager initialization flow."""
        from taskbar_manager import TaskbarManager

        # Create manager and verify it initializes without errors
        manager = TaskbarManager(mock_window)

        # Verify key components are set up
        assert manager.window is mock_window
        assert manager.auto_invalidate_enabled is True

        # Test operations don't crash
        manager.SetProgress(50)
        manager.SetThumbnailClip(0, 0, 100, 100)
        manager.ClearThumbnailClip()
        manager.SetAutoInvalidation(False)
        manager.SetDebounceDelay(100)

        # Verify the manager is still functional
        assert manager.IsAutoInvalidationEnabled() is False
        assert manager.GetDebounceDelay() == 100

    def test_complete_thumbnail_workflow(self, mock_modules, mock_window):
        """Test complete thumbnail workflow with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 99999
        manager.taskbar_button_created = True

        # Set up comprehensive mocking for the entire workflow
        with patch.object(manager, "_create_thumbnail_bitmap") as mock_create_bitmap:
            mock_create_bitmap.return_value = 4001  # Mock bitmap handle

            with patch(
                "ctypes.windll.dwmapi.DwmSetIconicThumbnail"
            ) as mock_set_thumbnail:
                mock_set_thumbnail.return_value = 0

                with patch("ctypes.windll.gdi32.DeleteObject") as mock_delete:
                    mock_delete.return_value = True

                    # 1. Set clipping rectangle
                    manager.SetThumbnailClip(50, 75, 400, 300)

                    # 2. Simulate thumbnail request
                    manager._delegate_thumbnail_request(99999, 250, 200)

                    # 3. Process the request
                    manager._handle_thumbnail_request_safe(99999, 250, 200)

                    # Verify the complete workflow
                    # Clipping should be set correctly
                    assert manager.clip_rect.left == 50
                    assert manager.clip_rect.top == 75
                    assert manager.clip_rect.right == 450  # 50 + 400
                    assert manager.clip_rect.bottom == 375  # 75 + 300

                    # Request should be delegated correctly
                    assert manager.thumbnail_width == 250
                    assert manager.thumbnail_height == 200

                    # Bitmap should be created with clipped parameters
                    mock_create_bitmap.assert_called_once_with(
                        50,  # clip_rect.left
                        75,  # clip_rect.top
                        400,  # width
                        300,  # height
                        250,  # thumb_width
                        200,  # thumb_height
                    )

                    # DWM should be called with correct parameters
                    mock_set_thumbnail.assert_called_once_with(99999, 4001, 0)

                    # Bitmap should be cleaned up
                    mock_delete.assert_called_once_with(4001)

    def test_complete_live_preview_workflow(self, mock_modules, mock_window):
        """Test complete live preview workflow with parameter verification."""
        from taskbar_manager import TaskbarManager

        manager = TaskbarManager(mock_window)
        manager.hwnd = 88888
        manager.taskbar_button_created = True

        # Mock client rect for live preview
        mock_rect = MagicMock()
        mock_rect.right = 1200
        mock_rect.left = 0
        mock_rect.bottom = 900
        mock_rect.top = 0

        # Set up comprehensive mocking for live preview workflow
        with patch.object(manager, "_create_thumbnail_bitmap") as mock_create_bitmap:
            mock_create_bitmap.return_value = 5001  # Mock bitmap handle

            with patch(
                "ctypes.windll.dwmapi.DwmSetIconicLivePreviewBitmap"
            ) as mock_set_preview:
                mock_set_preview.return_value = 0

                with patch("ctypes.windll.user32.GetClientRect") as mock_get_rect:
                    mock_get_rect.return_value = True

                    with patch("ctypes.wintypes.RECT", return_value=mock_rect):
                        with patch("ctypes.windll.gdi32.DeleteObject") as mock_delete:
                            mock_delete.return_value = True

                            # 1. Simulate live preview request
                            manager._delegate_live_preview_request(88888)

                            # 2. Process the request
                            manager._handle_live_preview_request_safe(88888)

                            # Verify the complete workflow
                            # Request should be delegated correctly
                            assert manager.live_preview_request_flag is True

                            # Client rect should be queried (may be called multiple times due to initialization)
                            assert mock_get_rect.call_count >= 1

                            # Bitmap should be created with bypass_clipping=True
                            mock_create_bitmap.assert_called_once_with(
                                0,  # src_x
                                0,  # src_y
                                1200,  # client_width
                                900,  # client_height
                                1200,  # width (same as client)
                                900,  # height (same as client)
                                bypass_clipping=True,
                            )

                            # DWM should be called with correct parameters
                            mock_set_preview.assert_called_once_with(
                                88888, 5001, None, 0
                            )

                            # Bitmap should be cleaned up
                            mock_delete.assert_called_once_with(5001)
