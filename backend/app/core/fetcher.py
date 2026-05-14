import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

FETCH_TIMEOUT = 15.0


@dataclass
class FetchedPage:
    url: str
    text: str
    screenshot_bytes: bytes | None


async def fetch(url: str) -> FetchedPage:
    text = await _fetch_text(url)
    screenshot = await _screenshot(url)
    return FetchedPage(url=url, text=text, screenshot_bytes=screenshot)


async def _fetch_text(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=FETCH_TIMEOUT) as client:
        resp = await client.get(url, headers={"User-Agent": "ai-slop-bot/1.0"})
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)[:8000]  # cap to avoid huge prompts


async def _screenshot(url: str) -> bytes | None:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=int(FETCH_TIMEOUT * 1000), wait_until="domcontentloaded")
            data = await page.screenshot(full_page=False, type="png")
            await browser.close()
            return data
    except Exception:
        logger.warning("Screenshot failed for %s — continuing with text only", url, exc_info=True)
        return None
