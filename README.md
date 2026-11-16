# Automação CRM → Excel → Cloud

Projeto independente de portfólio que demonstra a automação de processos web utilizando Python, Playwright e Excel.

O sistema simula um fluxo de trabalho entre duas aplicações web fictícias: um CRM e uma biblioteca de documentos.

## Demonstração

A automação executa o seguinte processo:

1. Acessa o CRM demonstrativo utilizando Chromium.
2. Realiza autenticação.
3. Exporta um relatório de negociações em Excel.
4. Baixa o arquivo automaticamente.
5. Acessa a biblioteca de documentos.
6. Realiza uma segunda autenticação.
7. Envia o relatório para armazenamento.
8. Confirma o resultado e a versão do documento.

**Status:** fluxo principal executado com sucesso em ambiente local.

## Arquitetura

O projeto possui três componentes independentes:

### 1. CRM demonstrativo

Aplicação web desenvolvida com FastAPI que oferece:
- Autenticação local.
- Dados comerciais fictícios.
- Consulta de negociações por período.
- Exportação de relatórios Excel.

### 2. Cloud Library

Biblioteca de documentos fictícia que oferece:
- Autenticação independente.
- Recebimento de arquivos `.xlsx`.
- Validação dos arquivos enviados.
- Armazenamento local.
- Registro de metadados em SQLite.
- Histórico de versões.

### 3. Automação

Implementada com Python e Playwright:
- Controle do navegador Chromium.
- Login nas duas aplicações.
- Download automático de relatórios.
- Upload por meio da interface web.
- Confirmação do resultado da operação.

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.14 | Linguagem principal |
| Playwright | Automação de navegador |
| FastAPI | Aplicações web |
| Uvicorn | Servidor ASGI |
| openpyxl | Geração e manipulação de Excel |
| SQLite | Metadados e histórico |
| Jinja2 | Templates HTML |
| python-dotenv | Gerenciamento de configurações |
| pytest | Infraestrutura planejada para testes |
| Ruff | Análise e padronização de código |
| Git | Controle de versão |

## Estrutura do projeto

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
│   └── security.md
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Requisitos

- Windows 11 ou sistema compatível com Python.
- Python 3.14 ou superior.
- Git.
- Chromium instalado pelo Playwright.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/automacao-crm-excel-cloud.git
cd automacao-crm-excel-cloud
```

Crie o ambiente virtual:

```powershell
py -3.14 -m venv .venv
```

Ative o ambiente:

```powershell
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

## Configuração

Crie o arquivo `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
```

As configurações incluem:

- Endereços locais das aplicações.
- Credenciais fictícias.
- Diretórios de armazenamento.
- Configurações do navegador.
- Tempo limite das operações.
- Configurações de logs.

As credenciais padrão são exclusivas para demonstração local. Não utilize senhas reais.

## Executando o projeto

São necessários três terminais.

**Terminal 1 — CRM**

```powershell
python -m uvicorn crm_cloud_demo.apps.crm.app:app --host 127.0.0.1 --port 8000 --reload
```

Acesso: http://127.0.0.1:8000/login

**Terminal 2 — Cloud Library**

```powershell
python -m uvicorn crm_cloud_demo.apps.cloud.app:app --host 127.0.0.1 --port 8001 --reload
```

Acesso: http://127.0.0.1:8001/login

**Terminal 3 — Automação**

```powershell
python -m crm_cloud_demo.automation.run
```

A automação utilizará as configurações definidas no `.env` para acessar as aplicações.

## Segurança

O projeto foi desenvolvido como uma simulação local e independente.

Algumas medidas implementadas:

- Dados comerciais sintéticos.
- Credenciais fictícias.
- Sessões independentes entre aplicações.
- Proteção de arquivos locais pelo `.gitignore`.
- Validação de arquivos Excel recebidos.
- Limitação de tamanho e conteúdo dos arquivos.
- Armazenamento versionado.
- Registro de metadados e hashes SHA-256.
- Ausência de integração com serviços corporativos reais.

Consulte [`docs/security.md`](docs/security.md) para mais informações.

**Importante:** o projeto é educacional e não deve ser considerado uma aplicação pronta para produção.

## Próximas melhorias

- Implementação de testes unitários e de integração.
- Melhorias no tratamento de exceções.
- Evidências visuais da automação.
- Relatórios estruturados de execução.
- Integração com o Agendador de Tarefas do Windows.
- Melhorias de segurança e documentação.

## Objetivo profissional

Este projeto faz parte do meu desenvolvimento prático em:

- Automação de processos.
- Python e desenvolvimento de software.
- Automação de navegadores.
- Manipulação de dados e Excel.
- Desenvolvimento de aplicações web.
- Segurança da informação.

Desenvolvido de forma independente para fins educacionais e construção de portfólio profissional.
