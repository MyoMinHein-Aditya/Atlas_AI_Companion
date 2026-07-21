import logging
import sys
import subprocess
import psutil
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas-backend")

class SystemService:
    """Service for retrieving local OS metrics, launching default apps, and focusing windows."""

    def get_system_metrics(self) -> Dict[str, Any]:
        """Returns current CPU, RAM, and Disk metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024 ** 3), 2),
                    "available_gb": round(memory.available / (1024 ** 3), 2),
                    "used_gb": round(memory.used / (1024 ** 3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024 ** 3), 2),
                    "free_gb": round(disk.free / (1024 ** 3), 2),
                    "percent": disk.percent
                }
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return {
                "cpu_percent": 0.0,
                "memory": {"total_gb": 0, "available_gb": 0, "used_gb": 0, "percent": 0},
                "disk": {"total_gb": 0, "free_gb": 0, "percent": 0}
            }

    def get_active_window(self) -> Dict[str, Optional[str]]:
        """
        Retrieves the title and process name of the active foreground window.
        Uses native Windows ctypes user32 API on Windows.
        """
        active_title = "Unknown Window"
        process_name = "Unknown Process"

        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()

                if hwnd:
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        active_title = buff.value

                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value:
                        try:
                            proc = psutil.Process(pid.value)
                            process_name = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except Exception as e:
                logger.error(f"Failed to retrieve Windows active window: {str(e)}")

        return {
            "title": active_title,
            "process": process_name
        }

    def focus_window_by_name(self, name_query: str) -> bool:
        """
        Searches all open top-level windows for titles matching name_query
        and restores/brings the matching window into front focus view.
        """
        if sys.platform != "win32":
            logger.warning("Window focusing is only supported on Windows OS.")
            return False

        try:
            import ctypes
            user32 = ctypes.windll.user32
            query_lower = name_query.lower().strip()
            matched_hwnd = None

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

            def enum_windows_callback(hwnd, lparam):
                nonlocal matched_hwnd
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value.lower()
                        if query_lower in title:
                            matched_hwnd = hwnd
                            return False  # stop enumeration
                return True

            user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

            if matched_hwnd:
                SW_RESTORE = 9
                user32.ShowWindow(matched_hwnd, SW_RESTORE)
                user32.SetForegroundWindow(matched_hwnd)
                logger.info(f"Successfully brought window matching '{name_query}' to front focus.")
                return True
            else:
                logger.info(f"No active window matching '{name_query}' found.")
                return False
        except Exception as e:
            logger.error(f"Failed to focus window for '{name_query}': {str(e)}")
            return False

    def launch_system_app(self, app_name: str) -> str:
        """
        Launches standard default Windows applications natively in detached mode.
        If an open window matching the application exists, brings it into focus view.
        """
        app_clean = app_name.lower().strip()

        # Map common application aliases to Windows launch commands
        app_command_map = {
            "notepad": "start notepad",
            "text editor": "start notepad",
            "calculator": "start calc",
            "calc": "start calc",
            "browser": "start msedge",
            "edge": "start msedge",
            "chrome": "start chrome",
            "explorer": "start explorer",
            "file explorer": "start explorer",
            "folder": "start explorer",
            "vscode": "start code",
            "code": "start code",
            "terminal": "start cmd",
            "cmd": "start cmd",
            "spotify": "start spotify"
        }

        # First check if an open window matching the app already exists
        focused = self.focus_window_by_name(app_clean)
        if focused:
            return f"Brought open application window for '{app_name}' into view."

        # Otherwise launch the app natively
        cmd = app_command_map.get(app_clean, f"start {app_clean}")
        logger.info(f"Launching system application command: '{cmd}'")

        try:
            if sys.platform == "win32":
                subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen([app_clean])
            return f"Successfully launched {app_name}."
        except Exception as e:
            logger.error(f"Failed to launch application '{app_name}': {str(e)}")
            return f"Failed to launch application '{app_name}': {str(e)}"

    def get_system_context(self) -> Dict[str, Any]:
        """Returns unified system metrics and active window state for AI context."""
        metrics = self.get_system_metrics()
        active_window = self.get_active_window()

        return {
            "metrics": metrics,
            "active_window": active_window,
            "os": sys.platform
        }

system_service = SystemService()
