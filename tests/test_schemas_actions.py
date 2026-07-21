import sys
import os
import pytest

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models.schemas import ActionItem, AIPlanResponse, SystemMetrics, MemoryMetrics, DiskMetrics
from app.services.actions import action_dispatcher

def test_pydantic_schemas_instantiation():
    action = ActionItem(type="open_app", app="notepad")
    assert action.type == "open_app"
    assert action.app == "notepad"

    plan = AIPlanResponse(response="Opening notepad.", actions=[action])
    assert plan.response == "Opening notepad."
    assert len(plan.actions) == 1

    metrics = SystemMetrics(
        cpu_percent=12.5,
        memory=MemoryMetrics(total_gb=16.0, available_gb=8.0, used_gb=8.0, percent=50.0),
        disk=DiskMetrics(total_gb=500.0, free_gb=250.0, percent=50.0)
    )
    assert metrics.cpu_percent == 12.5
    assert metrics.memory.total_gb == 16.0

@pytest.mark.asyncio
async def test_action_dispatcher_open_app():
    res = await action_dispatcher.handle_open_app({"app": "notepad"})
    assert isinstance(res, str)
    assert "notepad" in res or "launched" in res or "brought" in res

@pytest.mark.asyncio
async def test_action_dispatcher_open_folder():
    res = await action_dispatcher.handle_open_folder({"path": "docs"})
    assert isinstance(res, str)
    assert "docs" in res
