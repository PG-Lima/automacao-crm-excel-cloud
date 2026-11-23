from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import Request

TRANSLATIONS = {
    "pt": {
        "html_lang": "pt-BR",
        "language_selector": "Idioma",
        "currency_prefix": "R$",
        "crm_login_title": "CRM Demo | Entrar",
        "crm_brand_subtitle": "Sistema de Gestão Comercial",
        "welcome_back": "Bem-vindo de volta",
        "crm_login_description": (
            "Entre na plataforma para acessar suas negociações e relatórios demonstrativos."
        ),
        "username": "Usuário",
        "username_placeholder": "Digite seu usuário",
        "password": "Senha",
        "password_placeholder": "Digite sua senha",
        "crm_login_button": "Entrar na plataforma",
        "crm_login_footer": "CRM Demonstrativo · Projeto de Portfólio",
        "local_demo": "Ambiente fictício e local",
        "invalid_credentials": "Usuário ou senha inválidos.",
        "crm_dashboard_title": "CRM Dashboard | Negociações",
        "main_menu": "MENU PRINCIPAL",
        "overview": "Visão geral",
        "crm_demo": "CRM Demonstrativo",
        "independent_project": "Projeto independente de portfólio",
        "overview_description": "Acompanhe as negociações e os resultados do CRM.",
        "demo_user": "Usuário demonstrativo",
        "logout": "Sair",
        "general_indicators": "Indicadores gerais",
        "total_deals": "Total de negociações",
        "period_records": "Registros no período selecionado",
        "total_deal_value": "Valor total das negociações",
        "fictional_values": "Valores fictícios de demonstração",
        "exchange_rate_note": (
            "Conversão de BRL para USD pela taxa de referência {rate} USD por BRL "
            "· Data da taxa: {date} · Fonte: Frankfurter."
        ),
        "exchange_rate_unavailable": (
            "A conversão para USD está temporariamente indisponível porque não foi possível "
            "consultar a taxa de referência."
        ),
        "dashboard_period": "Período do painel",
        "until": "Até",
        "recent_deals": "Negociações recentes",
        "crm_demo_data": "Dados fictícios do CRM demonstrativo",
        "start_date": "DATA INICIAL",
        "end_date": "DATA FINAL",
        "export_excel": "↓ Exportar Excel",
        "identifier": "Identificador",
        "company": "Empresa",
        "owner": "Responsável",
        "stage": "Etapa",
        "amount": "Valor (BRL)",
        "date": "Data",
        "stage_won": "Ganho",
        "stage_negotiation": "Em negociação",
        "stage_proposal": "Proposta enviada",
        "stage_lost": "Perdido",
        "stage_new": "Novo contato",
        "no_deals": "Nenhuma negociação encontrada para este período.",
        "crm_footer": "CRM Demonstrativo · Aplicação fictícia executada localmente",
        "invalid_dates": "Informe datas válidas no formato AAAA-MM-DD.",
        "start_after_end": "A data inicial não pode ser posterior à data final.",
        "cloud_login_title": "Entrar | Biblioteca Demo",
        "document_library": "Biblioteca de documentos",
        "cloud_login_description": (
            "Acesse o ambiente demonstrativo para armazenar e consultar relatórios."
        ),
        "cloud_login_button": "Entrar na biblioteca",
        "fictional_demo": "AMBIENTE FICTÍCIO · PROJETO DEMONSTRATIVO",
        "cloud_dashboard_title": "Biblioteca | Cloud Demo",
        "manage_stored_reports": "Gerencie os relatórios armazenados no ambiente demonstrativo.",
        "stored_documents": "Documentos armazenados",
        "accepted_format": "Formato aceito",
        "upload_document": "Enviar documento",
        "select_excel": "Selecione uma planilha Excel para armazenar na biblioteca.",
        "send_file": "Enviar arquivo",
        "recent_documents": "Documentos recentes",
        "upload_history": "Histórico dos arquivos enviados para a biblioteca.",
        "file": "Arquivo",
        "version": "Versão",
        "size": "Tamanho",
        "upload_date": "Data de envio",
        "no_documents": "Nenhum documento foi enviado ainda.",
        "documents_appear": "Os arquivos enviados aparecerão aqui.",
        "cloud_footer": "AMBIENTE FICTÍCIO · PROJETO DEMONSTRATIVO",
        "upload_success": "Upload concluído. Versão {version}",
        "file_missing": "Arquivo para upload não encontrado: {path}",
        "xlsx_only": "A automação aceita somente arquivos .xlsx.",
    },
    "en": {
        "html_lang": "en",
        "language_selector": "Language",
        "currency_prefix": "US$",
        "crm_login_title": "CRM Demo | Sign in",
        "crm_brand_subtitle": "Sales Management System",
        "welcome_back": "Welcome back",
        "crm_login_description": "Sign in to access your deals and demonstration reports.",
        "username": "Username",
        "username_placeholder": "Enter your username",
        "password": "Password",
        "password_placeholder": "Enter your password",
        "crm_login_button": "Sign in",
        "crm_login_footer": "Demo CRM · Portfolio Project",
        "local_demo": "Fictional local environment",
        "invalid_credentials": "Invalid username or password.",
        "crm_dashboard_title": "CRM Dashboard | Deals",
        "main_menu": "MAIN MENU",
        "overview": "Overview",
        "crm_demo": "Demo CRM",
        "independent_project": "Independent portfolio project",
        "overview_description": "Track deals and CRM performance.",
        "demo_user": "Demo user",
        "logout": "Sign out",
        "general_indicators": "Key metrics",
        "total_deals": "Total deals",
        "period_records": "Records in the selected period",
        "total_deal_value": "Total deal value",
        "fictional_values": "Fictional demonstration values",
        "exchange_rate_note": (
            "Converted from BRL at {rate} USD per BRL · Rate date: {date} "
            "· Source: Frankfurter."
        ),
        "exchange_rate_unavailable": (
            "USD conversion is temporarily unavailable because the reference exchange rate "
            "could not be retrieved."
        ),
        "dashboard_period": "Dashboard period",
        "until": "Through",
        "recent_deals": "Recent deals",
        "crm_demo_data": "Fictional data from the demo CRM",
        "start_date": "START DATE",
        "end_date": "END DATE",
        "export_excel": "↓ Export Excel",
        "identifier": "ID",
        "company": "Company",
        "owner": "Owner",
        "stage": "Stage",
        "amount": "Amount (USD)",
        "date": "Date",
        "stage_won": "Won",
        "stage_negotiation": "In negotiation",
        "stage_proposal": "Proposal sent",
        "stage_lost": "Lost",
        "stage_new": "New lead",
        "no_deals": "No deals were found for this period.",
        "crm_footer": "Demo CRM · Fictional application running locally",
        "invalid_dates": "Enter valid dates using the YYYY-MM-DD format.",
        "start_after_end": "The start date cannot be later than the end date.",
        "cloud_login_title": "Sign in | Demo Library",
        "document_library": "Document library",
        "cloud_login_description": "Access the demo environment to store and browse reports.",
        "cloud_login_button": "Sign in to the library",
        "fictional_demo": "FICTIONAL ENVIRONMENT · DEMONSTRATION PROJECT",
        "cloud_dashboard_title": "Library | Cloud Demo",
        "manage_stored_reports": "Manage reports stored in the demonstration environment.",
        "stored_documents": "Stored documents",
        "accepted_format": "Accepted format",
        "upload_document": "Upload document",
        "select_excel": "Choose an Excel spreadsheet to store in the library.",
        "send_file": "Upload file",
        "recent_documents": "Recent documents",
        "upload_history": "History of files uploaded to the library.",
        "file": "File",
        "version": "Version",
        "size": "Size",
        "upload_date": "Upload date",
        "no_documents": "No documents have been uploaded yet.",
        "documents_appear": "Uploaded files will appear here.",
        "cloud_footer": "FICTIONAL ENVIRONMENT · DEMONSTRATION PROJECT",
        "upload_success": "Upload completed. Version {version}",
        "file_missing": "File to upload was not found: {path}",
        "xlsx_only": "The automation only accepts .xlsx files.",
    },
}

ERROR_TRANSLATIONS = {
    "Informe datas válidas no formato AAAA-MM-DD.": "invalid_dates",
    "A data inicial não pode ser posterior à data final.": "start_after_end",
    "Nome de arquivo inválido.": "invalid_filename",
    "Somente arquivos .xlsx são permitidos.": "only_xlsx",
    "O arquivo está vazio.": "empty_file",
    "O arquivo ultrapassa o limite de 10 MB.": "file_too_large",
    "O arquivo não possui uma estrutura XLSX válida.": "invalid_xlsx",
    "O arquivo possui conteúdo excessivo.": "too_many_entries",
    "O conteúdo descompactado é muito grande.": "uncompressed_too_large",
    "Estrutura de planilha inválida.": "invalid_workbook_structure",
    "O arquivo possui conteúdo corrompido.": "corrupt_file",
    "A planilha não possui abas.": "no_sheets",
    "Não foi possível validar a planilha Excel.": "cannot_validate_excel",
}

TRANSLATIONS["en"].update({
    "invalid_filename": "Invalid filename.",
    "only_xlsx": "Only .xlsx files are allowed.",
    "empty_file": "The file is empty.",
    "file_too_large": "The file exceeds the 10 MB limit.",
    "invalid_xlsx": "The file does not have a valid XLSX structure.",
    "too_many_entries": "The file contains too many entries.",
    "uncompressed_too_large": "The uncompressed content is too large.",
    "invalid_workbook_structure": "Invalid spreadsheet structure.",
    "corrupt_file": "The file contains corrupted content.",
    "no_sheets": "The workbook does not contain any worksheets.",
    "cannot_validate_excel": "The Excel workbook could not be validated.",
})
TRANSLATIONS["pt"].update({
    "invalid_filename": "Nome de arquivo inválido.",
    "only_xlsx": "Somente arquivos .xlsx são permitidos.",
    "empty_file": "O arquivo está vazio.",
    "file_too_large": "O arquivo ultrapassa o limite de 10 MB.",
    "invalid_xlsx": "O arquivo não possui uma estrutura XLSX válida.",
    "too_many_entries": "O arquivo possui conteúdo excessivo.",
    "uncompressed_too_large": "O conteúdo descompactado é muito grande.",
    "invalid_workbook_structure": "Estrutura de planilha inválida.",
    "corrupt_file": "O arquivo possui conteúdo corrompido.",
    "no_sheets": "A planilha não possui abas.",
    "cannot_validate_excel": "Não foi possível validar a planilha Excel.",
})


def get_language(request: Request) -> str:
    language = request.session.get("language", "pt")
    return language if language in TRANSLATIONS else "pt"


def get_translations(language: str) -> dict[str, str]:
    return TRANSLATIONS.get(language, TRANSLATIONS["pt"])


def template_context(request: Request, **values: object) -> dict:
    language = get_language(request)
    return {"lang": language, "t": get_translations(language), **values}


def translate_error(message: str, language: str) -> str:
    key = ERROR_TRANSLATIONS.get(message)
    if not key:
        return message
    return get_translations(language).get(key, message)


def safe_next_path(next_path: str | None, fallback: str = "/") -> str:
    if not next_path or any(ord(char) < 32 or ord(char) == 127 for char in next_path):
        return fallback

    try:
        parsed = urlsplit(next_path)
    except ValueError:
        return fallback

    if (
        parsed.scheme
        or parsed.netloc
        or not parsed.path.startswith("/")
        or parsed.path.startswith("//")
        or "\\" in parsed.path
    ):
        return fallback

    return next_path
