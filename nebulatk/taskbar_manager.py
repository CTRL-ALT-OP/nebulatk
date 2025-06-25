import ctypes
from ctypes import wintypes
from comtypes import GUID, CoInitialize


# Windows API Constants
class WindowsConstants:
    """Windows API constants used throughout the TaskbarManager."""

    # Window messages
    WM_DWMSENDICONICTHUMBNAIL = 0x0323
    WM_DWMSENDICONICLIVEPREVIEWBITMAP = 0x0326
    WM_PAINT = 0x000F
    WM_SIZE = 0x0005
    WM_MOVE = 0x0003
    WM_SHOWWINDOW = 0x0018
    WM_ACTIVATEAPP = 0x001C
    WM_SETFOCUS = 0x0007
    WM_KILLFOCUS = 0x0008
    WM_COMMAND = 0x0111

    # DWM attributes
    DWMWA_FORCE_ICONIC_REPRESENTATION = 7
    DWMWA_HAS_ICONIC_BITMAP = 10
    DWMWA_DISALLOW_PEEK = 12

    # Progress states
    TBPF_NOPROGRESS = 0
    TBPF_NORMAL = 2

    # System icons
    IDI_WARNING = 32515
    IDI_ERROR = 32513
    IDI_INFORMATION = 32516

    # GDI constants
    SRCCOPY = 0x00CC0020
    HALFTONE = 4
    PW_CLIENTONLY = 1
    GA_ROOT = 2
    GWL_WNDPROC = -4

    # COM constants
    CLSCTX_INPROC_SERVER = 0x1
    DIB_RGB_COLORS = 0
    BI_RGB = 0

    # Safety limits
    MAX_DIMENSION = 32767
    MAX_COORD = 32767

    # GUIDs
    CLSID_TASKBAR_LIST = GUID("{56FDF344-FD6D-11D0-958A-006097C9A090}")
    IID_ITASKBAR_LIST3 = GUID("{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}")

    # Thumbnail toolbar button constants
    THBN_CLICKED = 0x1800

    # Thumbnail button flags
    THBF_ENABLED = 0x00000000
    THBF_DISABLED = 0x00000001
    THBF_DISMISSONCLICK = 0x00000002
    THBF_NOBACKGROUND = 0x00000004
    THBF_HIDDEN = 0x00000008
    THBF_NONINTERACTIVE = 0x00000010

    # Maximum number of buttons
    THBN_MAX_BUTTONS = 7

    # Media control button IDs
    THUMB_BUTTON_BACKWARD = 1001
    THUMB_BUTTON_PLAY_PAUSE = 1002
    THUMB_BUTTON_FORWARD = 1003
    THUMB_BUTTON_STOP = 1004


class WindowsAPISetup:
    """Helper class to set up Windows API function signatures."""

    @staticmethod
    def setup_gdi32_functions():
        """Set up GDI32 function signatures to prevent overflow errors."""
        gdi32 = ctypes.windll.gdi32

        gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
        gdi32.CreateCompatibleDC.restype = wintypes.HDC

        gdi32.CreateCompatibleBitmap.argtypes = [
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
        ]
        gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP

        gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        gdi32.SelectObject.restype = wintypes.HGDIOBJ

        gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        gdi32.DeleteObject.restype = wintypes.BOOL

        gdi32.DeleteDC.argtypes = [wintypes.HDC]
        gdi32.DeleteDC.restype = wintypes.BOOL

        gdi32.BitBlt.argtypes = [
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.DWORD,
        ]
        gdi32.BitBlt.restype = wintypes.BOOL

        gdi32.StretchBlt.argtypes = [
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.DWORD,
        ]
        gdi32.StretchBlt.restype = wintypes.BOOL

        gdi32.SetStretchBltMode.argtypes = [wintypes.HDC, ctypes.c_int]
        gdi32.SetStretchBltMode.restype = ctypes.c_int

    @staticmethod
    def setup_user32_functions():
        """Set up User32 function signatures."""
        user32 = ctypes.windll.user32

        user32.GetDC.argtypes = [wintypes.HWND]
        user32.GetDC.restype = wintypes.HDC

        user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
        user32.ReleaseDC.restype = ctypes.c_int

        user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetClientRect.restype = wintypes.BOOL

        user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
        user32.PrintWindow.restype = wintypes.BOOL

    @staticmethod
    def setup_window_proc_types():
        """Set up window procedure related types and functions."""
        user32 = ctypes.windll.user32

        # Set up compatibility for 32/64-bit
        if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_int64):
            LRESULT = ctypes.c_int64
            LONG_PTR = ctypes.c_int64
        else:
            LRESULT = ctypes.c_long
            LONG_PTR = ctypes.c_long

        user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
        user32.SetWindowLongPtrW.restype = LONG_PTR

        user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetWindowLongPtrW.restype = LONG_PTR

        user32.CallWindowProcW.argtypes = [
            LONG_PTR,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.CallWindowProcW.restype = LRESULT

        WNDPROCTYPE = ctypes.WINFUNCTYPE(
            LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
        )

        return LRESULT, LONG_PTR, WNDPROCTYPE


class COMInterfaceManager:
    """Manages COM interface creation and setup for ITaskbarList3."""

    def __init__(self):
        self.taskbar_interface = None
        self.vtbl = None

    def create_taskbar_interface(self):
        """Create and initialize the ITaskbarList3 COM interface."""
        # Define COM types
        HRESULT = ctypes.c_long
        PVOID = ctypes.c_void_p
        UINT = ctypes.c_uint

        # Define ITaskbarList3 interface structure
        ITaskbarList3, ITaskbarList3Vtbl = self._define_taskbar_interface()

        # Create the COM interface
        ole32 = ctypes.OleDLL("ole32")
        ole32.CoCreateInstance.argtypes = [
            ctypes.POINTER(GUID),
            PVOID,
            UINT,
            ctypes.POINTER(GUID),
            ctypes.POINTER(PVOID),
        ]
        ole32.CoCreateInstance.restype = HRESULT

        raw = PVOID()
        hr = ole32.CoCreateInstance(
            ctypes.byref(WindowsConstants.CLSID_TASKBAR_LIST),
            None,
            WindowsConstants.CLSCTX_INPROC_SERVER,
            ctypes.byref(WindowsConstants.IID_ITASKBAR_LIST3),
            ctypes.byref(raw),
        )

        if hr != 0:
            raise OSError(
                f"Failed to create taskbar interface: 0x{hr & 0xffffffff:08X}"
            )

        self.taskbar_interface = ctypes.cast(raw, ctypes.POINTER(ITaskbarList3))
        self.vtbl = self.taskbar_interface.contents.lpVtbl.contents

        # Initialize the interface
        hr = self.vtbl.HrInit(self.taskbar_interface)
        if hr != 0:
            raise OSError(f"Failed to initialize taskbar interface: 0x{hr:08X}")

    def _define_taskbar_interface(self):
        """Define the ITaskbarList3 interface structure."""
        HRESULT = ctypes.c_long
        PVOID = ctypes.c_void_p
        UINT = ctypes.c_uint

        class ITaskbarList3(ctypes.Structure):
            pass

        class ITaskbarList3Vtbl(ctypes.Structure):
            _fields_ = [
                (
                    "QueryInterface",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        ctypes.POINTER(GUID),
                        ctypes.POINTER(PVOID),
                    ),
                ),
                (
                    "AddRef",
                    ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.POINTER(ITaskbarList3)),
                ),
                (
                    "Release",
                    ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.POINTER(ITaskbarList3)),
                ),
                ("HrInit", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(ITaskbarList3))),
                (
                    "AddTab",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND
                    ),
                ),
                (
                    "DeleteTab",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND
                    ),
                ),
                (
                    "ActivateTab",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND
                    ),
                ),
                (
                    "SetActiveAlt",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND
                    ),
                ),
                (
                    "MarkFullscreenWindow",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        ctypes.c_int,
                    ),
                ),
                (
                    "SetProgressValue",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        ctypes.c_ulonglong,
                        ctypes.c_ulonglong,
                    ),
                ),
                (
                    "SetProgressState",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        ctypes.c_int,
                    ),
                ),
                (
                    "RegisterTab",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        wintypes.HWND,
                    ),
                ),
                (
                    "UnregisterTab",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND
                    ),
                ),
                (
                    "SetTabOrder",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        wintypes.HWND,
                    ),
                ),
                (
                    "SetTabActive",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        wintypes.HWND,
                        UINT,
                    ),
                ),
                (
                    "ThumbBarAddButtons",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        UINT,
                        PVOID,
                    ),
                ),
                (
                    "ThumbBarUpdateButtons",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        UINT,
                        PVOID,
                    ),
                ),
                (
                    "ThumbBarSetImageList",
                    ctypes.WINFUNCTYPE(
                        HRESULT, ctypes.POINTER(ITaskbarList3), wintypes.HWND, PVOID
                    ),
                ),
                (
                    "SetOverlayIcon",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        PVOID,
                        wintypes.LPWSTR,
                    ),
                ),
                (
                    "SetThumbnailToolTip",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        wintypes.LPWSTR,
                    ),
                ),
                (
                    "SetThumbnailClip",
                    ctypes.WINFUNCTYPE(
                        HRESULT,
                        ctypes.POINTER(ITaskbarList3),
                        wintypes.HWND,
                        ctypes.POINTER(wintypes.RECT),
                    ),
                ),
            ]

        ITaskbarList3._fields_ = [("lpVtbl", ctypes.POINTER(ITaskbarList3Vtbl))]
        return ITaskbarList3, ITaskbarList3Vtbl


class ValidationHelper:
    """Helper class for validating dimensions and coordinates."""

    @staticmethod
    def validate_dimensions(width, height, name="dimension"):
        """Validate and clamp dimensions to prevent integer overflow."""
        # Ensure positive values
        width = max(1, int(width))
        height = max(1, int(height))

        # Clamp to maximum safe values
        if (
            width > WindowsConstants.MAX_DIMENSION
            or height > WindowsConstants.MAX_DIMENSION
        ):
            print(
                f"⚠️  Large {name} detected: {width}x{height}, clamping to safe values"
            )
            width = min(width, WindowsConstants.MAX_DIMENSION)
            height = min(height, WindowsConstants.MAX_DIMENSION)

        return width, height

    @staticmethod
    def validate_coordinates(x, y, max_x=None, max_y=None):
        """Validate and clamp coordinates to prevent integer overflow."""
        # Ensure non-negative values
        x = max(0, int(x))
        y = max(0, int(y))

        # Apply maximum bounds if specified
        if max_x is not None:
            x = min(x, int(max_x))
        if max_y is not None:
            y = min(y, int(max_y))

        # Clamp to absolute maximum safe values
        x = min(x, WindowsConstants.MAX_COORD)
        y = min(y, WindowsConstants.MAX_COORD)

        return x, y


class THUMBBUTTON(ctypes.Structure):
    """Structure for defining thumbnail toolbar buttons."""

    _fields_ = [
        ("dwMask", ctypes.c_uint),
        ("iId", ctypes.c_uint),
        ("iBitmap", ctypes.c_uint),
        ("hIcon", wintypes.HICON),
        ("szTip", ctypes.c_wchar * 260),
        ("dwFlags", ctypes.c_uint),
    ]

    # Mask values
    THB_BITMAP = 0x1
    THB_ICON = 0x2
    THB_TOOLTIP = 0x4
    THB_FLAGS = 0x8


class ThumbnailToolbarManager:
    """Helper class for managing thumbnail toolbar buttons."""

    def __init__(self, taskbar_manager):
        self.taskbar_manager = taskbar_manager
        self.buttons = []
        self.button_callbacks = {}
        self.is_playing = False  # Track play/pause state
        self.button_icons = {}  # Store loaded icons for cleanup

    def create_media_buttons(self, callbacks=None, custom_icons=None):
        """
        Create standard media control buttons (backward, play/pause, forward, stop).

        Args:
            callbacks (dict, optional): Dictionary mapping button IDs to callback functions
            custom_icons (dict, optional): Dictionary mapping button names to icon sources.
        """
        pass

    def _load_button_icons(self, custom_icons):
        pass

    def _load_custom_icon(self, icon_source, icon_name):
        return None

    def _load_icon_from_file(self, file_path):
        return None

    def _bitmap_to_icon(self, hbitmap):
        return None

    def _load_system_icon(self, dll_name, icon_index):
        return None

    def _add_buttons_to_taskbar(self):
        pass

    def update_play_pause_button(self, is_playing=None):
        pass

    def set_button_enabled(self, button_id, enabled=True):
        pass

    def handle_button_click(self, button_id):
        pass

    def update_button_icon(self, button_id, icon_source):
        pass

    def cleanup_resources(self):
        pass

    def __del__(self):
        pass


class BitmapCreator:
    """Helper class for creating thumbnails and live preview bitmaps."""

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._setup_api_functions()

    def _setup_api_functions(self):
        """Set up all required API function signatures."""
        WindowsAPISetup.setup_gdi32_functions()
        WindowsAPISetup.setup_user32_functions()

    def create_thumbnail_bitmap(
        self,
        src_x,
        src_y,
        src_width,
        src_height,
        thumb_width,
        thumb_height,
        bypass_clipping=False,
        clip_rect=None,
    ):
        """Create a thumbnail bitmap from window content."""
        try:
            # Get window dimensions
            client_rect = self._get_client_rect()
            if not client_rect:
                return None

            client_width, client_height = client_rect

            # Determine source rectangle
            source_rect = self._calculate_source_rect(
                client_width,
                client_height,
                src_x,
                src_y,
                src_width,
                src_height,
                clip_rect,
                bypass_clipping,
            )

            if not source_rect:
                return None

            src_x, src_y, src_width, src_height = source_rect

            # Calculate final dimensions preserving aspect ratio
            final_width, final_height = self._calculate_final_dimensions(
                src_width, src_height, thumb_width, thumb_height
            )

            # Create device contexts
            contexts = self._create_device_contexts()
            if not contexts:
                return None

            hdc_screen, hdc_window, hdc_mem_source, hdc_mem_thumb = contexts

            try:
                # Capture window content
                hbitmap_source = self._capture_window_content(
                    hdc_screen,
                    hdc_mem_source,
                    hdc_window,
                    client_width,
                    client_height,
                    src_x,
                    src_y,
                    src_width,
                    src_height,
                    clip_rect,
                    bypass_clipping,
                )

                if not hbitmap_source:
                    return None

                try:
                    # Create final thumbnail bitmap
                    hbitmap_thumb = self._create_final_bitmap(
                        hdc_screen,
                        hdc_mem_source,
                        hdc_mem_thumb,
                        src_width,
                        src_height,
                        final_width,
                        final_height,
                    )

                    return hbitmap_thumb

                finally:
                    ctypes.windll.gdi32.DeleteObject(hbitmap_source)

            finally:
                self._cleanup_device_contexts(contexts)

        except Exception as e:
            print(f"Error creating bitmap: {e}")
            return None

    def _get_client_rect(self):
        """Get the client rectangle dimensions."""
        user32 = ctypes.windll.user32
        client_rect = wintypes.RECT()

        if not user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
            return None

        client_width = client_rect.right - client_rect.left
        client_height = client_rect.bottom - client_rect.top

        if client_width <= 0 or client_height <= 0:
            return None

        # Clamp to safe dimensions
        client_width = min(client_width, WindowsConstants.MAX_DIMENSION)
        client_height = min(client_height, WindowsConstants.MAX_DIMENSION)

        return client_width, client_height

    def _calculate_source_rect(
        self,
        client_width,
        client_height,
        src_x,
        src_y,
        src_width,
        src_height,
        clip_rect,
        bypass_clipping,
    ):
        """Calculate the source rectangle for capturing."""
        if clip_rect and not bypass_clipping:
            # Use clipping rectangle
            src_x = max(0, min(clip_rect.left, client_width))
            src_y = max(0, min(clip_rect.top, client_height))
            src_width = max(
                1, min(clip_rect.right - clip_rect.left, client_width - src_x)
            )
            src_height = max(
                1, min(clip_rect.bottom - clip_rect.top, client_height - src_y)
            )
        else:
            # Use entire client area
            src_x = 0
            src_y = 0
            src_width = client_width
            src_height = client_height

        # Ensure all dimensions are within safe bounds
        src_width = max(1, min(src_width, WindowsConstants.MAX_DIMENSION))
        src_height = max(1, min(src_height, WindowsConstants.MAX_DIMENSION))

        return src_x, src_y, src_width, src_height

    def _calculate_final_dimensions(self, src_width, src_height, max_width, max_height):
        """Calculate aspect-ratio preserving dimensions."""
        if src_width <= max_width and src_height <= max_height:
            return src_width, src_height

        # Scale down to fit within bounds while preserving aspect ratio
        scale_x = max_width / src_width
        scale_y = max_height / src_height
        scale = min(scale_x, scale_y)

        final_width = int(src_width * scale)
        final_height = int(src_height * scale)

        return final_width, final_height

    def _create_device_contexts(self):
        """Create all required device contexts."""
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        hdc_screen = user32.GetDC(None)
        hdc_window = user32.GetDC(self.hwnd)
        hdc_mem_source = gdi32.CreateCompatibleDC(hdc_screen)
        hdc_mem_thumb = gdi32.CreateCompatibleDC(hdc_screen)

        if not all([hdc_screen, hdc_window, hdc_mem_source, hdc_mem_thumb]):
            self._cleanup_device_contexts(
                (hdc_screen, hdc_window, hdc_mem_source, hdc_mem_thumb)
            )
            return None

        return hdc_screen, hdc_window, hdc_mem_source, hdc_mem_thumb

    def _cleanup_device_contexts(self, contexts):
        """Clean up device contexts."""
        hdc_screen, hdc_window, hdc_mem_source, hdc_mem_thumb = contexts
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        if hdc_mem_source:
            gdi32.DeleteDC(hdc_mem_source)
        if hdc_mem_thumb:
            gdi32.DeleteDC(hdc_mem_thumb)
        if hdc_screen:
            user32.ReleaseDC(None, hdc_screen)
        if hdc_window:
            user32.ReleaseDC(self.hwnd, hdc_window)

    def _capture_window_content(
        self,
        hdc_screen,
        hdc_mem_source,
        hdc_window,
        client_width,
        client_height,
        src_x,
        src_y,
        src_width,
        src_height,
        clip_rect,
        bypass_clipping,
    ):
        """Capture window content into a bitmap."""
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32

        if clip_rect and not bypass_clipping:
            # Clipping mode: capture full window then extract region
            return self._capture_with_clipping(
                hdc_screen,
                hdc_mem_source,
                hdc_window,
                client_width,
                client_height,
                src_x,
                src_y,
                src_width,
                src_height,
            )
        else:
            # Direct capture mode
            return self._capture_direct(
                hdc_screen,
                hdc_mem_source,
                hdc_window,
                src_width,
                src_height,
                src_x,
                src_y,
            )

    def _capture_with_clipping(
        self,
        hdc_screen,
        hdc_mem_source,
        hdc_window,
        client_width,
        client_height,
        src_x,
        src_y,
        src_width,
        src_height,
    ):
        """Capture with clipping support."""
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32

        # Create full window bitmap
        hbitmap_full = gdi32.CreateCompatibleBitmap(
            hdc_screen, ctypes.c_int(client_width), ctypes.c_int(client_height)
        )
        if not hbitmap_full:
            return None

        hdc_temp = gdi32.CreateCompatibleDC(hdc_screen)
        if not hdc_temp:
            gdi32.DeleteObject(hbitmap_full)
            return None

        old_bitmap_temp = gdi32.SelectObject(hdc_temp, hbitmap_full)

        # Capture full window
        success = user32.PrintWindow(
            self.hwnd, hdc_temp, WindowsConstants.PW_CLIENTONLY
        )
        if not success:
            success = gdi32.BitBlt(
                hdc_temp,
                0,
                0,
                client_width,
                client_height,
                hdc_window,
                0,
                0,
                WindowsConstants.SRCCOPY,
            )

        if success:
            # Create clipped bitmap
            hbitmap_source = gdi32.CreateCompatibleBitmap(
                hdc_screen, ctypes.c_int(src_width), ctypes.c_int(src_height)
            )
            if hbitmap_source:
                old_bitmap_source = gdi32.SelectObject(hdc_mem_source, hbitmap_source)

                # Copy clipped region
                success = gdi32.BitBlt(
                    hdc_mem_source,
                    0,
                    0,
                    src_width,
                    src_height,
                    hdc_temp,
                    src_x,
                    src_y,
                    WindowsConstants.SRCCOPY,
                )

                if not success:
                    gdi32.SelectObject(hdc_mem_source, old_bitmap_source)
                    gdi32.DeleteObject(hbitmap_source)
                    hbitmap_source = None
            else:
                success = False
        else:
            hbitmap_source = None

        # Cleanup
        gdi32.SelectObject(hdc_temp, old_bitmap_temp)
        gdi32.DeleteObject(hbitmap_full)
        gdi32.DeleteDC(hdc_temp)

        return hbitmap_source if success else None

    def _capture_direct(
        self,
        hdc_screen,
        hdc_mem_source,
        hdc_window,
        src_width,
        src_height,
        src_x,
        src_y,
    ):
        """Direct capture without clipping."""
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32

        hbitmap_source = gdi32.CreateCompatibleBitmap(
            hdc_screen, ctypes.c_int(src_width), ctypes.c_int(src_height)
        )
        if not hbitmap_source:
            return None

        old_bitmap_source = gdi32.SelectObject(hdc_mem_source, hbitmap_source)

        # Capture window content
        success = user32.PrintWindow(
            self.hwnd, hdc_mem_source, WindowsConstants.PW_CLIENTONLY
        )
        if not success:
            success = gdi32.BitBlt(
                hdc_mem_source,
                0,
                0,
                src_width,
                src_height,
                hdc_window,
                src_x,
                src_y,
                WindowsConstants.SRCCOPY,
            )

        if not success:
            gdi32.SelectObject(hdc_mem_source, old_bitmap_source)
            gdi32.DeleteObject(hbitmap_source)
            return None

        return hbitmap_source

    def _create_final_bitmap(
        self,
        hdc_screen,
        hdc_mem_source,
        hdc_mem_thumb,
        src_width,
        src_height,
        final_width,
        final_height,
    ):
        """Create the final scaled bitmap."""
        gdi32 = ctypes.windll.gdi32

        # Create 32-bit DIB bitmap
        bmi = self._create_bitmap_info(final_width, final_height)
        bits = ctypes.c_void_p()

        # Set up CreateDIBSection function signature with the proper BITMAPINFO type
        BITMAPINFO = type(bmi)
        gdi32.CreateDIBSection.argtypes = [
            wintypes.HDC,
            ctypes.POINTER(BITMAPINFO),
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_void_p),
            wintypes.HANDLE,
            ctypes.c_uint,
        ]
        gdi32.CreateDIBSection.restype = wintypes.HBITMAP

        hbitmap_thumb = gdi32.CreateDIBSection(
            hdc_screen,
            ctypes.byref(bmi),
            WindowsConstants.DIB_RGB_COLORS,
            ctypes.byref(bits),
            None,
            0,
        )

        if not hbitmap_thumb:
            return None

        old_bitmap_thumb = gdi32.SelectObject(hdc_mem_thumb, hbitmap_thumb)

        # Scale the content
        if final_width == src_width and final_height == src_height:
            # Direct copy
            success = gdi32.BitBlt(
                hdc_mem_thumb,
                0,
                0,
                final_width,
                final_height,
                hdc_mem_source,
                0,
                0,
                WindowsConstants.SRCCOPY,
            )
        else:
            # Scale with high quality
            gdi32.SetStretchBltMode(hdc_mem_thumb, WindowsConstants.HALFTONE)
            success = gdi32.StretchBlt(
                hdc_mem_thumb,
                0,
                0,
                final_width,
                final_height,
                hdc_mem_source,
                0,
                0,
                src_width,
                src_height,
                WindowsConstants.SRCCOPY,
            )

        gdi32.SelectObject(hdc_mem_thumb, old_bitmap_thumb)

        if not success:
            gdi32.DeleteObject(hbitmap_thumb)
            return None

        return hbitmap_thumb

    def _create_bitmap_info(self, width, height):
        """Create BITMAPINFO structure for DIB creation."""

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", ctypes.c_uint32),
                ("biWidth", ctypes.c_int32),
                ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16),
                ("biBitCount", ctypes.c_uint16),
                ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32),
                ("biXPelsPerMeter", ctypes.c_int32),
                ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32),
                ("biClrImportant", ctypes.c_uint32),
            ]

        class BITMAPINFO(ctypes.Structure):
            _fields_ = [
                ("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", ctypes.c_uint32 * 3),
            ]

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = ctypes.c_int32(width)
        bmi.bmiHeader.biHeight = ctypes.c_int32(-height)  # Negative for top-down DIB
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32  # Must be 32-bit for Windows thumbnails
        bmi.bmiHeader.biCompression = WindowsConstants.BI_RGB
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0

        return bmi


class TaskbarManager:
    """Manages Windows taskbar features for a Tkinter application."""

    def __init__(self, root):
        """Initialize the taskbar manager for the given Tkinter root window."""
        self.window = root  # Store the nebulatk window object
        self.root = None  # Will be set safely later
        self.hwnd = None

        # COM interface manager
        self.com_manager = COMInterfaceManager()

        # Window procedure handling
        self.old_wndproc = None
        self.new_wndproc = None

        # Taskbar state
        self.clip_rect = None
        self.taskbar_button_created = False
        self.custom_thumbnails_initialized = False
        self.auto_invalidate_enabled = True
        self.debounce_delay = 50  # 50ms debounce delay

        # Thread-safe delegation system
        self.thumbnail_request_flag = False
        self.thumbnail_width = 0
        self.thumbnail_height = 0
        self.live_preview_request_flag = False
        self.polling_active = False

        # Debouncing timers
        self.thumbnail_pending_timer = None
        self.live_preview_pending_timer = None

        # Thumbnail toolbar manager
        self.toolbar_manager = None
        self._pending_button_callbacks = None
        self._pending_custom_icons = None

        # Initialize
        self._initialize()

    def _initialize(self):
        """Initialize all components of the taskbar manager."""
        # Initialize COM
        CoInitialize()

        # Set up Windows API function signatures
        WindowsAPISetup.setup_gdi32_functions()
        WindowsAPISetup.setup_user32_functions()

        # Set up components
        self._setup_window()
        self._setup_taskbar_interface()
        self._setup_window_hook()
        self.manual_apply()

    def _setup_window(self):
        """Set up the window handle and ensure it appears in taskbar."""

        def setup_window_safe():
            self.root = self.window.root
            self.root.wm_attributes("-toolwindow", False)
            self.root.lift()
            self.root.update()

            # Get the correct window handle
            child_hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            self.hwnd = user32.GetAncestor(child_hwnd, WindowsConstants.GA_ROOT)
            if self.hwnd == 0:
                self.hwnd = child_hwnd

        self._schedule_safe_tkinter_call(setup_window_safe)

    def _schedule_safe_tkinter_call(self, func):
        """Schedule a function to be called safely on the tkinter main thread."""
        try:
            if self.window.root is not None:
                func()
                if not self.polling_active:
                    self._start_polling()
            else:
                import time

                while self.window.root is None:
                    time.sleep(0.01)
                func()
                if not self.polling_active:
                    self._start_polling()
        except Exception as e:
            print(f"Error in safe tkinter call: {e}")

    def _setup_taskbar_interface(self):
        """Set up the ITaskbarList3 COM interface."""
        self.com_manager.create_taskbar_interface()
        # Expose the interface and vtbl for direct access
        self.taskbar_interface = self.com_manager.taskbar_interface
        self.vtbl = self.com_manager.vtbl

        # Initialize bitmap creator
        self.bitmap_creator = None

    def _initialize_bitmap_creator(self):
        """Initialize the bitmap creator once we have a window handle."""
        if self.hwnd and not self.bitmap_creator:
            self.bitmap_creator = BitmapCreator(self.hwnd)

    def _handle_thumbnail_request_safe(self, hwnd, width, height):
        """Handle thumbnail generation request on main thread (thread-safe)."""
        # Validate thumbnail dimensions
        width, height = ValidationHelper.validate_dimensions(
            width, height, "thumbnail request"
        )

        try:
            self._initialize_bitmap_creator()

            if self.clip_rect:
                bitmap = self._create_clipped_thumbnail(width, height)
            else:
                bitmap = self._create_full_thumbnail(width, height)

            if bitmap:
                dwmapi = ctypes.windll.dwmapi
                dwmapi.DwmSetIconicThumbnail.argtypes = [
                    wintypes.HWND,
                    wintypes.HBITMAP,
                    ctypes.c_int,
                ]
                dwmapi.DwmSetIconicThumbnail.restype = ctypes.c_long
                hr = dwmapi.DwmSetIconicThumbnail(hwnd, bitmap, 0)

                ctypes.windll.gdi32.DeleteObject(bitmap)
        except Exception as e:
            print(f"❌ Error creating thumbnail: {e}")

    def _create_full_thumbnail(self, width, height):
        """Create thumbnail of the full window."""
        return self.bitmap_creator.create_thumbnail_bitmap(
            0, 0, None, None, width, height, bypass_clipping=True
        )

    def _create_clipped_thumbnail(self, width, height):
        """Create thumbnail of the clipped region."""
        if not self.clip_rect:
            return self._create_full_thumbnail(width, height)

        return self.bitmap_creator.create_thumbnail_bitmap(
            self.clip_rect.left,
            self.clip_rect.top,
            self.clip_rect.right - self.clip_rect.left,
            self.clip_rect.bottom - self.clip_rect.top,
            width,
            height,
            clip_rect=self.clip_rect,
        )

    def _handle_live_preview_request_safe(self, hwnd):
        """Handle live preview request on main thread (thread-safe)."""
        try:
            self._initialize_bitmap_creator()

            user32 = ctypes.windll.user32
            client_rect = wintypes.RECT()
            user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))

            client_width = client_rect.right - client_rect.left
            client_height = client_rect.bottom - client_rect.top

            if client_width <= 0 or client_height <= 0:
                return

            bitmap = self._create_live_preview_bitmap(client_width, client_height)

            if bitmap:
                dwmapi = ctypes.windll.dwmapi
                dwmapi.DwmSetIconicLivePreviewBitmap.argtypes = [
                    wintypes.HWND,
                    wintypes.HBITMAP,
                    ctypes.POINTER(wintypes.POINT),
                    ctypes.c_int,
                ]
                dwmapi.DwmSetIconicLivePreviewBitmap.restype = ctypes.c_long

                hr = dwmapi.DwmSetIconicLivePreviewBitmap(hwnd, bitmap, None, 0)
                ctypes.windll.gdi32.DeleteObject(bitmap)
            else:
                print("❌ Failed to create live preview bitmap")
        except Exception as e:
            print(f"❌ Error creating live preview: {e}")

    def _create_live_preview_bitmap(self, width, height):
        """Create a live preview bitmap of the entire window (ignores clipping)."""
        width, height = ValidationHelper.validate_dimensions(
            width, height, "live preview"
        )

        # Live previews always show full window content
        return self.bitmap_creator.create_thumbnail_bitmap(
            0, 0, width, height, width, height, bypass_clipping=True
        )

    # Public API methods
    def SetThumbnailClip(self, x, y, width, height):
        """Set the thumbnail clipping rectangle."""
        # Initialize custom thumbnails on first call
        if not self.custom_thumbnails_initialized:
            self._initialize_custom_thumbnails()

        # Validate and clamp all values
        x, y = ValidationHelper.validate_coordinates(x, y)
        width, height = ValidationHelper.validate_dimensions(
            width, height, "clip region"
        )

        # Create RECT structure
        self.clip_rect = wintypes.RECT(x, y, x + width, y + height)

        # Invalidate thumbnails to trigger refresh
        if self.taskbar_button_created:
            self._invalidate_thumbnails()

    def ClearThumbnailClip(self):
        """Clear the thumbnail clipping rectangle to show the full window."""
        # Initialize custom thumbnails on first call if not already done
        if not self.custom_thumbnails_initialized:
            self._initialize_custom_thumbnails()

        self.clip_rect = None

        if self.taskbar_button_created:
            self._invalidate_thumbnails()

    def SetThumbnailNotification(self, icon_type="warning"):
        """Set the overlay icon on the taskbar button."""
        user32 = ctypes.windll.user32

        if icon_type is None:
            hicon = None
            description = ""
        else:
            icon_map = {
                "warning": WindowsConstants.IDI_WARNING,
                "error": WindowsConstants.IDI_ERROR,
                "info": WindowsConstants.IDI_INFORMATION,
            }
            icon_id = icon_map.get(icon_type, WindowsConstants.IDI_WARNING)
            hicon = user32.LoadIconW(None, ctypes.cast(icon_id, wintypes.LPCWSTR))
            description = f"{icon_type.capitalize()} Icon"

        hr = self.vtbl.SetOverlayIcon(
            self.taskbar_interface, self.hwnd, hicon, description
        )
        return hr == 0

    def SetProgress(self, progress):
        """Set the progress bar value on the taskbar button."""
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")

        # Set progress state
        if progress == 0:
            state = WindowsConstants.TBPF_NOPROGRESS
        else:
            state = WindowsConstants.TBPF_NORMAL

        hr1 = self.vtbl.SetProgressState(self.taskbar_interface, self.hwnd, state)

        if progress > 0:
            hr2 = self.vtbl.SetProgressValue(
                self.taskbar_interface, self.hwnd, progress, 100
            )
            return hr1 == 0 and hr2 == 0

        return hr1 == 0

    def InvalidateLivePreview(self):
        """Invalidate the live preview to force Windows to request a new one."""
        if self.taskbar_button_created and self.custom_thumbnails_initialized:
            self._invalidate_thumbnails()

    def _invalidate_thumbnails(self):
        """Helper method to invalidate thumbnails."""
        dwmapi = ctypes.windll.dwmapi
        dwmapi.DwmInvalidateIconicBitmaps.argtypes = [wintypes.HWND]
        dwmapi.DwmInvalidateIconicBitmaps.restype = ctypes.c_long
        dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)

    # Configuration methods
    def SetAutoInvalidation(self, enabled=True):
        """Enable or disable automatic thumbnail and live preview invalidation."""
        self.auto_invalidate_enabled = enabled
        print(f"🔄 Auto-invalidation {'enabled' if enabled else 'disabled'}")

    def IsAutoInvalidationEnabled(self):
        """Check if automatic invalidation is currently enabled."""
        return self.auto_invalidate_enabled

    def SetDebounceDelay(self, delay_ms):
        """Set the debounce delay for thumbnail and live preview requests."""
        if delay_ms < 10:
            print("⚠️  Warning: Debounce delay below 10ms may cause performance issues")
        elif delay_ms > 1000:
            print("⚠️  Warning: Debounce delay above 1000ms may feel unresponsive")

        self.debounce_delay = max(10, int(delay_ms))
        print(f"🕐 Debounce delay set to {self.debounce_delay}ms")
        return self

    def GetDebounceDelay(self):
        """Get the current debounce delay in milliseconds."""
        return self.debounce_delay

    def _setup_window_hook(self):
        """Set up window message hook to handle taskbar messages."""
        LRESULT, LONG_PTR, WNDPROCTYPE = WindowsAPISetup.setup_window_proc_types()

        user32 = ctypes.windll.user32
        TaskbarButtonCreated = user32.RegisterWindowMessageW("TaskbarButtonCreated")

        # Get the old window procedure
        self.old_wndproc = user32.GetWindowLongPtrW(
            self.hwnd, WindowsConstants.GWL_WNDPROC
        )

        # Create window procedure
        @WNDPROCTYPE
        def window_proc(hwnd, msg, wparam, lparam):
            return self._handle_window_message(
                hwnd, msg, wparam, lparam, TaskbarButtonCreated, LONG_PTR
            )

        # Store reference and install hook
        self.new_wndproc = window_proc
        func_ptr = LONG_PTR(ctypes.cast(window_proc, ctypes.c_void_p).value)
        user32.SetWindowLongPtrW(self.hwnd, WindowsConstants.GWL_WNDPROC, func_ptr)

    def _handle_window_message(
        self, hwnd, msg, wparam, lparam, TaskbarButtonCreated, LONG_PTR
    ):
        """Handle window messages for taskbar integration."""
        user32 = ctypes.windll.user32

        if msg == TaskbarButtonCreated:
            self._on_taskbar_button_created()
        elif msg == WindowsConstants.WM_COMMAND:
            # Handle thumbnail toolbar button clicks
            button_id = wparam & 0xFFFF
            if self.toolbar_manager and button_id in [
                WindowsConstants.THUMB_BUTTON_BACKWARD,
                WindowsConstants.THUMB_BUTTON_PLAY_PAUSE,
                WindowsConstants.THUMB_BUTTON_FORWARD,
                WindowsConstants.THUMB_BUTTON_STOP,
            ]:
                self.toolbar_manager.handle_button_click(button_id)
                return 0
        elif (
            msg == WindowsConstants.WM_DWMSENDICONICTHUMBNAIL
            and self.custom_thumbnails_initialized
        ):
            height = lparam & 0xFFFF
            width = (lparam >> 16) & 0xFFFF
            self._delegate_thumbnail_request(hwnd, width, height)
            return 0
        elif (
            msg == WindowsConstants.WM_DWMSENDICONICLIVEPREVIEWBITMAP
            and self.custom_thumbnails_initialized
        ):
            self._delegate_live_preview_request(hwnd)
            return 0
        elif msg in self._get_auto_invalidate_messages():
            if self.auto_invalidate_enabled and self.custom_thumbnails_initialized:
                self._auto_invalidate_thumbnails()

        return user32.CallWindowProcW(
            LONG_PTR(self.old_wndproc), hwnd, msg, wparam, lparam
        )

    def _get_auto_invalidate_messages(self):
        """Get the set of window messages that should trigger auto-invalidation."""
        return {
            WindowsConstants.WM_PAINT,
            WindowsConstants.WM_SIZE,
            WindowsConstants.WM_MOVE,
            WindowsConstants.WM_SHOWWINDOW,
            WindowsConstants.WM_ACTIVATEAPP,
            WindowsConstants.WM_SETFOCUS,
            WindowsConstants.WM_KILLFOCUS,
        }

    def _on_taskbar_button_created(self):
        """Handle taskbar button creation."""
        self._apply_taskbar_features()

    def _apply_taskbar_features(self):
        """Apply basic taskbar features (custom thumbnails only initialized when SetThumbnailClip is called)."""
        self.taskbar_button_created = True

        # Add pending button callbacks if any were requested before taskbar button was ready - BROKEN: Don't apply them
        # if (
        #     self._pending_button_callbacks is not None
        #     or self._pending_custom_icons is not None
        # ):
        #     self.AddMediaControlButtons(
        #         self._pending_button_callbacks, self._pending_custom_icons
        #     )
        #     self._pending_button_callbacks = None
        #     self._pending_custom_icons = None

    def _setup_custom_thumbnails(self):
        """Set up the window for custom thumbnails and live previews."""
        dwmapi = ctypes.windll.dwmapi

        # Enable custom thumbnails
        force_iconic = ctypes.c_int(1)
        has_iconic = ctypes.c_int(1)
        disallow_peek = ctypes.c_int(0)  # 0 = allow peek

        hr1 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            WindowsConstants.DWMWA_FORCE_ICONIC_REPRESENTATION,
            ctypes.byref(force_iconic),
            ctypes.sizeof(force_iconic),
        )

        hr2 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            WindowsConstants.DWMWA_HAS_ICONIC_BITMAP,
            ctypes.byref(has_iconic),
            ctypes.sizeof(has_iconic),
        )

        hr3 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            WindowsConstants.DWMWA_DISALLOW_PEEK,
            ctypes.byref(disallow_peek),
            ctypes.sizeof(disallow_peek),
        )

        return hr1 == 0 and hr2 == 0 and hr3 == 0

    def _set_thumbnail_tooltip(self, text):
        """Set a custom tooltip for the taskbar thumbnail."""
        hr = self.vtbl.SetThumbnailToolTip(self.taskbar_interface, self.hwnd, text)
        return hr == 0

    def _initialize_custom_thumbnails(self):
        """Initialize custom thumbnail functionality (only called when SetThumbnailClip is used)."""
        if self.custom_thumbnails_initialized:
            return

        self._setup_custom_thumbnails()
        self._set_thumbnail_tooltip("TaskbarManager Demo")

        # Invalidate to trigger thumbnail request
        if self.taskbar_button_created:
            self._invalidate_thumbnails()

        self.custom_thumbnails_initialized = True

    def manual_apply(self):
        """Manually apply taskbar features (for testing/debugging)."""
        if not self.taskbar_button_created:
            self._apply_taskbar_features()
        # Note: Custom thumbnails are only initialized when SetThumbnailClip is called

    # Delegation and polling methods
    def _delegate_thumbnail_request(self, hwnd, width, height):
        """Safely delegate thumbnail request using flags."""
        self.thumbnail_width = width
        self.thumbnail_height = height
        self.thumbnail_request_flag = True

    def _delegate_live_preview_request(self, hwnd):
        """Safely delegate live preview request using flags."""
        self.live_preview_request_flag = True

    def _start_polling(self):
        """Start polling for requests."""
        self.polling_active = True
        self._poll_for_requests()

    def _poll_for_requests(self):
        """Poll for requests and process them with proper debouncing."""
        if not self.polling_active:
            return

        try:
            if self.thumbnail_request_flag:
                self._schedule_debounced_thumbnail()
                self.thumbnail_request_flag = False

            if self.live_preview_request_flag:
                self._schedule_debounced_live_preview()
                self.live_preview_request_flag = False

        except Exception as e:
            print(f"❌ Error in polling: {e}")

        if self.root is not None:
            self.root.after(10, self._poll_for_requests)

    def _schedule_debounced_thumbnail(self):
        """Schedule thumbnail processing with debouncing."""
        if self.thumbnail_pending_timer is not None:
            self.root.after_cancel(self.thumbnail_pending_timer)

        self.thumbnail_pending_timer = self.root.after(
            self.debounce_delay, self._process_debounced_thumbnail
        )

    def _schedule_debounced_live_preview(self):
        """Schedule live preview processing with debouncing."""
        if self.live_preview_pending_timer is not None:
            self.root.after_cancel(self.live_preview_pending_timer)

        self.live_preview_pending_timer = self.root.after(
            self.debounce_delay, self._process_debounced_live_preview
        )

    def _process_debounced_thumbnail(self):
        """Process thumbnail request after debounce delay."""
        try:
            self._handle_thumbnail_request_safe(
                self.hwnd, self.thumbnail_width, self.thumbnail_height
            )
            self.thumbnail_pending_timer = None
        except Exception as e:
            print(f"❌ Error processing debounced thumbnail: {e}")

    def _process_debounced_live_preview(self):
        """Process live preview request after debounce delay."""
        try:
            self._handle_live_preview_request_safe(self.hwnd)
            self.live_preview_pending_timer = None
        except Exception as e:
            print(f"❌ Error processing debounced live preview: {e}")

    # Auto-invalidation methods
    def _auto_invalidate_thumbnails(self):
        """Automatically invalidate thumbnails and live previews when window updates."""
        if not self.taskbar_button_created or not self.custom_thumbnails_initialized:
            return

        def schedule_invalidation():
            if hasattr(self, "_invalidate_pending"):
                self.root.after_cancel(self._invalidate_pending)

            self._invalidate_pending = self.root.after(
                self.debounce_delay, self._perform_invalidation
            )

        try:
            if self.root is not None:
                schedule_invalidation()
        except Exception as e:
            print(f"Error scheduling invalidation: {e}")

    def _perform_invalidation(self):
        """Perform the actual thumbnail and live preview invalidation."""
        if self.taskbar_button_created:
            self._invalidate_thumbnails()

        if hasattr(self, "_invalidate_pending"):
            delattr(self, "_invalidate_pending")

    # Thumbnail toolbar button methods
    def AddMediaControlButtons(self, callbacks=None, custom_icons=None):
        pass

    def UpdatePlayPauseButton(self, is_playing):
        pass

    def SetButtonEnabled(self, button_id, enabled=True):
        pass

    def UpdateButtonIcon(self, button_id, icon_source):
        pass

    def GetAvailableSystemIcons(self):
        pass

    def GetButtonConstants(self):
        pass
