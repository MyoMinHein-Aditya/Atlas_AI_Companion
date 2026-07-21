import logging
import mss
import pyautogui
from PIL import Image
from io import BytesIO

# Configure PyAutoGUI Failsafe: moving cursor to any extreme corner aborts execution
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

logger = logging.getLogger("atlas-backend")

def take_screenshot() -> bytes:
    """Grabs primary display screen pixels and returns PNG bytes."""
    logger.info("Capturing desktop screen...")
    try:
        with mss.mss() as sct:
            # Index 1 is the primary monitor screen
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            
            # Convert raw BGRA pixels to PIL RGB
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            output_buffer = BytesIO()
            img.save(output_buffer, format="PNG")
            logger.info("Screen screenshot taken successfully.")
            return output_buffer.getvalue()
    except Exception as e:
        logger.error(f"Desktop screenshot capture failed: {str(e)}")
        raise e

def mouse_click(x: int, y: int):
    """Fires mouse click event at x, y pixels."""
    logger.info(f"Emulating mouse click at screen pixels: ({x}, {y})")
    pyautogui.click(x, y)

def keyboard_type(text: str):
    """Emulates keyboard string key inputs."""
    logger.info(f"Emulating keyboard text inputs: '{text[:30]}...'")
    pyautogui.write(text, interval=0.01)

def keyboard_press(key: str):
    """Emulates singular key taps (e.g. 'enter', 'tab')."""
    logger.info(f"Emulating keyboard hotkey tap: '{key}'")
    pyautogui.press(key)
