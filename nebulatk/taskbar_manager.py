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
                                         Can be file paths, system icon specs, or HICON handles.

                                         Example:
                                         {
                                             'backward': 'path/to/prev.ico',
                                             'play': ('shell32.dll', 16),  # DLL and index
                                             'pause': hicon_handle,        # Direct HICON
                                             'forward': 'path/to/next.png',
                                             'stop': 'path/to/stop.ico'
                                         }
        """
        if callbacks is None:
            callbacks = {}
        if custom_icons is None:
            custom_icons = {}

        # Load icons (custom or system defaults)
        icons = self._load_button_icons(custom_icons)

        # Create button structures
        buttons = []

        # Backward button
        backward_btn = THUMBBUTTON()
        backward_btn.dwMask = (
            THUMBBUTTON.THB_ICON | THUMBBUTTON.THB_TOOLTIP | THUMBBUTTON.THB_FLAGS
        )
        backward_btn.iId = WindowsConstants.THUMB_BUTTON_BACKWARD
        backward_btn.hIcon = icons.get("backward", None)
        backward_btn.szTip = "Previous"
        backward_btn.dwFlags = WindowsConstants.THBF_ENABLED
        buttons.append(backward_btn)

        # Play/Pause button (starts as play)
        play_pause_btn = THUMBBUTTON()
        play_pause_btn.dwMask = (
            THUMBBUTTON.THB_ICON | THUMBBUTTON.THB_TOOLTIP | THUMBBUTTON.THB_FLAGS
        )
        play_pause_btn.iId = WindowsConstants.THUMB_BUTTON_PLAY_PAUSE
        play_pause_btn.hIcon = icons.get("play", None)
        play_pause_btn.szTip = "Play"
        play_pause_btn.dwFlags = WindowsConstants.THBF_ENABLED
        buttons.append(play_pause_btn)

        # Forward button
        forward_btn = THUMBBUTTON()
        forward_btn.dwMask = (
            THUMBBUTTON.THB_ICON | THUMBBUTTON.THB_TOOLTIP | THUMBBUTTON.THB_FLAGS
        )
        forward_btn.iId = WindowsConstants.THUMB_BUTTON_FORWARD
        forward_btn.hIcon = icons.get("forward", None)
        forward_btn.szTip = "Next"
        forward_btn.dwFlags = WindowsConstants.THBF_ENABLED
        buttons.append(forward_btn)

        # Stop button
        stop_btn = THUMBBUTTON()
        stop_btn.dwMask = (
            THUMBBUTTON.THB_ICON | THUMBBUTTON.THB_TOOLTIP | THUMBBUTTON.THB_FLAGS
        )
        stop_btn.iId = WindowsConstants.THUMB_BUTTON_STOP
        stop_btn.hIcon = icons.get("stop", None)
        stop_btn.szTip = "Stop"
        stop_btn.dwFlags = WindowsConstants.THBF_ENABLED
        buttons.append(stop_btn)

        self.buttons = buttons
        self.button_callbacks = callbacks
        self._icons = icons  # Keep reference to prevent GC

        return self._add_buttons_to_taskbar()

    def _load_button_icons(self, custom_icons):
        """Load icons for buttons, using custom icons where specified or system defaults."""
        icons = {}

        # Default system icons mapping
        default_system_icons = {
            "backward": ("imageres.dll", 260),  # Previous track
            "play": ("imageres.dll", 261),  # Play
            "pause": ("imageres.dll", 262),  # Pause
            "forward": ("imageres.dll", 263),  # Next track
            "stop": ("imageres.dll", 264),  # Stop
        }

        # Load each icon
        for icon_name in ["backward", "play", "pause", "forward", "stop"]:
            if icon_name in custom_icons:
                # Try to load custom icon
                icon = self._load_custom_icon(custom_icons[icon_name], icon_name)
                if icon:
                    icons[icon_name] = icon
                    continue
                else:
                    print(
                        f"⚠️  Failed to load custom icon for {icon_name}, using system default"
                    )

            # Fall back to system default
            dll_name, icon_index = default_system_icons[icon_name]
            icon = self._load_system_icon(dll_name, icon_index)
            if icon:
                icons[icon_name] = icon
            else:
                print(f"⚠️  Failed to load system icon for {icon_name}")

        return icons

    def _load_custom_icon(self, icon_source, icon_name):
        """
        Load a custom icon from various sources.

        Args:
            icon_source: Can be:
                        - String: File path to icon file (.ico, .png, .bmp, etc.)
                        - Tuple: (dll_name, icon_index) for system DLL icons
                        - Integer: HICON handle (already loaded icon)

        Returns:
            HICON handle or None if failed
        """
        try:
            if isinstance(icon_source, str):
                # File path
                return self._load_icon_from_file(icon_source)
            elif isinstance(icon_source, tuple) and len(icon_source) == 2:
                # (dll_name, icon_index)
                dll_name, icon_index = icon_source
                return self._load_system_icon(dll_name, icon_index)
            elif isinstance(icon_source, int):
                # Direct HICON handle
                return icon_source if icon_source != 0 else None
            else:
                print(
                    f"❌ Invalid icon source type for {icon_name}: {type(icon_source)}"
                )
                return None
        except Exception as e:
            print(f"❌ Error loading custom icon for {icon_name}: {e}")
            return None

    def _load_icon_from_file(self, file_path):
        """Load an icon from a file (.ico, .png, .bmp, etc.)."""
        import os

        if not os.path.exists(file_path):
            print(f"❌ Icon file not found: {file_path}")
            return None

        try:
            user32 = ctypes.windll.user32

            # Get file extension to determine loading method
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".ico":
                # Load .ico file directly
                hicon = user32.LoadImageW(
                    None,  # hInst
                    file_path,  # name
                    1,  # IMAGE_ICON
                    16,  # desired width (16x16 for taskbar)
                    16,  # desired height
                    0x00000010 | 0x00002000,  # LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
            else:
                # For other formats (.png, .bmp, etc.), we need to load as bitmap first
                # then convert to icon
                hbitmap = user32.LoadImageW(
                    None,  # hInst
                    file_path,  # name
                    0,  # IMAGE_BITMAP
                    16,  # desired width
                    16,  # desired height
                    0x00000010 | 0x00002000,  # LR_LOADFROMFILE | LR_DEFAULTSIZE
                )

                if hbitmap:
                    # Convert bitmap to icon
                    hicon = self._bitmap_to_icon(hbitmap)
                    # Clean up bitmap
                    ctypes.windll.gdi32.DeleteObject(hbitmap)
                else:
                    hicon = None

            if hicon and hicon != 0:
                # Store for cleanup later
                if "custom_icons" not in self.button_icons:
                    self.button_icons["custom_icons"] = []
                self.button_icons["custom_icons"].append(hicon)
                return hicon
            else:
                print(f"❌ Failed to load icon from file: {file_path}")
                return None

        except Exception as e:
            print(f"❌ Error loading icon from file {file_path}: {e}")
            return None

    def _bitmap_to_icon(self, hbitmap):
        """Convert a bitmap handle to an icon handle."""
        try:
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            # Get bitmap info
            bitmap_info = ctypes.create_string_buffer(24)  # BITMAP structure
            gdi32.GetObjectW(hbitmap, 24, bitmap_info)

            # Create icon info structure
            class ICONINFO(ctypes.Structure):
                _fields_ = [
                    ("fIcon", ctypes.c_bool),
                    ("xHotspot", ctypes.c_uint32),
                    ("yHotspot", ctypes.c_uint32),
                    ("hbmMask", wintypes.HBITMAP),
                    ("hbmColor", wintypes.HBITMAP),
                ]

            # Create mask bitmap (same size, monochrome)
            hdc = user32.GetDC(None)
            hbm_mask = gdi32.CreateCompatibleBitmap(hdc, 16, 16)
            user32.ReleaseDC(None, hdc)

            if not hbm_mask:
                return None

            icon_info = ICONINFO()
            icon_info.fIcon = True
            icon_info.xHotspot = 0
            icon_info.yHotspot = 0
            icon_info.hbmMask = hbm_mask
            icon_info.hbmColor = hbitmap

            # Create icon
            hicon = user32.CreateIconIndirect(ctypes.byref(icon_info))

            # Clean up mask bitmap
            gdi32.DeleteObject(hbm_mask)

            return hicon if hicon and hicon != 0 else None

        except Exception as e:
            print(f"❌ Error converting bitmap to icon: {e}")
            return None

    def _load_system_icon(self, dll_name, icon_index):
        """Load an icon from a system DLL."""
        try:
            shell32 = ctypes.windll.shell32
            hicon = shell32.ExtractIconW(0, dll_name, icon_index)
            return hicon if hicon and hicon != 1 else None
        except:
            return None

    def _add_buttons_to_taskbar(self):
        """Add the buttons to the taskbar."""
        if not self.buttons:
            return False

        try:
            # Create array of THUMBBUTTON structures
            button_array = (THUMBBUTTON * len(self.buttons))(*self.buttons)

            # Add buttons to taskbar
            hr = self.taskbar_manager.vtbl.ThumbBarAddButtons(
                self.taskbar_manager.taskbar_interface,
                self.taskbar_manager.hwnd,
                len(self.buttons),
                ctypes.cast(button_array, ctypes.c_void_p),
            )

            return hr == 0
        except Exception as e:
            print(f"❌ Error adding thumbnail buttons: {e}")
            return False

    def update_play_pause_button(self, is_playing=None):
        """Update the play/pause button state and icon."""
        if is_playing is not None:
            self.is_playing = is_playing
        else:
            self.is_playing = not self.is_playing

        # Find the play/pause button
        play_pause_btn = None
        for btn in self.buttons:
            if btn.iId == WindowsConstants.THUMB_BUTTON_PLAY_PAUSE:
                play_pause_btn = btn
                break

        if play_pause_btn is None:
            return False

        # Update icon and tooltip based on state
        if self.is_playing:
            play_pause_btn.hIcon = self._icons.get("pause", None)
            play_pause_btn.szTip = "Pause"
        else:
            play_pause_btn.hIcon = self._icons.get("play", None)
            play_pause_btn.szTip = "Play"

        # Update the button on taskbar
        try:
            button_array = (THUMBBUTTON * 1)(play_pause_btn)
            hr = self.taskbar_manager.vtbl.ThumbBarUpdateButtons(
                self.taskbar_manager.taskbar_interface,
                self.taskbar_manager.hwnd,
                1,
                ctypes.cast(button_array, ctypes.c_void_p),
            )
            return hr == 0
        except Exception as e:
            print(f"❌ Error updating play/pause button: {e}")
            return False

    def set_button_enabled(self, button_id, enabled=True):
        """Enable or disable a specific button."""
        button = None
        for btn in self.buttons:
            if btn.iId == button_id:
                button = btn
                break

        if button is None:
            return False

        # Update button flags
        if enabled:
            button.dwFlags = WindowsConstants.THBF_ENABLED
        else:
            button.dwFlags = WindowsConstants.THBF_DISABLED

        # Update the button on taskbar
        try:
            button_array = (THUMBBUTTON * 1)(button)
            hr = self.taskbar_manager.vtbl.ThumbBarUpdateButtons(
                self.taskbar_manager.taskbar_interface,
                self.taskbar_manager.hwnd,
                1,
                ctypes.cast(button_array, ctypes.c_void_p),
            )
            return hr == 0
        except Exception as e:
            print(f"❌ Error updating button state: {e}")
            return False

    def handle_button_click(self, button_id):
        """Handle button click events."""
        if button_id == WindowsConstants.THUMB_BUTTON_PLAY_PAUSE:
            self.update_play_pause_button()

        # Call user-defined callback if available
        callback = self.button_callbacks.get(button_id)
        if callback and callable(callback):
            try:
                callback(
                    button_id,
                    (
                        self.is_playing
                        if button_id == WindowsConstants.THUMB_BUTTON_PLAY_PAUSE
                        else None
                    ),
                )
            except Exception as e:
                print(f"❌ Error in button callback: {e}")

        return True

    def update_button_icon(self, button_id, icon_source):
        """
        Update the icon for a specific button.

        Args:
            button_id (int): Button ID (WindowsConstants.THUMB_BUTTON_*)
            icon_source: Icon source (same format as in create_media_buttons)

        Returns:
            bool: True if icon was updated successfully
        """
        # Load the new icon
        icon = self._load_custom_icon(icon_source, f"button_{button_id}")
        if not icon:
            return False

        # Find the button
        button = None
        for btn in self.buttons:
            if btn.iId == button_id:
                button = btn
                break

        if not button:
            print(f"❌ Button with ID {button_id} not found")
            return False

        # Update button icon
        old_icon = button.hIcon
        button.hIcon = icon

        # Update on taskbar
        try:
            button_array = (THUMBBUTTON * 1)(button)
            hr = self.taskbar_manager.vtbl.ThumbBarUpdateButtons(
                self.taskbar_manager.taskbar_interface,
                self.taskbar_manager.hwnd,
                1,
                ctypes.cast(button_array, ctypes.c_void_p),
            )

            if hr == 0:
                # Clean up old icon if it was custom
                if old_icon and "custom_icons" in self.button_icons:
                    if old_icon in self.button_icons["custom_icons"]:
                        ctypes.windll.user32.DestroyIcon(old_icon)
                        self.button_icons["custom_icons"].remove(old_icon)

                # Store new icon for cleanup
                if "custom_icons" not in self.button_icons:
                    self.button_icons["custom_icons"] = []
                self.button_icons["custom_icons"].append(icon)

                return True
            else:
                print(f"❌ Failed to update button icon on taskbar: 0x{hr:08X}")
                return False

        except Exception as e:
            print(f"❌ Error updating button icon: {e}")
            return False

    def cleanup_resources(self):
        """Clean up loaded custom icons to prevent resource leaks."""
        if "custom_icons" in self.button_icons:
            for hicon in self.button_icons["custom_icons"]:
                try:
                    ctypes.windll.user32.DestroyIcon(hicon)
                except:
                    pass  # Ignore errors during cleanup
            self.button_icons["custom_icons"].clear()

    def __del__(self):
        """Destructor to ensure resource cleanup."""
        try:
            self.cleanup_resources()
        except:
            pass  # Ignore errors during destruction


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

        # Add pending button callbacks if any were requested before taskbar button was ready
        if (
            self._pending_button_callbacks is not None
            or self._pending_custom_icons is not None
        ):
            self.AddMediaControlButtons(
                self._pending_button_callbacks, self._pending_custom_icons
            )
            self._pending_button_callbacks = None
            self._pending_custom_icons = None

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
        """
        Add media control buttons (backward, play/pause, forward, stop) to the taskbar thumbnail.

        Args:
            callbacks (dict, optional): Dictionary mapping button IDs to callback functions.
                                      Button IDs are accessible via WindowsConstants:
                                      - THUMB_BUTTON_BACKWARD
                                      - THUMB_BUTTON_PLAY_PAUSE
                                      - THUMB_BUTTON_FORWARD
                                      - THUMB_BUTTON_STOP

                                      Callback signature: callback(button_id, is_playing=None)
                                      For play/pause button, is_playing indicates current state.

            custom_icons (dict, optional): Dictionary mapping button names to icon sources.
                                         Button names: 'backward', 'play', 'pause', 'forward', 'stop'
                                         Icon sources can be:
                                         - String: File path to icon (.ico, .png, .bmp, etc.)
                                         - Tuple: (dll_name, icon_index) for system DLL icons
                                         - Integer: HICON handle (already loaded icon)

        Returns:
            bool: True if buttons were added successfully, False otherwise.

        Example:
            def on_play_pause(button_id, is_playing):
                print(f"Play/Pause clicked, now playing: {is_playing}")

            def on_next(button_id, is_playing):
                print("Next track clicked")

            callbacks = {
                WindowsConstants.THUMB_BUTTON_PLAY_PAUSE: on_play_pause,
                WindowsConstants.THUMB_BUTTON_FORWARD: on_next,
            }

            custom_icons = {
                'play': 'icons/play.ico',
                'pause': 'icons/pause.ico',
                'forward': ('shell32.dll', 16),  # System icon
                'backward': ('shell32.dll', 15)
            }

            taskbar_manager.AddMediaControlButtons(callbacks, custom_icons)
        """
        if not self.taskbar_button_created:
            print(
                "⚠️  Taskbar button not yet created. Buttons will be added when available."
            )
            # Store callbacks and icons for later use
            if callbacks:
                self._pending_button_callbacks = callbacks
            if custom_icons:
                self._pending_custom_icons = custom_icons
            return False

        # Initialize toolbar manager if not already done
        if not self.toolbar_manager:
            self.toolbar_manager = ThumbnailToolbarManager(self)

        success = self.toolbar_manager.create_media_buttons(callbacks, custom_icons)
        if success:
            print("✅ Media control buttons added to taskbar thumbnail")
        else:
            print("❌ Failed to add media control buttons")

        return success

    def UpdatePlayPauseButton(self, is_playing):
        """
        Update the play/pause button to show play or pause icon.

        Args:
            is_playing (bool): True to show pause icon, False to show play icon.

        Returns:
            bool: True if button was updated successfully, False otherwise.
        """
        if not self.toolbar_manager:
            print(
                "❌ Media control buttons not initialized. Call AddMediaControlButtons() first."
            )
            return False

        return self.toolbar_manager.update_play_pause_button(is_playing)

    def SetButtonEnabled(self, button_id, enabled=True):
        """
        Enable or disable a specific thumbnail toolbar button.

        Args:
            button_id (int): Button ID (use WindowsConstants.THUMB_BUTTON_* constants)
            enabled (bool): True to enable, False to disable

        Returns:
            bool: True if button state was updated successfully, False otherwise.
        """
        if not self.toolbar_manager:
            print(
                "❌ Media control buttons not initialized. Call AddMediaControlButtons() first."
            )
            return False

        return self.toolbar_manager.set_button_enabled(button_id, enabled)

    def UpdateButtonIcon(self, button_id, icon_source):
        """
        Update the icon for a specific thumbnail toolbar button.

        Args:
            button_id (int): Button ID (use WindowsConstants.THUMB_BUTTON_* constants)
            icon_source: Icon source, can be:
                        - String: File path to icon file (.ico, .png, .bmp, etc.)
                        - Tuple: (dll_name, icon_index) for system DLL icons
                        - Integer: HICON handle (already loaded icon)

        Returns:
            bool: True if icon was updated successfully, False otherwise.

        Example:
            # Update play button with custom icon file
            taskbar_manager.UpdateButtonIcon(WindowsConstants.THUMB_BUTTON_PLAY_PAUSE, 'icons/play.ico')

            # Update forward button with system icon
            taskbar_manager.UpdateButtonIcon(WindowsConstants.THUMB_BUTTON_FORWARD, ('shell32.dll', 16))
        """
        if not self.toolbar_manager:
            print(
                "❌ Media control buttons not initialized. Call AddMediaControlButtons() first."
            )
            return False

        return self.toolbar_manager.update_button_icon(button_id, icon_source)

    def GetAvailableSystemIcons(self):
        """
        Get a dictionary of commonly used system icons that can be used for buttons.

        Returns:
            dict: Dictionary mapping icon names to (dll_name, icon_index) tuples
        """
        return {
            # Media control icons
            "media_play": ("imageres.dll", 261),
            "media_pause": ("imageres.dll", 262),
            "media_stop": ("imageres.dll", 264),
            "media_previous": ("imageres.dll", 260),
            "media_next": ("imageres.dll", 263),
            "media_record": ("imageres.dll", 265),
            # Navigation icons
            "arrow_left": ("shell32.dll", 15),
            "arrow_right": ("shell32.dll", 16),
            "arrow_up": ("shell32.dll", 17),
            "arrow_down": ("shell32.dll", 18),
            # Common actions
            "refresh": ("shell32.dll", 238),
            "settings": ("shell32.dll", 316),
            "home": ("shell32.dll", 235),
            "search": ("shell32.dll", 23),
            "folder": ("shell32.dll", 3),
            "document": ("shell32.dll", 1),
            # Status icons
            "warning": ("user32.dll", 32515),
            "error": ("user32.dll", 32513),
            "info": ("user32.dll", 32516),
            "question": ("user32.dll", 32514),
        }

    def GetButtonConstants(self):
        """
        Get a dictionary of button ID constants for use with callbacks.

        Returns:
            dict: Dictionary mapping button names to their ID constants.
        """
        return {
            "BACKWARD": WindowsConstants.THUMB_BUTTON_BACKWARD,
            "PLAY_PAUSE": WindowsConstants.THUMB_BUTTON_PLAY_PAUSE,
            "FORWARD": WindowsConstants.THUMB_BUTTON_FORWARD,
            "STOP": WindowsConstants.THUMB_BUTTON_STOP,
        }
