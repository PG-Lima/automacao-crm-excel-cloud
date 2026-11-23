import asyncio

from crm_cloud_demo.logging_config import configure_logging

from .browser import browser_session
from .cloud import login_to_cloud, upload_to_cloud
from .crm import download_crm_report, login_to_crm


async def run_automation() -> None:
    logger = configure_logging()
    logger.info("Iniciando automação.")

    try:
        async with browser_session() as page:
            logger.info("[1/4] Acessando o CRM.")
            await login_to_crm(page)
            logger.info("Login no CRM realizado.")

            logger.info("[2/4] Exportando relatório.")
            report_path = await download_crm_report(page)
            logger.info(
                "Relatório baixado: %s (%s bytes).",
                report_path.name,
                report_path.stat().st_size,
            )

            logger.info("[3/4] Acessando a biblioteca.")
            await login_to_cloud(page)
            logger.info("Login na biblioteca realizado.")

            logger.info("[4/4] Enviando relatório.")
            result = await upload_to_cloud(page, report_path)
            logger.info("Resultado do upload: %s", result)

    except Exception as exc:
        logger.error("Automação falhou (%s).", type(exc).__name__)
        raise

    logger.info("Automação finalizada com sucesso.")


if __name__ == "__main__":
    asyncio.run(run_automation())
