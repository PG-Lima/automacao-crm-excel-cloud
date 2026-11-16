from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Page, async_playwright

from crm_cloud_demo.config import settings


@asynccontextmanager
async def browser_session() -> AsyncIterator[Page]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=settings.playwright_headless)

        context = await browser.new_context(accept_downloads=True)

        page = await context.new_page()
        page.set_default_timeout(settings.automation_timeout)

        try:
            yield page
        finally:
            await context.close()
            await browser.close()
