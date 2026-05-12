import asyncio
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("browser")


class BrowserController:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._page = None

    async def _ensure_browser(self):
        if self._browser is None:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=False)
            self._page = await self._browser.new_page()

    async def open_url(self, url: str) -> bool:
        try:
            await self._ensure_browser()
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            await self._page.goto(url)
            logger.info(f"Opened URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to open {url}: {e}")
            return False

    async def search(self, query: str, engine: str = "google") -> bool:
        urls = {
            "google": f"https://www.google.com/search?q={query}",
            "yandex": f"https://yandex.ru/search/?text={query}",
            "bing": f"https://www.bing.com/search?q={query}",
        }
        url = urls.get(engine, urls["google"])
        return await self.open_url(url)

    async def scrape(self, url: str, selector: str | None = None) -> str:
        try:
            await self._ensure_browser()
            await self._page.goto(url, wait_until="domcontentloaded")
            if selector:
                elements = await self._page.query_selector_all(selector)
                texts = [await el.inner_text() for el in elements if el]
                return "\n".join(texts[:50])
            return await self._page.content()
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ""

    async def screenshot(self, url: str, path: str | None = None) -> str | None:
        try:
            await self._ensure_browser()
            await self._page.goto(url, wait_until="domcontentloaded")
            if path is None:
                path = str(Path.home() / "Pictures" / f"jarvis_browser_{url.split('//')[1].split('/')[0]}.png")
            await self._page.screenshot(path=path, full_page=True)
            logger.info(f"Browser screenshot: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to screenshot {url}: {e}")
            return None

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
