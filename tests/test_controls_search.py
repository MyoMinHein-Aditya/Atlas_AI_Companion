import sys
import os
import pytest

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.system import system_service
from app.services.actions import action_dispatcher

def test_battery_status_structure():
    bat = system_service.get_battery_status()
    assert "percent" in bat
    assert "power_plugged" in bat
    assert "time_left_mins" in bat
    assert isinstance(bat["percent"], (int, float))
    assert isinstance(bat["power_plugged"], bool)
    assert isinstance(bat["time_left_mins"], (int, float))

def test_volume_actions():
    res_up = system_service.change_volume("up")
    res_down = system_service.change_volume("down")
    res_mute = system_service.change_volume("mute")
    assert "volume adjusted" in res_up.lower()
    assert "volume adjusted" in res_down.lower()
    assert "volume adjusted" in res_mute.lower()

def test_power_commands_validation():
    # Test valid/invalid options
    res_lock = system_service.set_system_power("lock")
    res_sleep = system_service.set_system_power("sleep")
    res_invalid = system_service.set_system_power("invalid")
    assert "locked" in res_lock
    assert "sleep" in res_sleep
    assert "Invalid" in res_invalid

def test_file_search_existing():
    results = system_service.search_file_contents("ActionDispatcher")
    assert isinstance(results, list)
    # The keyword exists in actions.py and other files
    assert len(results) > 0
    assert "file" in results[0]
    assert "path" in results[0]

def test_read_file_text_existing():
    # Read docs/Tasks.md or similar docs
    tasks_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "Tasks.md"))
    content = system_service.read_file_text(tasks_path)
    assert isinstance(content, str)
    assert "Phase" in content

@pytest.mark.asyncio
async def test_action_dispatcher_volume():
    res = await action_dispatcher.handle_volume({"direction": "up"})
    assert "volume adjusted" in res.lower()

@pytest.mark.asyncio
async def test_action_dispatcher_file_search():
    res = await action_dispatcher.handle_file_search({"keyword": "ActionDispatcher"})
    assert "Found" in res
