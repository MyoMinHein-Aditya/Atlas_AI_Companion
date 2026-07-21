import base64
import logging
import json
from typing import Tuple, Optional
from groq import AsyncGroq
from app.config import settings

logger = logging.getLogger("atlas-backend")

class VisionService:
    def __init__(self):
        self.groq_client = None
        if settings.groq_api_key:
            try:
                logger.info("Initializing Groq Async Client for vision analysis.")
                self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client in VisionService: {str(e)}")
        else:
            logger.warning("GROQ_API_KEY is not configured for VisionService.")

    async def analyze_screenshot(self, image_bytes: bytes, prompt: str) -> str:
        """Transmits the captured image to Groq Vision model and returns text analysis."""
        if not self.groq_client:
            return "Configuration Error: GROQ_API_KEY is not set."

        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        try:
            logger.info("Requesting screen analysis from Groq Vision...")
            response = await self.groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq Vision analysis call failed: {str(e)}")
            return f"Vision Service error: {str(e)}"

    async def locate_element(self, image_bytes: bytes, description: str) -> Optional[Tuple[int, int]]:
        """Resolves the center coordinate (x, y) of an element in the screen image using Groq Vision."""
        if not self.groq_client:
            logger.error("Groq client not configured for locate_element.")
            return None

        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        locate_prompt = (
            "Analyze the provided screenshot of the computer screen. "
            f"Locate the center point of the following element: '{description}'. "
            "You MUST respond ONLY with a JSON object. Do not add markdown wrappers. "
            "The JSON object must contain coordinates x and y matching this schema: "
            "{\"x\": integer, \"y\": integer}. "
            "Ensure the coordinates map to the actual pixel location in the image."
        )

        try:
            logger.info(f"Locating screen element '{description}' via Groq Vision...")
            response = await self.groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": locate_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )

            raw_content = response.choices[0].message.content.strip()
            parsed = json.loads(raw_content)
            x = parsed.get("x")
            y = parsed.get("y")
            if x is not None and y is not None:
                logger.info(f"Resolved element coordinates: ({x}, {y})")
                return int(x), int(y)
        except Exception as e:
            logger.error(f"Failed to resolve element coordinates via Groq Vision: {str(e)}")

        return None

# Global shared instance
vision_service = VisionService()
