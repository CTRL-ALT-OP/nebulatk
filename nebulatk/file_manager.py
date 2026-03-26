import sys


def _normalize_filetypes(filetypes):
    """Normalize filetype tuples for dialog backends."""
    if not filetypes:
        return (("All files", "*"),)

    normalized = []
    for entry in filetypes:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            continue
        label, pattern = entry
        normalized.append((str(label), pattern))

    return tuple(normalized) if normalized else (("All files", "*"),)


def _build_windows_filter_spec(filetypes):
    """Build COMDLG filter string from normalized filetypes."""
    filter_chunks = []
    for label, pattern in _normalize_filetypes(filetypes):
        if isinstance(pattern, (list, tuple)):
            pattern = ";".join(str(value) for value in pattern)
        filter_chunks.extend([str(label), str(pattern)])

    if not filter_chunks:
        filter_chunks = ["All files", "*.*"]

    return "\0".join(filter_chunks) + "\0\0"


def _open_with_tkinter(initialdir, mode, filetypes):
    """Open file dialog using tkinter. Returns (file, dialog_available)."""
    try:
        from tkinter import filedialog
    except Exception:
        return None, False

    try:
        return (
            filedialog.askopenfile(
                initialdir=initialdir,
                mode=mode,
                filetypes=_normalize_filetypes(filetypes),
            ),
            True,
        )
    except Exception:
        return None, False


def _open_with_windows_native(initialdir, mode, filetypes):
    """Windows fallback for environments without tkinter."""
    try:
        import ctypes
        from ctypes import wintypes

        class OPENFILENAMEW(ctypes.Structure):
            _fields_ = [
                ("lStructSize", wintypes.DWORD),
                ("hwndOwner", wintypes.HWND),
                ("hInstance", wintypes.HINSTANCE),
                ("lpstrFilter", wintypes.LPCWSTR),
                ("lpstrCustomFilter", wintypes.LPWSTR),
                ("nMaxCustFilter", wintypes.DWORD),
                ("nFilterIndex", wintypes.DWORD),
                ("lpstrFile", wintypes.LPWSTR),
                ("nMaxFile", wintypes.DWORD),
                ("lpstrFileTitle", wintypes.LPWSTR),
                ("nMaxFileTitle", wintypes.DWORD),
                ("lpstrInitialDir", wintypes.LPCWSTR),
                ("lpstrTitle", wintypes.LPCWSTR),
                ("Flags", wintypes.DWORD),
                ("nFileOffset", wintypes.WORD),
                ("nFileExtension", wintypes.WORD),
                ("lpstrDefExt", wintypes.LPCWSTR),
                ("lCustData", wintypes.LPARAM),
                ("lpfnHook", wintypes.LPVOID),
                ("lpTemplateName", wintypes.LPCWSTR),
                ("pvReserved", wintypes.LPVOID),
                ("dwReserved", wintypes.DWORD),
                ("FlagsEx", wintypes.DWORD),
            ]

        file_buffer = ctypes.create_unicode_buffer(4096)
        dialog = OPENFILENAMEW()
        dialog.lStructSize = ctypes.sizeof(OPENFILENAMEW)
        dialog.lpstrFilter = _build_windows_filter_spec(filetypes)
        dialog.lpstrFile = file_buffer
        dialog.nMaxFile = len(file_buffer)
        dialog.lpstrInitialDir = initialdir
        dialog.Flags = 0x00000008 | 0x00001000

        if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(dialog)):
            selected_path = file_buffer.value
            if selected_path:
                return open(selected_path, mode)
    except Exception:
        return None

    return None


def FileDialog(window, initialdir=None, mode="r", filetypes=(("All files", "*"))):
    """Compatibility wrapper around a platform file picker."""
    window.leave_window(None)

    file_handle, tkinter_available = _open_with_tkinter(initialdir, mode, filetypes)
    if sys.platform == "win32" and not tkinter_available:
        file_handle = _open_with_windows_native(initialdir, mode, filetypes)

    window.leave_window(None)
    return file_handle
