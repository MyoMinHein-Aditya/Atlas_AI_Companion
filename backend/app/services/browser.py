import logging
from playwright.async_api import async_playwright

logger = logging.getLogger("atlas-backend")

class BrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self, headless: bool = False):
        """Initializes a new Playwright Chromium instance."""
        logger.info("Starting Playwright Chromium browser driver...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        self.context = await self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = await self.context.new_page()
        logger.info("Playwright browser driver ready.")

    async def navigate_to(self, url: str):
        """Navigates to URL, waiting for network to be idle."""
        if not self.page:
            await self.start()
        logger.info(f"Browser navigating to: {url}")
        await self.page.goto(url, wait_until="networkidle", timeout=15000)

    async def click_element(self, selector: str):
        """Clicks element matching CSS selector."""
        if not self.page:
            raise Exception("Browser page is not instantiated.")
        logger.info(f"Browser clicking element selector: '{selector}'")
        await self.page.click(selector, timeout=5000)

    async def fill_field(self, selector: str, text: str):
        """Fills input text inside the matched element selector."""
        if not self.page:
            raise Exception("Browser page is not instantiated.")
        logger.info(f"Browser inputting text to selector '{selector}'")
        await self.page.fill(selector, text, timeout=5000)

    async def scrape_text(self) -> str:
        """Extracts plain text contents from web page body."""
        if not self.page:
            return ""
        logger.info("Scraping page inner text...")
        return await self.page.inner_text("body")

    async def close(self):
        """Clean teardown of all browser connection structures."""
        logger.info("Teardown Playwright browser processes...")
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Browser teardown exception: {str(e)}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            logger.info("Browser processes terminated.")

# Global shared instance
browser_service = BrowserAutomation()
