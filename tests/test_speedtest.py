import sys
import os
import pytest

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.system import system_service

@pytest.mark.asyncio
async def test_speed_test_execution():
    result = await system_service.run_speed_test()
    assert "ping_ms" in result
    assert "download_mbps" in result
    assert "upload_mbps" in result
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert result["download_mbps"] >= 0
