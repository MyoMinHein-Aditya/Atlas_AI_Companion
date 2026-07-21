import sys
import os
from fastapi.testclient import TestClient

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.main import app
from app.services.system import system_service

client = TestClient(app)

def test_system_metrics():
    metrics = system_service.get_system_metrics()
    assert "cpu_percent" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert isinstance(metrics["cpu_percent"], float) or isinstance(metrics["cpu_percent"], int)
    assert metrics["memory"]["total_gb"] >= 0

def test_active_window():
    window_info = system_service.get_active_window()
    assert "title" in window_info
    assert "process" in window_info
    assert isinstance(window_info["title"], str)

def test_system_context_endpoint():
    response = client.get("/api/system/context")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "active_window" in data
    assert "os" in data
