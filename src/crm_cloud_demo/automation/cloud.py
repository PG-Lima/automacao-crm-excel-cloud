from pathlib import Path

from playwright.async_api import Page

from crm_cloud_demo.config import settings


async def login_to_cloud(page: Page) -> None:
    await page.goto(
        f"{settings.cloud_base_url}/login",
        wait_until="domcontentloaded",
    )

    await page.locator('input[name="username"]').fill(settings.cloud_demo_username)

    await page.locator('input[name="password"]').fill(settings.cloud_demo_password)

    await page.locator('form[action="/login"] button[type="submit"]').click()

    await page.wait_for_url(
        lambda url: "/login" not in url,
        timeout=settings.automation_timeout,
    )


async def upload_to_cloud(
    page: Page,
    file_path: Path,
) -> str:
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Arquivo para upload não encontrado: {file_path}")

    if file_path.suffix.lower() != ".xlsx":
        raise ValueError("A automação aceita somente arquivos .xlsx.")

    await page.goto(
        settings.cloud_base_url,
        wait_until="domcontentloaded",
    )

    file_input = page.locator('input[type="file"][name="file"]')
    await file_input.set_input_files(str(file_path))

    await page.locator('form[action="/upload"] button[type="submit"]').click()

    success_message = page.locator(".message.success")
    await success_message.wait_for(
        state="visible",
        timeout=settings.automation_timeout,
    )

    return (await success_message.inner_text()).strip()
