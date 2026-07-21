import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.ai import AIService

@pytest.mark.asyncio
async def test_groq_planning_success():
    service = AIService()
    
    # Mock response format returned by Groq Completion
    mock_choice = MagicMock()
    mock_choice.message.content = '{"response": "Executing task", "actions": [{"type": "screenshot"}]}'
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_completions = MagicMock()
    mock_completions.create = AsyncMock(return_value=mock_response)
    
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions = mock_completions
    service.groq_client = mock_groq_client
    
    # Execute plan generator
    plan = await service.generate_response_and_plan("Take a screenshot", [])
    
    assert plan["response"] == "Executing task"
    assert len(plan["actions"]) == 1
    assert plan["actions"][0]["type"] == "screenshot"
