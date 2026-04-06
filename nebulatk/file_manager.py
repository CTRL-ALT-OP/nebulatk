import shutil
import subprocess
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


def _flatten_patterns(pattern):
    if isinstance(pattern, (list, tuple)):
        values = []
        for item in pattern:
            values.extend(_flatten_patterns(item))
        return values
    if pattern is None:
        return []
    return [str(pattern)]


def _build_windows_filter_spec(filetypes):
    """Build COMDLG filter string from normalized filetypes."""
    filter_chunks = []
    for label, pattern in _normalize_filetypes(filetypes):
        patterns = _flatten_patterns(pattern)
        pattern = ";".join(patterns) if patterns else "*.*"
        filter_chunks.extend([str(label), str(pattern)])

    if not filter_chunks:
        filter_chunks = ["All files", "*.*"]

    return "\0".join(filter_chunks) + "\0\0"


def _open_selected_path(selected_path, mode):
    if not selected_path:
        return None
    try:
        return open(selected_path, mode)
    except Exception:
        return None


def _open_with_windows_native(initialdir, mode, filetypes):
    """Open file dialog using Win32 common dialog API."""
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
                return _open_selected_path(selected_path, mode)
    except Exception:
        return None

    return None


def _escape_applescript_string(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _open_with_macos_native(initialdir, mode, filetypes):
    """Open file dialog using AppleScript on macOS."""
    try:
        base = 'set chosenFile to choose file with prompt "Select a file"'
        if initialdir:
            escaped_dir = _escape_applescript_string(initialdir)
            base += f' default location POSIX file "{escaped_dir}"'
        script = [base, "POSIX path of chosenFile"]
        result = subprocess.run(
            ["osascript", *sum([["-e", line] for line in script], [])],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        selected_path = result.stdout.strip()
        return _open_selected_path(selected_path, mode)
    except Exception:
        return None


def _build_linux_filter_arguments(filetypes):
    normalized = _normalize_filetypes(filetypes)
    zenity_filters = []
    kdialog_filters = []

    for label, pattern in normalized:
        patterns = _flatten_patterns(pattern)
        clean_patterns = [value for value in patterns if value.strip()]
        if not clean_patterns:
            clean_patterns = ["*"]
        zenity_filters.append(f"{label} | {' '.join(clean_patterns)}")
        kdialog_filters.append(f"{' '.join(clean_patterns)}|{label}")

    return zenity_filters, "\n".join(kdialog_filters)


def _open_with_linux_native(initialdir, mode, filetypes):
    """Open file dialog using available Linux desktop tools."""
    zenity_filters, kdialog_filter = _build_linux_filter_arguments(filetypes)
    initial_path = initialdir or ""

    candidates = []
    if shutil.which("zenity"):
        command = ["zenity", "--file-selection"]
        if initial_path:
            command.append(f"--filename={initial_path}")
        for file_filter in zenity_filters:
            command.append(f"--file-filter={file_filter}")
        candidates.append(command)
    if shutil.which("kdialog"):
        command = ["kdialog", "--getopenfilename"]
        if initial_path:
            command.append(initial_path)
        else:
            command.append(".")
        command.append(kdialog_filter if kdialog_filter else "*|All files")
        candidates.append(command)
    if shutil.which("qarma"):
        command = ["qarma", "--file-selection"]
        if initial_path:
            command.append(f"--filename={initial_path}")
        candidates.append(command)

    for command in candidates:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                selected_path = result.stdout.strip()
                file_handle = _open_selected_path(selected_path, mode)
                if file_handle is not None:
                    return file_handle
        except Exception:
            continue

    return None


def FileDialog(window, initialdir=None, mode="r", filetypes=(("All files", "*"),)):
    """Open a platform-native file picker and return an open file handle."""
    window.leave_window(None)
    try:
        if sys.platform == "win32":
            return _open_with_windows_native(initialdir, mode, filetypes)
        if sys.platform == "darwin":
            return _open_with_macos_native(initialdir, mode, filetypes)
        return _open_with_linux_native(initialdir, mode, filetypes)
    except Exception:
        return None
    finally:
        window.leave_window(None)
