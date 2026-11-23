# CRM → Excel → Cloud Automation | Automação CRM → Excel → Cloud

🇧🇷 **Desenvolvido de forma independente no Brasil.**  
🌎 **Independently developed in Brazil.**

[Português](#português) · [English](#english)

---

## Português

Este projeto tem **dois objetivos igualmente importantes: ser um portfólio de desenvolvimento e um recurso de aprendizagem aberto**.

Como portfólio, demonstra como identifiquei um problema, escolhi tecnologias e desenvolvi uma solução de automação de ponta a ponta. Como material didático, busca ajudar quem enfrenta um desafio semelhante a entender o processo, reproduzir a solução e adaptá-la à própria realidade.

O cenário é a transferência automatizada de relatórios entre duas aplicações web fictícias: um CRM e uma biblioteca de documentos. A solução utiliza Python e Playwright para controlar o navegador, gerar e baixar um relatório Excel no CRM demonstrativo e, em seguida, enviá-lo à aplicação Cloud Library.

As aplicações são fictícias, executadas localmente e utilizam dados sintéticos. A proposta não é apenas entregar um código pronto, mas compartilhar o caminho, as decisões técnicas e o conhecimento necessário para que outras pessoas aprendam com ele.

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

Aplicação web desenvolvida com FastAPI. Disponibiliza interface em português e inglês, autenticação local, dados comerciais fictícios, consulta de negociações por período e exportação de relatórios Excel no idioma selecionado.

**2. Cloud Library**

Aplicação web independente que simula uma biblioteca de documentos. Possui interface em português e inglês, autenticação própria, recebe arquivos `.xlsx`, valida os documentos, armazena os arquivos localmente e registra metadados e histórico de versões em SQLite.

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
| Frankfurter API | Taxa de referência para conversão BRL/USD na interface inglesa |
| SQLite | Persistência de metadados e histórico de versões |
| Jinja2 | Templates HTML |
| python-dotenv | Carregamento de configurações por variáveis de ambiente |
| pytest / pytest-cov | Testes unitários, integração e E2E com relatório de cobertura |
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
│       ├── currency.py
│       ├── localization.py
│       └── logging_config.py
├── tests/
│   ├── unit/
│   │   ├── test_localization.py
│   │   ├── test_bilingual_report.py
│   │   └── ...
│   ├── integration/
│   │   └── test_web_apps.py
│   └── e2e/
│       └── test_browser_workflow.py
├── docs/
│   ├── architecture.md
│   ├── architecture.en.md
│   ├── learning-guide.md
│   ├── learning-guide.en.md
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

Instale o Chromium no diretório de navegadores do projeto:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
python -m playwright install chromium
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

**Idioma e moeda:** nas telas de login e nos painéis do CRM e da Cloud Library, utilize o seletor `PT-BR / EN` para alternar o idioma. Cada aplicação mantém sua própria preferência durante a sessão. No modo PT-BR, os valores são exibidos em BRL. No modo EN, os valores são convertidos de BRL para USD usando a taxa de referência mais recente consultada na API Frankfurter; a data da taxa e a fonte são informadas no painel e no Excel. Os registros originais continuam armazenados em BRL. A versão inglesa precisa de conexão com a internet para consultar a taxa; se a API estiver indisponível, a tela sinaliza o problema em vez de exibir uma conversão inventada.

### Testes

O `pytest` e o `pytest-cov` são dependências de desenvolvimento. A suíte está organizada em três níveis:

- `tests/unit/`: regras de configuração, localização, conversão cambial, geração do Excel, armazenamento, logging e funções do robô.
- `tests/integration/`: autenticação, rotas, exportação do CRM, upload da Cloud Library, persistência e histórico de versões.
- `tests/e2e/`: execução real do robô com Chromium e Playwright, desde o login no CRM até a confirmação do arquivo armazenado na biblioteca.

Com o ambiente virtual ativado e o Chromium instalado, execute a suíte completa e a análise de cobertura:

```powershell
python -m pytest tests -v --cov=crm_cloud_demo --cov-report=term-missing
python -m ruff check src tests
```

A cobertura informa quais linhas foram exercitadas; ela não substitui a análise de qualidade dos cenários. O GitHub Actions executa os testes e a verificação Ruff a cada push na `main` e em pull requests.

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

### Como aprender com o projeto

A ideia é que você consiga acompanhar o raciocínio, e não apenas copiar comandos. Comece pelo [Guia de Aprendizagem](docs/learning-guide.md), que organiza o estudo em etapas: entender o problema, preparar o ambiente, conhecer a arquitetura, acompanhar a automação e verificar o comportamento da solução.

O guia também indica o que observar no código e quais perguntas você deve conseguir responder ao final de cada etapa.

### Próximas melhorias

A funcionalidade principal, a automação com navegador e os testes unitários, de integração e E2E já estão implementados. As evoluções seguintes não bloqueiam a demonstração acadêmica atual:

- Integrar o módulo de logs ao orquestrador e padronizar os registros de cada etapa.
- Validar o conteúdo do arquivo baixado antes de iniciar o upload.
- Adicionar proteção CSRF e limitação de tentativas de autenticação antes de qualquer exposição pública.
- Adicionar evidências visuais, relatório de execução e instruções de demonstração para a apresentação do TCC.
- Avaliar a execução programada pelo Agendador de Tarefas do Windows.
- Definir uma licença de uso para orientar a reutilização do código por outras pessoas.

### Dois objetivos, a mesma importância

**Portfólio:** este projeto registra minha evolução prática em automação de processos, Python, desenvolvimento web, automação de navegadores, manipulação de dados e Excel e segurança da informação. Demonstra como transformei um problema em uma solução estruturada.

**Aprendizagem e compartilhamento:** quero que alguém com uma necessidade semelhante encontre aqui um ponto de partida útil, entenda por que cada tecnologia foi utilizada e consiga reproduzir ou adaptar a solução. A documentação em português e inglês ajuda a compartilhar esse conhecimento com mais pessoas, sem deixar de valorizar a origem brasileira do projeto.

**Desenvolvido de forma independente no Brasil. Construído para demonstrar meu trabalho e, ao mesmo tempo, ajudar outras pessoas a aprender.**

Documentação: [Arquitetura — PT-BR](docs/architecture.md) · [Architecture — EN](docs/architecture.en.md) · [Segurança — PT-BR](docs/security.md) · [Security — EN](docs/security.en.md)

---

## English

This project has **two equally important goals: to serve as a software development portfolio and as an open learning resource**.

As a portfolio project, it demonstrates how I identified a problem, selected technologies, and built an end-to-end automation solution. As an educational resource, it aims to help people facing a similar challenge understand the workflow, reproduce the solution, and adapt it to their own needs.

The scenario is the automated transfer of reports between two fictional web applications: a CRM and a document library. The solution uses Python and Playwright to control a browser, generate and download an Excel report from the demo CRM, and then upload it to the Cloud Library application.

Both applications are fictional, run locally, and use synthetic data. The goal is not merely to provide finished code, but to share the process, technical decisions, and knowledge that can help others learn from it.

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

A web application built with FastAPI. It provides a Portuguese and English interface, local authentication, fictional business data, date-based deal queries, and Excel report exports in the selected language.

**2. Cloud Library**

An independent web application that simulates a document library. It provides a Portuguese and English interface, its own authentication, accepts `.xlsx` files, validates documents, stores files locally, and records metadata and version history in SQLite.

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
| Frankfurter API | Reference rate for BRL/USD conversion in the English interface |
| SQLite | Metadata and document version-history persistence |
| Jinja2 | HTML templates |
| python-dotenv | Environment-based configuration loading |
| pytest / pytest-cov | Unit, integration, and browser end-to-end tests with coverage reporting |
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
│       ├── currency.py
│       ├── localization.py
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

Install Chromium in the project's browser directory:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
python -m playwright install chromium
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

**Language and currency:** use the `PT-BR / EN` selector on the CRM and Cloud Library login pages and dashboards to switch languages. Each application keeps its own preference during the session. In PT-BR mode, amounts are displayed in BRL. In EN mode, amounts are converted from BRL to USD using the latest reference rate retrieved from the Frankfurter API; the rate date and source are shown in the dashboard and Excel report. Original records remain stored in BRL. The English version needs an internet connection to retrieve the rate; if the API is unavailable, the interface reports the issue instead of showing an invented conversion.

### Tests

`pytest` and `pytest-cov` are development dependencies. The test suite is organized into three levels:

- `tests/unit/`: configuration, localization, currency conversion, Excel generation, storage, logging, and automation helpers.
- `tests/integration/`: authentication, routes, CRM exports, Cloud Library uploads, persistence, and version history.
- `tests/e2e/`: the actual automation robot running with Chromium and Playwright, from CRM login through confirmation that the report was stored in the library.

With the virtual environment activated and Chromium installed, run the full suite and coverage report:

```powershell
python -m pytest tests -v --cov=crm_cloud_demo --cov-report=term-missing
python -m ruff check src tests
```

Coverage shows which lines were exercised; it does not replace reviewing the quality of test scenarios. GitHub Actions runs the test suite and Ruff checks on every push to `main` and on pull requests.

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

### Learning path

The goal is to help you understand the reasoning behind the implementation, not just copy commands. Start with the [Learning Guide](docs/learning-guide.en.md), which organizes the journey into stages: understand the problem, prepare the environment, explore the architecture, follow the automation, and verify the solution's behavior.

The guide also points to the code areas to inspect and the questions you should be able to answer at the end of each stage.

### Next improvements

The core functionality, browser automation, and unit, integration, and end-to-end tests are implemented. The following improvements do not block the current academic demonstration:

- Integrate the logging module with the orchestrator and standardize workflow-stage records.
- Validate the downloaded file contents before starting the upload.
- Add CSRF protection and authentication-attempt rate limiting before any public exposure.
- Add visual evidence, an execution report, and demonstration instructions for the TCC presentation.
- Evaluate scheduled execution through Windows Task Scheduler.
- Choose a software license to clarify how others may reuse the code.

### Two equally important goals

**Portfolio:** this project documents my hands-on development in process automation, Python, web development, browser automation, data and Excel manipulation, and information security. It shows how I turned a problem into a structured solution.

**Learning and knowledge sharing:** I want people with a similar need to find a useful starting point here, understand why each technology was chosen, and learn how to reproduce or adapt the solution. Documentation in Portuguese and English helps share this knowledge with a wider audience while keeping the project's Brazilian roots visible.

**Independently developed in Brazil. Built to demonstrate my work and, at the same time, help others learn.**

Documentation: [Architecture — EN](docs/architecture.en.md) · [Arquitetura — PT-BR](docs/architecture.md) · [Security — EN](docs/security.en.md) · [Segurança — PT-BR](docs/security.md)
