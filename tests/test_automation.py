import sys
import os
import pytest

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.executor import execute_command, is_command_safe

def test_command_safety_scanner():
    # Safe commands
    assert is_command_safe("python --version") is True
    assert is_command_safe("pip install pytest") is True
    assert is_command_safe("echo 'hello world'") is True
    
    # Dangerous commands (matched by keyword blacklist)
    assert is_command_safe("rm -rf /") is False
    assert is_command_safe("del /q /s *") is False
    assert is_command_safe("format c:") is False
    assert is_command_safe("remove-item -recurse -force .") is False

@pytest.mark.asyncio
async def test_async_shell_execution():
    # Verify that a basic shell echo command runs successfully and returns output
    output = await execute_command("echo HelloAtlas")
    assert "HelloAtlas" in output
