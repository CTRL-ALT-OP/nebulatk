import ctypes
from ctypes import wintypes
from comtypes import GUID, CoInitialize


class TaskbarManager:
    """Manages Windows taskbar features for a Tkinter application."""

    def __init__(self, root):
        """Initialize the taskbar manager for the given Tkinter root window.

        Args:
            root: The nebulatk window object
        """
        self.window = (
            root  # Store the nebulatk window object instead of raw tkinter root
        )
        self.root = None  # Will be set safely later
        self.hwnd = None
        self.taskbar_interface = None
        self.old_wndproc = None
        self.new_wndproc = None
        self.clip_rect = None
        self.taskbar_button_created = False
        self.auto_invalidate_enabled = True  # Enable automatic invalidation by default
        self.debounce_delay = 50  # 50ms debounce delay (reduced from 500ms)

        # Polling-based delegation system (thread-safe)
        self.thumbnail_request_flag = False
        self.thumbnail_width = 0
        self.thumbnail_height = 0
        self.live_preview_request_flag = False
        self.polling_active = False

        # Debouncing for thumbnail and live preview requests
        self.thumbnail_pending_timer = None
        self.live_preview_pending_timer = None

        # Initialize COM
        CoInitialize()

        # Set up the window and taskbar interface
        self._setup_window()
        self._setup_taskbar_interface()
        self._setup_window_hook()
        self.manual_apply()

    def _setup_window(self):
        """Set up the window handle and ensure it appears in taskbar."""

        # Safely get the tkinter root and perform operations on the main thread
        def setup_window_safe():
            self.root = self.window.root
            self.root.wm_attributes("-toolwindow", False)
            self.root.lift()
            self.root.update()

            # Get the correct window handle
            child_hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            self.hwnd = user32.GetAncestor(child_hwnd, 2)  # GA_ROOT = 2
            if self.hwnd == 0:
                self.hwnd = child_hwnd

        # Execute safely on the main thread
        self._schedule_safe_tkinter_call(setup_window_safe)

    def _schedule_safe_tkinter_call(self, func):
        """Schedule a function to be called safely on the tkinter main thread."""
        try:
            # If we're already on the main thread, call directly
            if self.window.root is not None:
                func()
                # Start polling after root is available
                if not self.polling_active:
                    self._start_polling()
            else:
                # Wait for the window to be ready
                import time

                while self.window.root is None:
                    time.sleep(0.01)
                func()
                # Start polling after root is available
                if not self.polling_active:
                    self._start_polling()
        except Exception as e:
            print(f"Error in safe tkinter call: {e}")

    def _setup_taskbar_interface(self):
        """Set up the ITaskbarList3 COM interface."""
        # Define COM types and GUIDs
        HRESULT = ctypes.c_long
        PVOID = ctypes.c_void_p
        UINT = ctypes.c_uint
        CLSCTX_INPROC_SERVER = 0x1
        CLSID_TaskbarList = GUID("{56FDF344-FD6D-11D0-958A-006097C9A090}")
        IID_ITaskbarList3 = GUID("{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}")

        # Define ITaskbarList3 interface structure
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
            ctypes.byref(CLSID_TaskbarList),
            None,
            CLSCTX_INPROC_SERVER,
            ctypes.byref(IID_ITaskbarList3),
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

    def _setup_window_hook(self):
        """Set up window message hook to handle taskbar messages."""
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
        GWL_WNDPROC = -4

        TaskbarButtonCreated = user32.RegisterWindowMessageW("TaskbarButtonCreated")
        WM_DWMSENDICONICTHUMBNAIL = 0x0323
        WM_DWMSENDICONICLIVEPREVIEWBITMAP = 0x0326

        # Window update messages that should trigger thumbnail invalidation
        WM_PAINT = 0x000F
        WM_SIZE = 0x0005
        WM_MOVE = 0x0003
        WM_SHOWWINDOW = 0x0018
        WM_ACTIVATEAPP = 0x001C
        WM_SETFOCUS = 0x0007
        WM_KILLFOCUS = 0x0008

        # Get the old window procedure
        self.old_wndproc = user32.GetWindowLongPtrW(self.hwnd, GWL_WNDPROC)

        @WNDPROCTYPE
        def window_proc(hwnd, msg, wparam, lparam):
            if msg == TaskbarButtonCreated:
                self._on_taskbar_button_created()
            elif msg == WM_DWMSENDICONICTHUMBNAIL:
                # Thread-safe delegation: capture parameters and schedule on main thread
                height = lparam & 0xFFFF
                width = (lparam >> 16) & 0xFFFF
                self._delegate_thumbnail_request(hwnd, width, height)
                return 0
            elif msg == WM_DWMSENDICONICLIVEPREVIEWBITMAP:
                # Thread-safe delegation: capture parameters and schedule on main thread
                self._delegate_live_preview_request(hwnd)
                return 0
            elif msg in (
                WM_PAINT,
                WM_SIZE,
                WM_MOVE,
                WM_SHOWWINDOW,
                WM_ACTIVATEAPP,
                WM_SETFOCUS,
                WM_KILLFOCUS,
            ):
                # Auto-invalidate thumbnails and live previews on window updates
                if self.auto_invalidate_enabled:
                    self._auto_invalidate_thumbnails()

            return user32.CallWindowProcW(
                LONG_PTR(self.old_wndproc), hwnd, msg, wparam, lparam
            )

        # Store reference and install hook
        self.new_wndproc = window_proc
        func_ptr = LONG_PTR(ctypes.cast(window_proc, ctypes.c_void_p).value)
        user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, func_ptr)

    def _on_taskbar_button_created(self):
        """Handle taskbar button creation."""
        self._apply_taskbar_features()

    def _apply_taskbar_features(self):
        """Apply all taskbar features like the working implementation."""
        # Set up custom thumbnails now that we have thread-safe delegation
        self._setup_custom_thumbnails()

        # Set default tooltip
        self._set_thumbnail_tooltip("TaskbarManager Demo")

        # Invalidate to trigger thumbnail request
        dwmapi = ctypes.windll.dwmapi
        dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)

        self.taskbar_button_created = True

    def _set_thumbnail_tooltip(self, text):
        """Set a custom tooltip for the taskbar thumbnail."""
        hr = self.vtbl.SetThumbnailToolTip(self.taskbar_interface, self.hwnd, text)
        status = "SUCCESS" if hr == 0 else f"ERROR 0x{hr & 0xFFFFFFFF:08X}"
        return hr == 0

    def manual_apply(self):
        """Manually apply taskbar features (for testing/debugging)."""
        if not self.taskbar_button_created:
            self._apply_taskbar_features()

    def _validate_dimensions(self, width, height, name="dimension"):
        """Validate and clamp dimensions to prevent integer overflow.

        Args:
            width: Width value to validate
            height: Height value to validate
            name: Name for error messages

        Returns:
            tuple: (validated_width, validated_height)
        """
        MAX_DIMENSION = 32767  # Maximum safe dimension for GDI functions

        # Ensure positive values
        width = max(1, int(width))
        height = max(1, int(height))

        # Clamp to maximum safe values
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            print(
                f"⚠️  Large {name} detected: {width}x{height}, clamping to safe values"
            )
            width = min(width, MAX_DIMENSION)
            height = min(height, MAX_DIMENSION)

        return width, height

    def _validate_coordinates(self, x, y, max_x=None, max_y=None):
        """Validate and clamp coordinates to prevent integer overflow.

        Args:
            x: X coordinate to validate
            y: Y coordinate to validate
            max_x: Maximum allowed X value
            max_y: Maximum allowed Y value

        Returns:
            tuple: (validated_x, validated_y)
        """
        MAX_COORD = 32767  # Maximum safe coordinate for GDI functions

        # Ensure non-negative values
        x = max(0, int(x))
        y = max(0, int(y))

        # Apply maximum bounds if specified
        if max_x is not None:
            x = min(x, int(max_x))
        if max_y is not None:
            y = min(y, int(max_y))

        # Clamp to absolute maximum safe values
        x = min(x, MAX_COORD)
        y = min(y, MAX_COORD)

        return x, y

    def _setup_custom_thumbnails(self):
        """Set up the window for custom thumbnails and live previews."""
        dwmapi = ctypes.windll.dwmapi
        DWMWA_FORCE_ICONIC_REPRESENTATION = 7
        DWMWA_HAS_ICONIC_BITMAP = 10
        DWMWA_DISALLOW_PEEK = 12

        # Enable custom thumbnails
        force_iconic = ctypes.c_int(1)
        has_iconic = ctypes.c_int(1)
        disallow_peek = ctypes.c_int(0)  # 0 = allow peek, 1 = disallow peek

        hr1 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            DWMWA_FORCE_ICONIC_REPRESENTATION,
            ctypes.byref(force_iconic),
            ctypes.sizeof(force_iconic),
        )

        hr2 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            DWMWA_HAS_ICONIC_BITMAP,
            ctypes.byref(has_iconic),
            ctypes.sizeof(has_iconic),
        )

        # Enable live preview (Aero Peek)
        hr3 = dwmapi.DwmSetWindowAttribute(
            self.hwnd,
            DWMWA_DISALLOW_PEEK,
            ctypes.byref(disallow_peek),
            ctypes.sizeof(disallow_peek),
        )

        return hr1 == 0 and hr2 == 0 and hr3 == 0

    def _handle_thumbnail_request_safe(self, hwnd, width, height):
        """Handle thumbnail generation request on main thread (thread-safe)."""

        # Validate thumbnail dimensions to prevent overflow
        width, height = self._validate_dimensions(width, height, "thumbnail request")

        try:
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
        return self._create_thumbnail_bitmap(0, 0, None, None, width, height)

    def _create_clipped_thumbnail(self, width, height):
        """Create thumbnail of the clipped region."""
        if not self.clip_rect:
            return self._create_full_thumbnail(width, height)
        return self._create_thumbnail_bitmap(
            self.clip_rect.left,
            self.clip_rect.top,
            self.clip_rect.right - self.clip_rect.left,
            self.clip_rect.bottom - self.clip_rect.top,
            width,
            height,
        )

    def _create_thumbnail_bitmap(
        self,
        src_x,
        src_y,
        src_width,
        src_height,
        thumb_width,
        thumb_height,
        bypass_clipping=False,
    ):
        """Create a thumbnail bitmap from window content using the exact working approach.

        This method accepts a parameter to bypass clipping for live previews.
        """
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        # Set up proper ctypes function signatures to prevent overflow errors
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

        user32.GetDC.argtypes = [wintypes.HWND]
        user32.GetDC.restype = wintypes.HDC
        user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
        user32.ReleaseDC.restype = ctypes.c_int
        user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetClientRect.restype = wintypes.BOOL

        try:
            # Get the client area dimensions
            client_rect = wintypes.RECT()
            user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))
            client_width = client_rect.right - client_rect.left
            client_height = client_rect.bottom - client_rect.top

            # Add bounds checking to prevent overflow
            MAX_DIMENSION = 32767  # Maximum safe dimension for GDI functions

            if client_width <= 0 or client_height <= 0:
                return None

            if client_width > MAX_DIMENSION or client_height > MAX_DIMENSION:
                client_width = min(client_width, MAX_DIMENSION)
                client_height = min(client_height, MAX_DIMENSION)

            # Determine the source rectangle (what part of the window to capture)
            if self.clip_rect and not bypass_clipping:
                # Use the clipping rectangle (only for thumbnails when not bypassing)
                src_x = max(0, min(self.clip_rect.left, client_width))
                src_y = max(0, min(self.clip_rect.top, client_height))
                src_width = max(
                    1,
                    min(
                        self.clip_rect.right - self.clip_rect.left, client_width - src_x
                    ),
                )
                src_height = max(
                    1,
                    min(
                        self.clip_rect.bottom - self.clip_rect.top,
                        client_height - src_y,
                    ),
                )
            else:
                # Use the entire client area (for live previews or when no clipping)
                src_x = 0
                src_y = 0
                src_width = client_width
                src_height = client_height

            # Ensure all dimensions are within safe bounds
            src_width = max(1, min(src_width, MAX_DIMENSION))
            src_height = max(1, min(src_height, MAX_DIMENSION))
            thumb_width = max(1, min(thumb_width, MAX_DIMENSION))
            thumb_height = max(1, min(thumb_height, MAX_DIMENSION))

            # Create device contexts
            hdc_screen = user32.GetDC(None)
            hdc_window = user32.GetDC(self.hwnd)
            hdc_mem_source = gdi32.CreateCompatibleDC(hdc_screen)
            hdc_mem_thumb = gdi32.CreateCompatibleDC(hdc_screen)

            # Always capture the full window first, then clip if needed
            if self.clip_rect and not bypass_clipping:
                # Clipping mode: capture full window then extract region (thumbnails only)
                hbitmap_full = gdi32.CreateCompatibleBitmap(
                    hdc_screen, ctypes.c_int(client_width), ctypes.c_int(client_height)
                )
                hdc_temp = gdi32.CreateCompatibleDC(hdc_screen)
                old_bitmap_temp = gdi32.SelectObject(hdc_temp, hbitmap_full)

                # Set up PrintWindow function signature
                user32.PrintWindow.argtypes = [
                    wintypes.HWND,
                    wintypes.HDC,
                    wintypes.UINT,
                ]
                user32.PrintWindow.restype = wintypes.BOOL

                # Capture the full window content first
                success = user32.PrintWindow(
                    self.hwnd, hdc_temp, 1
                )  # PW_CLIENTONLY = 1
                if not success:
                    # Fallback to BitBlt if PrintWindow fails
                    success = gdi32.BitBlt(
                        hdc_temp,
                        ctypes.c_int(0),
                        ctypes.c_int(0),
                        ctypes.c_int(client_width),
                        ctypes.c_int(client_height),
                        hdc_window,
                        ctypes.c_int(0),
                        ctypes.c_int(0),
                        wintypes.DWORD(0x00CC0020),  # SRCCOPY
                    )

                if success:
                    # Now create the clipped bitmap and copy the region
                    hbitmap_source = gdi32.CreateCompatibleBitmap(
                        hdc_screen, ctypes.c_int(src_width), ctypes.c_int(src_height)
                    )
                    if hbitmap_source:
                        old_bitmap_source = gdi32.SelectObject(
                            hdc_mem_source, hbitmap_source
                        )

                        # Copy just the clipped region
                        success = gdi32.BitBlt(
                            hdc_mem_source,
                            ctypes.c_int(0),
                            ctypes.c_int(0),
                            ctypes.c_int(src_width),
                            ctypes.c_int(src_height),
                            hdc_temp,
                            ctypes.c_int(src_x),
                            ctypes.c_int(src_y),
                            wintypes.DWORD(0x00CC0020),  # SRCCOPY
                        )
                    else:
                        success = False

                # Clean up temporary resources
                gdi32.SelectObject(hdc_temp, old_bitmap_temp)
                gdi32.DeleteObject(hbitmap_full)
                gdi32.DeleteDC(hdc_temp)

            else:
                # No clipping or live preview - capture directly to the source bitmap
                hbitmap_source = gdi32.CreateCompatibleBitmap(
                    hdc_screen, ctypes.c_int(src_width), ctypes.c_int(src_height)
                )
                if not hbitmap_source:
                    user32.ReleaseDC(None, hdc_screen)
                    user32.ReleaseDC(self.hwnd, hdc_window)
                    gdi32.DeleteDC(hdc_mem_source)
                    gdi32.DeleteDC(hdc_mem_thumb)
                    return None

                old_bitmap_source = gdi32.SelectObject(hdc_mem_source, hbitmap_source)

                # Set up PrintWindow function signature
                user32.PrintWindow.argtypes = [
                    wintypes.HWND,
                    wintypes.HDC,
                    wintypes.UINT,
                ]
                user32.PrintWindow.restype = wintypes.BOOL

                # Capture the window content (client area only)
                success = user32.PrintWindow(
                    self.hwnd, hdc_mem_source, 1
                )  # PW_CLIENTONLY = 1
                if not success:
                    # Fallback to BitBlt if PrintWindow fails
                    success = gdi32.BitBlt(
                        hdc_mem_source,
                        ctypes.c_int(0),
                        ctypes.c_int(0),
                        ctypes.c_int(src_width),
                        ctypes.c_int(src_height),
                        hdc_window,
                        ctypes.c_int(src_x),
                        ctypes.c_int(src_y),
                        wintypes.DWORD(0x00CC0020),  # SRCCOPY
                    )

            if not success:
                if "old_bitmap_source" in locals() and "hbitmap_source" in locals():
                    gdi32.SelectObject(hdc_mem_source, old_bitmap_source)
                    gdi32.DeleteObject(hbitmap_source)
                gdi32.DeleteDC(hdc_mem_source)
                gdi32.DeleteDC(hdc_mem_thumb)
                user32.ReleaseDC(None, hdc_screen)
                user32.ReleaseDC(self.hwnd, hdc_window)
                return None

            # Create a 32-bit DIB bitmap for the thumbnail (CRITICAL for Windows thumbnails)
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
                    ("bmiColors", ctypes.c_uint32 * 3),  # Space for color table
                ]

            # Set up CreateDIBSection function signature
            gdi32.CreateDIBSection.argtypes = [
                wintypes.HDC,
                ctypes.POINTER(BITMAPINFO),
                ctypes.c_uint,
                ctypes.POINTER(ctypes.c_void_p),
                wintypes.HANDLE,
                ctypes.c_uint,
            ]
            gdi32.CreateDIBSection.restype = wintypes.HBITMAP

            # Calculate aspect-ratio preserving dimensions that fit within maximum bounds
            # The requested dimensions are maximums, not exact requirements
            src_aspect = src_width / src_height
            max_width = thumb_width
            max_height = thumb_height

            if src_width <= max_width and src_height <= max_height:
                # Source already fits within bounds - use original size
                final_width = src_width
                final_height = src_height
            else:
                # Scale down to fit within maximum bounds while preserving aspect ratio
                scale_x = max_width / src_width
                scale_y = max_height / src_height
                scale = min(scale_x, scale_y)  # Use the smaller scale to ensure it fits

                final_width = int(src_width * scale)
                final_height = int(src_height * scale)

            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = ctypes.c_int32(final_width)
            bmi.bmiHeader.biHeight = ctypes.c_int32(
                -final_height
            )  # Negative for top-down DIB
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32  # Must be 32-bit for Windows thumbnails
            bmi.bmiHeader.biCompression = 0  # BI_RGB
            bmi.bmiHeader.biSizeImage = 0
            bmi.bmiHeader.biXPelsPerMeter = 0
            bmi.bmiHeader.biYPelsPerMeter = 0
            bmi.bmiHeader.biClrUsed = 0
            bmi.bmiHeader.biClrImportant = 0

            bits = ctypes.c_void_p()
            hbitmap_thumb = gdi32.CreateDIBSection(
                hdc_screen,
                ctypes.byref(bmi),
                0,  # DIB_RGB_COLORS
                ctypes.byref(bits),
                None,
                0,
            )

            if not hbitmap_thumb:
                gdi32.SelectObject(hdc_mem_source, old_bitmap_source)
                gdi32.DeleteObject(hbitmap_source)
                gdi32.DeleteDC(hdc_mem_source)
                gdi32.DeleteDC(hdc_mem_thumb)
                user32.ReleaseDC(None, hdc_screen)
                user32.ReleaseDC(self.hwnd, hdc_window)
                return None

            # Select the thumbnail bitmap
            old_bitmap_thumb = gdi32.SelectObject(hdc_mem_thumb, hbitmap_thumb)

            # Copy/scale the source to fill the entire final bitmap (no black borders)
            if final_width == src_width and final_height == src_height:
                # Direct copy - no scaling needed
                success = gdi32.BitBlt(
                    hdc_mem_thumb,
                    ctypes.c_int(0),
                    ctypes.c_int(0),
                    ctypes.c_int(final_width),
                    ctypes.c_int(final_height),
                    hdc_mem_source,
                    ctypes.c_int(0),
                    ctypes.c_int(0),
                    wintypes.DWORD(0x00CC0020),  # SRCCOPY
                )
            else:
                # Scale the source to the final dimensions (fills entire bitmap)
                gdi32.SetStretchBltMode(hdc_mem_thumb, 4)  # HALFTONE for better quality
                success = gdi32.StretchBlt(
                    hdc_mem_thumb,
                    ctypes.c_int(0),
                    ctypes.c_int(0),
                    ctypes.c_int(final_width),
                    ctypes.c_int(final_height),
                    hdc_mem_source,
                    ctypes.c_int(0),
                    ctypes.c_int(0),
                    ctypes.c_int(src_width),
                    ctypes.c_int(src_height),
                    wintypes.DWORD(0x00CC0020),  # SRCCOPY
                )

            if not success:
                gdi32.SelectObject(hdc_mem_thumb, old_bitmap_thumb)
                gdi32.DeleteObject(hbitmap_thumb)
                hbitmap_thumb = None

            # Cleanup
            if "old_bitmap_source" in locals() and "hbitmap_source" in locals():
                gdi32.SelectObject(hdc_mem_source, old_bitmap_source)
                gdi32.DeleteObject(hbitmap_source)
            gdi32.SelectObject(hdc_mem_thumb, old_bitmap_thumb)
            gdi32.DeleteDC(hdc_mem_source)
            gdi32.DeleteDC(hdc_mem_thumb)
            user32.ReleaseDC(None, hdc_screen)
            user32.ReleaseDC(self.hwnd, hdc_window)

            return hbitmap_thumb

        except Exception as e:
            return None

    def SetThumbnailClip(self, x, y, width, height):
        """Set the thumbnail clipping rectangle.

        Args:
            x: X coordinate of the clip region
            y: Y coordinate of the clip region
            width: Width of the clip region
            height: Height of the clip region
        """
        # Validate and clamp all values to prevent overflow
        x, y = self._validate_coordinates(x, y)
        width, height = self._validate_dimensions(width, height, "clip region")

        # Create RECT structure like the working implementation
        self.clip_rect = wintypes.RECT(x, y, x + width, y + height)

        # Invalidate thumbnails to trigger refresh
        if self.taskbar_button_created:
            dwmapi = ctypes.windll.dwmapi
            dwmapi.DwmInvalidateIconicBitmaps.argtypes = [wintypes.HWND]
            dwmapi.DwmInvalidateIconicBitmaps.restype = ctypes.c_long
            dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)

    def SetThumbnailNotification(self, icon_type="warning"):
        """Set the overlay icon on the taskbar button.

        Args:
            icon_type: Type of icon ("warning", "error", "info", or None to clear)
        """
        user32 = ctypes.windll.user32

        if icon_type is None:
            hicon = None
            description = ""
        else:
            icon_map = {
                "warning": 32515,  # IDI_WARNING
                "error": 32513,  # IDI_ERROR
                "info": 32516,  # IDI_INFORMATION
            }
            icon_id = icon_map.get(icon_type, 32515)
            hicon = user32.LoadIconW(None, ctypes.cast(icon_id, wintypes.LPCWSTR))
            description = f"{icon_type.capitalize()} Icon"

        hr = self.vtbl.SetOverlayIcon(
            self.taskbar_interface, self.hwnd, hicon, description
        )
        return hr == 0

    def SetProgress(self, progress):
        """Set the progress bar value on the taskbar button.

        Args:
            progress: Progress value (0-100 integer)
        """
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")

        # Set progress state
        TBPF_NORMAL = 2
        TBPF_NOPROGRESS = 0

        if progress == 0:
            state = TBPF_NOPROGRESS
        else:
            state = TBPF_NORMAL

        hr1 = self.vtbl.SetProgressState(self.taskbar_interface, self.hwnd, state)

        if progress > 0:
            hr2 = self.vtbl.SetProgressValue(
                self.taskbar_interface, self.hwnd, progress, 100
            )
            return hr1 == 0 and hr2 == 0

        return hr1 == 0

    def ClearThumbnailClip(self):
        """Clear the thumbnail clipping rectangle to show the full window."""
        self.clip_rect = None

        if self.taskbar_button_created:
            dwmapi = ctypes.windll.dwmapi
            dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)

    def _handle_live_preview_request_safe(self, hwnd):
        """Handle live preview request on main thread (thread-safe)."""

        try:
            user32 = ctypes.windll.user32
            dwmapi = ctypes.windll.dwmapi

            # Get the current window dimensions
            client_rect = wintypes.RECT()
            user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))
            client_width = client_rect.right - client_rect.left
            client_height = client_rect.bottom - client_rect.top

            if client_width <= 0 or client_height <= 0:
                return

            # For live preview, show the window at actual size (no scaling)
            preview_width = client_width
            preview_height = client_height

            # Create the live preview bitmap
            bitmap = self._create_live_preview_bitmap(preview_width, preview_height)

            if bitmap:
                # Set up DwmSetIconicLivePreviewBitmap function signature
                dwmapi.DwmSetIconicLivePreviewBitmap.argtypes = [
                    wintypes.HWND,
                    wintypes.HBITMAP,
                    ctypes.POINTER(wintypes.POINT),
                    ctypes.c_int,
                ]
                dwmapi.DwmSetIconicLivePreviewBitmap.restype = ctypes.c_long

                # Set the live preview bitmap (no specific client offset for now)
                hr = dwmapi.DwmSetIconicLivePreviewBitmap(hwnd, bitmap, None, 0)

                # Clean up the bitmap
                ctypes.windll.gdi32.DeleteObject(bitmap)
            else:
                print("❌ Failed to create live preview bitmap")
        except Exception as e:
            print(f"❌ Error creating live preview: {e}")

    def _create_live_preview_bitmap(self, width, height):
        """Create a live preview bitmap of the entire window (ignores clipping).

        Live previews should always show the complete window content,
        regardless of any thumbnail clipping settings.
        """
        # Validate dimensions
        width, height = self._validate_dimensions(width, height, "live preview")

        # Get window dimensions for full capture
        user32 = ctypes.windll.user32
        client_rect = wintypes.RECT()
        user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetClientRect.restype = wintypes.BOOL
        user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))

        client_width = client_rect.right - client_rect.left
        client_height = client_rect.bottom - client_rect.top

        # Create live preview with full window dimensions (bypass clipping)
        return self._create_thumbnail_bitmap(
            0, 0, client_width, client_height, width, height, bypass_clipping=True
        )

    def InvalidateLivePreview(self):
        """Invalidate the live preview to force Windows to request a new one."""
        if self.taskbar_button_created:
            dwmapi = ctypes.windll.dwmapi
            # Set up DwmInvalidateIconicBitmaps function signature
            dwmapi.DwmInvalidateIconicBitmaps.argtypes = [wintypes.HWND]
            dwmapi.DwmInvalidateIconicBitmaps.restype = ctypes.c_long
            hr = dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)

    def _auto_invalidate_thumbnails(self):
        """Automatically invalidate thumbnails and live previews when window updates.

        This method is called automatically when window update events are detected.
        It uses a debouncing mechanism to avoid excessive invalidation calls.
        """
        if not self.taskbar_button_created:
            return

        # Use thread-safe method to schedule invalidation
        def schedule_invalidation():
            # Cancel previous pending invalidation
            if hasattr(self, "_invalidate_pending"):
                self.root.after_cancel(self._invalidate_pending)

            # Schedule invalidation after a short delay
            self._invalidate_pending = self.root.after(
                self.debounce_delay, self._perform_invalidation
            )

        # Execute safely on the main thread
        try:
            if self.root is not None:
                schedule_invalidation()
        except Exception as e:
            print(f"Error scheduling invalidation: {e}")

    def _perform_invalidation(self):
        """Perform the actual thumbnail and live preview invalidation."""
        if self.taskbar_button_created:
            dwmapi = ctypes.windll.dwmapi
            dwmapi.DwmInvalidateIconicBitmaps.argtypes = [wintypes.HWND]
            dwmapi.DwmInvalidateIconicBitmaps.restype = ctypes.c_long
            hr = dwmapi.DwmInvalidateIconicBitmaps(self.hwnd)
            # Uncomment the next line for debugging invalidation calls
            # print(f"🔄 Auto-invalidation result: 0x{hr & 0xFFFFFFFF:08X}")

        # Clear the pending invalidation flag
        if hasattr(self, "_invalidate_pending"):
            delattr(self, "_invalidate_pending")

    def SetAutoInvalidation(self, enabled=True):
        """Enable or disable automatic thumbnail and live preview invalidation.

        Args:
            enabled: True to enable auto-invalidation, False to disable
        """
        self.auto_invalidate_enabled = enabled
        print(f"🔄 Auto-invalidation {'enabled' if enabled else 'disabled'}")

    def IsAutoInvalidationEnabled(self):
        """Check if automatic invalidation is currently enabled.

        Returns:
            bool: True if auto-invalidation is enabled, False otherwise
        """
        return self.auto_invalidate_enabled

    def _delegate_thumbnail_request(self, hwnd, width, height):
        """Safely delegate thumbnail request using flags (no Python object access).

        This method is called from the Windows message thread and only sets
        simple flags to avoid any GIL violations.
        """
        # Only set simple integer/boolean flags - no Python object access
        self.thumbnail_width = width
        self.thumbnail_height = height
        self.thumbnail_request_flag = True

    def _delegate_live_preview_request(self, hwnd):
        """Safely delegate live preview request using flags (no Python object access).

        This method is called from the Windows message thread and only sets
        simple flags to avoid any GIL violations.
        """
        # Only set simple boolean flags - no Python object access
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
            # Handle thumbnail requests with debouncing
            if self.thumbnail_request_flag:
                # Cancel any pending thumbnail processing
                if self.thumbnail_pending_timer is not None:
                    self.root.after_cancel(self.thumbnail_pending_timer)

                # Schedule thumbnail processing after debounce delay
                self.thumbnail_pending_timer = self.root.after(
                    self.debounce_delay, self._process_debounced_thumbnail
                )

                # Clear the flag now that we've scheduled processing
                self.thumbnail_request_flag = False

            # Handle live preview requests with debouncing
            if self.live_preview_request_flag:
                # Cancel any pending live preview processing
                if self.live_preview_pending_timer is not None:
                    self.root.after_cancel(self.live_preview_pending_timer)

                # Schedule live preview processing after debounce delay
                self.live_preview_pending_timer = self.root.after(
                    self.debounce_delay, self._process_debounced_live_preview
                )

                # Clear the flag now that we've scheduled processing
                self.live_preview_request_flag = False

        except Exception as e:
            print(f"❌ Error in polling: {e}")

        # Continue polling at faster rate for responsiveness
        if self.root is not None:
            self.root.after(10, self._poll_for_requests)

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

    def SetDebounceDelay(self, delay_ms):
        """Set the debounce delay for thumbnail and live preview requests.

        Args:
            delay_ms (int): Debounce delay in milliseconds (default: 50ms)
                          Higher values = less frequent updates but better performance
                          Lower values = more responsive but potentially more processing
        """
        if delay_ms < 10:
            print("⚠️  Warning: Debounce delay below 10ms may cause performance issues")
        elif delay_ms > 1000:
            print("⚠️  Warning: Debounce delay above 1000ms may feel unresponsive")

        self.debounce_delay = max(10, int(delay_ms))
        print(f"🕐 Debounce delay set to {self.debounce_delay}ms")
        return self

    def GetDebounceDelay(self):
        """Get the current debounce delay in milliseconds.

        Returns:
            int: Current debounce delay in milliseconds
        """
        return self.debounce_delay
