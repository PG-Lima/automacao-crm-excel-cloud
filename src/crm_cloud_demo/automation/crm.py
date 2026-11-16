from pathlib import Path

from playwright.async_api import Page

from crm_cloud_demo.config import PROJECT_ROOT, settings


async def login_to_crm(page: Page) -> None:
    await page.goto(
        f"{settings.crm_base_url}/login",
        wait_until="domcontentloaded",
    )

    await page.locator('input[name="username"]').fill(settings.crm_demo_username)

    await page.locator('input[name="password"]').fill(settings.crm_demo_password)

    await page.locator('form[action="/login"] button[type="submit"]').click()

    await page.wait_for_url(
        lambda url: "/login" not in url,
        timeout=settings.automation_timeout,
    )


async def download_crm_report(page: Page) -> Path:
    download_dir = PROJECT_ROOT / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)

    export_button = page.locator("form.export-form button.export-button")

    if await export_button.count() == 0:
        raise RuntimeError("O botão de exportação não foi encontrado no CRM.")

    async with page.expect_download() as download_info:
        await export_button.click()

    download = await download_info.value

    filename = Path(download.suggested_filename).name
    destination = download_dir / filename

    await download.save_as(destination)

    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError("O arquivo Excel não foi baixado corretamente.")

    return destination
