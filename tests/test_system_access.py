import sys
import os

# Add backend to path so we can import app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.system import system_service

def test_find_local_folder_existing():
    # Searching for known local root folder like 'backend' or 'frontend' or 'docs'
    root_docs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
    found = system_service.find_local_folder("docs")
    assert found is not None
    assert os.path.exists(found)

def test_list_running_applications():
    apps = system_service.list_running_applications()
    assert isinstance(apps, list)
    assert len(apps) > 0

def test_open_folder_in_explorer_service():
    result = system_service.open_folder_in_explorer("docs")
    assert isinstance(result, str)
    assert "Opened folder" in result or "docs" in result
