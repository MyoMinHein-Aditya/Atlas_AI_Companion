import sys
import os

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.system import system_service

def test_focus_window_nonexistent():
    # Searching for a non-existent window should return False gracefully without crashing
    result = system_service.focus_window_by_name("NonExistentWindowNameXYZ123")
    assert result is False

def test_launch_system_app_helper():
    # Calling launch_system_app with a known query should return string response
    response = system_service.launch_system_app("notepad")
    assert isinstance(response, str)
    assert "Notepad" in response or "notepad" in response or "brought" in response
