import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.vision import VisionService

@pytest.mark.asyncio
async def test_locate_element_success():
    service = VisionService()
    
    # Mock coordinates returned in JSON format from Vision LLM
    mock_choice = MagicMock()
    mock_choice.message.content = '{"x": 640, "y": 360}'
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_completions = MagicMock()
    mock_completions.create = AsyncMock(return_value=mock_response)
    
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions = mock_completions
    service.groq_client = mock_groq_client
    
    coords = await service.locate_element(b"dummy_bytes", "The blue settings icon")
    assert coords == (640, 360)

@pytest.mark.asyncio
async def test_analyze_screenshot_success():
    service = VisionService()
    
    # Mock text block analysis returned by Vision LLM
    mock_choice = MagicMock()
    mock_choice.message.content = "Extracted Text:\nHello World"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_completions = MagicMock()
    mock_completions.create = AsyncMock(return_value=mock_response)
    
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions = mock_completions
    service.groq_client = mock_groq_client
    
    text = await service.analyze_screenshot(b"dummy_bytes", "Extract all text")
    assert text == "Extracted Text:\nHello World"
