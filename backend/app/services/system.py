import logging
import sys
import psutil
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas-backend")

class SystemService:
    """Service for retrieving local OS metrics and active window context."""

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
                    # Retrieve window title length
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        active_title = buff.value

                    # Retrieve PID and process name
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
