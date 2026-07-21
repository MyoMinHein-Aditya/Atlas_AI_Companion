import logging
import json
from typing import Dict, Any
from groq import AsyncGroq
from app.config import settings

logger = logging.getLogger("atlas-backend")

SYSTEM_PROMPT = """You are Atlas, a next-generation intelligent desktop operating companion.
You reside on the user's computer. You are direct, smart, and helpful.

You must respond STRICTLY in a valid JSON format.
Do not add markdown wraps like ```json or ``` in your output. Just return the raw JSON object.

The JSON schema must be exactly:
{
  "response": "Your conversational text response or explanation here.",
  "actions": [
     // List of actions to execute in order. Leave empty [] if no actions are needed.
     // Valid action structures:
     // 1. Shell commands:
     //    { "type": "shell", "command": "python --version" }
     // 2. Desktop screen capture:
     //    { "type": "screenshot" }
     // 3. Web automation:
     //    { "type": "browser", "url": "https://news.ycombinator.com" }
     // 4. Extract screen text (OCR):
     //    { "type": "read_screen_text" }
     // 5. Visual element click:
     //    { "type": "click_element", "description": "The center of the blue login button" }
  ]
}

Example user prompt: "Check python version"
Example response:
{
  "response": "Checking the current Python version on your system.",
  "actions": [
    { "type": "shell", "command": "python --version" }
  ]
}
"""

class AIService:
  def __init__(self):
    self.groq_client = None

    # Initialize Groq Client
    if settings.groq_api_key:
      try:
        logger.info("Initializing Groq Async Client for plans.")
        self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
      except Exception as e:
        logger.error(f"Failed to initialize Groq client: {str(e)}")
    else:
      logger.warning("GROQ_API_KEY is not configured in local environment.")

  async def generate_response_and_plan(self, prompt: str, history: list) -> Dict[str, Any]:
    """Queries Groq Llama 3.3 to obtain conversational response and structured action logs."""
    raw_content = ""

    if self.groq_client:
      try:
        logger.info("Requesting plan from Groq (Llama-3.3).")
        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
          role = "user" if msg.get("sender") == "user" else "assistant"
          content = msg.get("content", "")
          if content:
            formatted_messages.append({"role": role, "content": content})
        
        formatted_messages.append({"role": "user", "content": prompt})

        response = await self.groq_client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=formatted_messages,
          response_format={"type": "json_object"},
          temperature=0.2,
        )

        raw_content = response.choices[0].message.content.strip()
      except Exception as e:
        logger.error(f"Groq plan request failed: {str(e)}")
        return {
          "response": f"AI service error during Groq completion call: {str(e)}",
          "actions": []
        }
    else:
      return {
        "response": "Configuration Error: GROQ_API_KEY is missing or unconfigured.",
        "actions": []
      }

    # Parse JSON
    if raw_content:
      try:
        # Strip markdown syntax wraps if the model returned them
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
        raw_content = raw_content.strip()

        parsed = json.loads(raw_content)
        if "response" in parsed and "actions" in parsed:
          return parsed
      except Exception as e:
        logger.error(f"Failed to parse AI plan JSON. Raw output was: {raw_content}. Error: {str(e)}")

    return {
      "response": "I received an invalid payload structure from the AI service.",
      "actions": []
    }

# Global singleton
ai_service = AIService()
