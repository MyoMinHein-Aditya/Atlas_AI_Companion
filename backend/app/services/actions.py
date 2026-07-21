import os
import logging
from typing import Dict, Any, Tuple
from fastapi import WebSocket
from app.services.system import system_service
from app.services.executor import execute_command, is_command_safe
from app.services.automation import take_screenshot, mouse_click
from app.services.browser import browser_service
from app.services.vision import vision_service
from app.services import db_service

logger = logging.getLogger("atlas-backend")

class ActionDispatcher:
    """Modular action dispatcher for Atlas execution pipeline."""

    async def handle_open_folder(self, action: Dict[str, Any]) -> str:
        """Handler for folder opening actions (<5 lines)."""
        path = action.get("path", "")
        return system_service.open_folder_in_explorer(path)

    async def handle_open_app(self, action: Dict[str, Any]) -> str:
        """Handler for system app launch actions (<5 lines)."""
        app_name = action.get("app", "")
        return system_service.launch_system_app(app_name)

    async def handle_focus_app(self, action: Dict[str, Any]) -> str:
        """Handler for window focus actions (<5 lines)."""
        name = action.get("name", "")
        success = system_service.focus_window_by_name(name)
        return f"Window '{name}' brought to view." if success else f"No window matching '{name}' found."

    async def handle_wifi_speed(self, action: Dict[str, Any]) -> str:
        """Handler for network speed testing actions (<5 lines)."""
        speed_res = await system_service.run_speed_test()
        summary = speed_res.get("summary", "Network test completed.")
        return f"Network Speed Test Completed — {summary}"

    async def handle_screenshot(self, action: Dict[str, Any]) -> str:
        """Handler for screen capturing (<5 lines)."""
        png_bytes = take_screenshot()
        os.makedirs("assets", exist_ok=True)
        with open("assets/screenshot.png", "wb") as f:
            f.write(png_bytes)
        return "Screen captured successfully and saved to assets/screenshot.png"

    async def handle_browser(self, action: Dict[str, Any]) -> str:
        """Handler for browser automation (<5 lines)."""
        url = action.get("url", "")
        await browser_service.navigate_to(url)
        return f"Browser navigated successfully to {url}"

    async def handle_click_element(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Handler for visual element clicking (<5 lines)."""
        description = action.get("description", "")
        png_bytes = take_screenshot()
        coords = await vision_service.locate_element(png_bytes, description)
        if coords:
            mouse_click(coords[0], coords[1])
            return True, f"Clicked element '{description}' at ({coords[0]}, {coords[1]})."
        return False, f"Failed to locate visual element '{description}' on screen."

    async def handle_read_screen_text(self, action: Dict[str, Any]) -> str:
        """Handler for OCR screen reading (<5 lines)."""
        png_bytes = take_screenshot()
        text = await vision_service.extract_screen_text(png_bytes)
        return f"OCR Text Extracted:\n{text[:300]}"

    async def dispatch(self, action: Dict[str, Any], websocket: WebSocket, step_idx: int, session_id: str, db: Any) -> Tuple[bool, str]:
        """Dispatches action dictionary to matching modular handler function."""
        action_type = action.get("type", "")
        logger.info(f"Dispatching action step {step_idx}: type='{action_type}'")

        if action_type == "open_folder":
            msg = await self.handle_open_folder(action)
            return True, msg

        elif action_type == "open_app":
            msg = await self.handle_open_app(action)
            return True, msg

        elif action_type == "focus_app":
            msg = await self.handle_focus_app(action)
            return True, msg

        elif action_type == "wifi_speed":
            msg = await self.handle_wifi_speed(action)
            return True, msg

        elif action_type == "screenshot":
            msg = await self.handle_screenshot(action)
            return True, msg

        elif action_type == "browser":
            msg = await self.handle_browser(action)
            return True, msg

        elif action_type == "click_element":
            return await self.handle_click_element(action)

        elif action_type == "read_screen_text":
            msg = await self.handle_read_screen_text(action)
            return True, msg

        elif action_type == "shell":
            command = action.get("command", "")
            is_safe_launch = command.strip().lower().startswith("start ") or is_command_safe(command)
            
            if is_safe_launch and command.strip().lower().startswith("start "):
                output = await execute_command(command)
                return True, f"Output:\n{output}"

            # Trigger security approval for sensitive shell scripts
            await websocket.send_json({"type": "approval_required", "command": command, "step": step_idx})
            approved = False
            while True:
                resp = await websocket.receive_json()
                if resp.get("type") == "approval_response":
                    approved = resp.get("approved", False)
                    break

            if approved:
                output = await execute_command(command)
                return True, f"Output:\n{output}"
            else:
                return False, "Script execution denied by user."

        return True, f"Unrecognized action type '{action_type}' skipped."

action_dispatcher = ActionDispatcher()
