# CRM → Excel → Cloud Automation | Automação CRM → Excel → Cloud

🇧🇷 **Desenvolvido de forma independente no Brasil.**  
🌎 **Independently developed in Brazil.**

[Português](#português) · [English](#english)

---

## Português

Projeto independente de portfólio que demonstra a automação de um processo de transferência de relatórios entre duas aplicações web fictícias: um CRM e uma biblioteca de documentos.

A solução utiliza Python e Playwright para controlar o navegador, gerar e baixar um relatório Excel no CRM demonstrativo e, em seguida, enviá-lo à aplicação Cloud Library.

O projeto foi desenvolvido para fins educacionais, prática de desenvolvimento de software e construção de portfólio. As aplicações são fictícias, executadas localmente e utilizam dados sintéticos.

### Demonstração do fluxo

1. A automação abre o CRM demonstrativo utilizando Chromium.
2. Realiza a autenticação no CRM.
3. Solicita a exportação de um relatório de negociações.
4. Baixa o arquivo Excel.
5. Acessa a Cloud Library.
6. Realiza uma segunda autenticação, independente da primeira.
7. Envia o relatório para armazenamento.
8. Aguarda a confirmação do upload e da versão do documento.

**Status publicado:** o fluxo principal foi implementado e executado com sucesso em ambiente local.

### Arquitetura

O projeto possui três componentes independentes:

**1. CRM demonstrativo**

Aplicação web desenvolvida com FastAPI. Disponibiliza autenticação local, dados comerciais fictícios, consulta de negociações por período e exportação de relatórios Excel.

**2. Cloud Library**

Aplicação web independente que simula uma biblioteca de documentos. Possui autenticação própria, recebe arquivos `.xlsx`, valida os documentos, armazena os arquivos localmente e registra metadados e histórico de versões em SQLite.

**3. Robô de automação**

Implementado em Python com Playwright. Controla o navegador Chromium, realiza login nas duas aplicações, baixa o relatório e envia o arquivo por meio da interface web.

### Tecnologias utilizadas

| Tecnologia | Função no projeto |
|---|---|
| Python 3.14+ | Linguagem principal da solução |
| Playwright | Automação do navegador |
| FastAPI | Desenvolvimento das aplicações web |
| Uvicorn | Servidor ASGI |
| openpyxl | Geração e manipulação de arquivos Excel |
| SQLite | Persistência de metadados e histórico de versões |
| Jinja2 | Templates HTML |
| python-dotenv | Carregamento de configurações por variáveis de ambiente |
| pytest | Framework declarado para testes no ambiente de desenvolvimento |
| Ruff | Análise e padronização do código |
| Git | Controle de versão |

### Estrutura do projeto

```text
automacao-crm-excel-cloud/
├── src/
│   └── crm_cloud_demo/
│       ├── apps/
│       │   ├── crm/
│       │   │   ├── templates/
│       │   │   ├── app.py
│       │   │   ├── routes.py
│       │   │   └── services.py
│       │   └── cloud/
│       │       ├── templates/
│       │       ├── app.py
│       │       ├── routes.py
│       │       └── storage.py
│       ├── automation/
│       │   ├── browser.py
│       │   ├── crm.py
│       │   ├── cloud.py
│       │   └── run.py
│       ├── services/
│       ├── config.py
│       └── logging_config.py
├── docs/
│   ├── architecture.md
│   ├── architecture.en.md
│   ├── security.md
│   └── security.en.md
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### Requisitos

- Windows 11 ou sistema compatível com Python.
- Python 3.14 ou superior.
- Git.
- Chromium instalado pelo Playwright.

### Instalação

Clone este repositório:

```powershell
git clone https://github.com/PG-Lima/automacao-crm-excel-cloud.git
cd automacao-crm-excel-cloud
```

Crie e ative um ambiente virtual:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale o projeto e as dependências de desenvolvimento:

```powershell
python -m pip install -e ".[dev]"
```

Instale o Chromium:

```powershell
playwright install chromium
```

### Configuração

Crie o arquivo `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
```

As configurações incluem endereços locais, credenciais fictícias, diretórios de armazenamento, opções do navegador, limites de tempo e parâmetros de log.

**Utilize somente as credenciais fictícias de demonstração. Não informe senhas reais.**

### Execução

São necessários três terminais PowerShell.

**Terminal 1 — CRM**

```powershell
python -m uvicorn crm_cloud_demo.apps.crm.app:app --host 127.0.0.1 --port 8000 --reload
```

Acesse: http://127.0.0.1:8000/login

**Terminal 2 — Cloud Library**

```powershell
python -m uvicorn crm_cloud_demo.apps.cloud.app:app --host 127.0.0.1 --port 8001 --reload
```

Acesse: http://127.0.0.1:8001/login

**Terminal 3 — Robô de automação**

```powershell
python -m crm_cloud_demo.automation.run
```

O robô utiliza as configurações definidas no arquivo `.env` para acessar as duas aplicações.

### Testes

O `pytest` está declarado como dependência de desenvolvimento. **A versão atualmente publicada neste repositório ainda não inclui os arquivos da suíte de testes automatizados.** A documentação do status dos testes deve acompanhar a publicação desses arquivos.

### Segurança e escopo

O projeto é uma simulação local e independente. Entre as medidas documentadas estão:

- Utilização de dados comerciais sintéticos e credenciais fictícias.
- Aplicações e sessões independentes.
- Servidores iniciados no endereço local `127.0.0.1`.
- Proteção de arquivos locais pelo `.gitignore`.
- Validação de arquivos Excel recebidos e limites de tamanho e conteúdo.
- Armazenamento com identificadores únicos, metadados, hashes SHA-256 e histórico de versões.
- Ausência de integração com sistemas corporativos reais.

O projeto é educacional e **não deve ser considerado uma aplicação pronta para produção**. Consulte a [Política de Segurança](docs/security.md).

### Próximas melhorias

- Publicar e manter a suíte de testes unitários e de integração no repositório.
- Aprimorar o tratamento de exceções e falhas.
- Integrar o módulo de logs ao fluxo principal.
- Adicionar evidências visuais e relatórios estruturados de execução.
- Avaliar a execução programada pelo Agendador de Tarefas do Windows.
- Continuar a revisão de segurança e documentação.

### Objetivo profissional

Este projeto faz parte do meu desenvolvimento prático em automação de processos, Python, desenvolvimento web, automação de navegadores, manipulação de dados e Excel e segurança da informação.

**Desenvolvido de forma independente no Brasil, com aplicações fictícias e infraestrutura local, para fins educacionais e de portfólio profissional.**

Documentação: [Arquitetura — PT-BR](docs/architecture.md) · [Architecture — EN](docs/architecture.en.md) · [Segurança — PT-BR](docs/security.md) · [Security — EN](docs/security.en.md)

---

## English

An independent portfolio project demonstrating the automation of a report-transfer workflow between two fictional web applications: a CRM and a document library.

The solution uses Python and Playwright to control a browser, generate and download an Excel report from the demo CRM, and then upload it to the Cloud Library application.

This project was built for educational purposes, software development practice, and portfolio development. Both applications are fictional, run locally, and use synthetic data.

### Workflow demonstration

1. The automation opens the demo CRM using Chromium.
2. It authenticates with the CRM.
3. It requests the export of a deals report.
4. It downloads the Excel file.
5. It opens the Cloud Library.
6. It performs a second authentication, independent from the first one.
7. It uploads the report for storage.
8. It waits for confirmation of the upload and document version.

**Published status:** the main workflow has been implemented and successfully executed in a local environment.

### Architecture

The project has three independent components:

**1. Demo CRM**

A web application built with FastAPI. It provides local authentication, fictional business data, date-based deal queries, and Excel report exports.

**2. Cloud Library**

An independent web application that simulates a document library. It has its own authentication, accepts `.xlsx` files, validates documents, stores files locally, and records metadata and version history in SQLite.

**3. Automation robot**

Implemented in Python with Playwright. It controls the Chromium browser, logs in to both applications, downloads the report, and uploads the file through the web interface.

### Technology stack

| Technology | Role in the project |
|---|---|
| Python 3.14+ | Main programming language |
| Playwright | Browser automation |
| FastAPI | Web application development |
| Uvicorn | ASGI server |
| openpyxl | Excel file generation and manipulation |
| SQLite | Metadata and document version-history persistence |
| Jinja2 | HTML templates |
| python-dotenv | Environment-based configuration loading |
| pytest | Test framework declared for the development environment |
| Ruff | Code linting and formatting checks |
| Git | Version control |

### Project structure

```text
automacao-crm-excel-cloud/
├── src/
│   └── crm_cloud_demo/
│       ├── apps/
│       │   ├── crm/
│       │   │   ├── templates/
│       │   │   ├── app.py
│       │   │   ├── routes.py
│       │   │   └── services.py
│       │   └── cloud/
│       │       ├── templates/
│       │       ├── app.py
│       │       ├── routes.py
│       │       └── storage.py
│       ├── automation/
│       │   ├── browser.py
│       │   ├── crm.py
│       │   ├── cloud.py
│       │   └── run.py
│       ├── services/
│       ├── config.py
│       └── logging_config.py
├── docs/
│   ├── architecture.md
│   ├── architecture.en.md
│   ├── security.md
│   └── security.en.md
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### Requirements

- Windows 11 or an operating system compatible with Python.
- Python 3.14 or later.
- Git.
- Chromium installed through Playwright.

### Installation

Clone this repository:

```powershell
git clone https://github.com/PG-Lima/automacao-crm-excel-cloud.git
cd automacao-crm-excel-cloud
```

Create and activate a virtual environment:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Install Chromium:

```powershell
playwright install chromium
```

### Configuration

Create the `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Configuration includes local application addresses, fictional credentials, storage directories, browser options, operation timeouts, and logging settings.

**Use only the fictional demonstration credentials. Do not enter real passwords.**

### Running the project

Three PowerShell terminals are required.

**Terminal 1 — CRM**

```powershell
python -m uvicorn crm_cloud_demo.apps.crm.app:app --host 127.0.0.1 --port 8000 --reload
```

Open: http://127.0.0.1:8000/login

**Terminal 2 — Cloud Library**

```powershell
python -m uvicorn crm_cloud_demo.apps.cloud.app:app --host 127.0.0.1 --port 8001 --reload
```

Open: http://127.0.0.1:8001/login

**Terminal 3 — Automation robot**

```powershell
python -m crm_cloud_demo.automation.run
```

The robot uses the settings defined in the `.env` file to access both applications.

### Tests

`pytest` is declared as a development dependency. **The version currently published in this repository does not yet include the automated test-suite files.** The test status documentation should be updated when those files are published.

### Security and scope

This project is an independent local simulation. The documented measures include:

- Synthetic business data and fictional credentials.
- Independent applications and sessions.
- Servers bound to the local address `127.0.0.1`.
- Local file protection through `.gitignore`.
- Validation of received Excel files and file-size and content limits.
- Storage with unique identifiers, metadata, SHA-256 hashes, and version history.
- No integration with real corporate systems.

This is an educational project and **must not be considered production-ready software**. See the [Security Policy](docs/security.en.md).

### Planned improvements

- Publish and maintain the unit and integration test suite in the repository.
- Improve exception and failure handling.
- Integrate the logging module into the main workflow.
- Add visual evidence and structured execution reports.
- Evaluate scheduled execution through Windows Task Scheduler.
- Continue security and documentation reviews.

### Professional development goals

This project supports my hands-on development in process automation, Python, web development, browser automation, data and Excel manipulation, and information security.

**Independently developed in Brazil using fictional applications and local infrastructure for educational and professional portfolio purposes.**

Documentation: [Architecture — EN](docs/architecture.en.md) · [Arquitetura — PT-BR](docs/architecture.md) · [Security — EN](docs/security.en.md) · [Segurança — PT-BR](docs/security.md)
