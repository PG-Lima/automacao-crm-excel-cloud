import asyncio

from .browser import browser_session
from .cloud import login_to_cloud, upload_to_cloud
from .crm import download_crm_report, login_to_crm


async def run_automation() -> None:
    print("Iniciando automação...")

    async with browser_session() as page:
        print("\n[1/4] Acessando o CRM...")
        await login_to_crm(page)
        print("Login no CRM realizado.")

        print("\n[2/4] Exportando relatório...")
        report_path = await download_crm_report(page)
        print(f"Relatório baixado: {report_path.name}")

        print("\n[3/4] Acessando a biblioteca...")
        await login_to_cloud(page)
        print("Login na biblioteca realizado.")

        print("\n[4/4] Enviando relatório...")
        result = await upload_to_cloud(page, report_path)
        print(f"Resultado: {result}")

    print("\nAutomação finalizada com sucesso!")


if __name__ == "__main__":
    asyncio.run(run_automation())
