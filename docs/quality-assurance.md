# Garantia de Qualidade e Estratégia de Testes

**English:** [Read the English version](quality-assurance.en.md).

## 1. Objetivo

Este documento descreve como o projeto automacao-crm-excel-cloud verifica o comportamento das aplicações, do armazenamento e do robô de automação.

A estratégia combina testes unitários, testes de integração HTTP e um teste de ponta a ponta com Chromium real. O objetivo é verificar comportamentos observáveis e caminhos de falha relevantes, não apenas executar linhas de código.

## 2. Níveis de teste

### 2.1 Testes unitários — tests/unit/

Verificam componentes isolados, incluindo:

- Validação e carregamento das configurações.
- Seleção de idioma, traduções e validação de caminhos de retorno.
- Conversão BRL/USD, arredondamento, cache e tratamento de respostas inválidas da fonte cambial.
- Geração dos relatórios Excel em português e inglês.
- Sanitização de nomes, validação de arquivos XLSX, persistência, hashes, versões e rollback do armazenamento.
- Configuração de logs e tratamento dos recursos do navegador.
- Funções de login, download, upload e orquestração do robô.

### 2.2 Testes de integração — tests/integration/

Utilizam o TestClient do FastAPI para enviar requisições HTTP reais às aplicações locais de demonstração.

Os cenários cobrem:

- Login válido e inválido, logout e proteção de rotas.
- Preferências de idioma independentes.
- Painel do CRM em BRL e USD, incluindo indisponibilidade da cotação.
- Exportação de relatórios Excel nos dois idiomas.
- Validação de datas e respostas de erro.
- Upload de arquivos válidos, arquivos com extensão inválida e planilhas corrompidas.
- Persistência de arquivos, hash SHA-256 e histórico de versões no SQLite.

### 2.3 Teste de ponta a ponta — tests/e2e/

O teste E2E inicia os dois servidores FastAPI em portas locais disponíveis e utiliza Chromium real controlado por Playwright.

O robô executa a sequência completa:

1. Acessa e autentica no CRM.
2. Solicita a exportação do relatório.
3. Baixa a planilha Excel.
4. Acessa e autentica na Cloud Library.
5. Envia o arquivo pela interface web.
6. Verifica a confirmação, o arquivo armazenado, o hash SHA-256 e a versão registrada no SQLite.
7. Verifica o arquivo de log e confirma que as senhas demonstrativas não foram registradas.

Esse teste utiliza aplicações fictícias, credenciais de teste e armazenamento temporário. Não acessa sistemas corporativos.

## 3. Integração contínua

O workflow .github/workflows/ci.yml executa automaticamente em pushes para main e em pull requests.

A pipeline:

1. Prepara Python 3.14.
2. Instala o projeto e as dependências de desenvolvimento.
3. Instala Chromium pelo Playwright.
4. Executa testes unitários, de integração e E2E.
5. Gera o relatório de cobertura do pacote crm_cloud_demo.
6. Exige pelo menos 100% de cobertura de linhas nesse pacote.
7. Executa o Ruff para verificar a qualidade e a organização estática do código.

Execuções antigas da mesma branch podem ser canceladas para priorizar a validação do commit mais recente.

## 4. Como reproduzir os testes localmente

No PowerShell, com o ambiente virtual ativado:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
python -m playwright install chromium

python -m pytest tests -v --cov=crm_cloud_demo --cov-report=term-missing --cov-fail-under=100
python -m ruff check src tests
```

O teste E2E necessita que o Chromium esteja instalado no diretório configurado por PLAYWRIGHT_BROWSERS_PATH.

## 5. Como interpretar a cobertura

A cobertura de 100% refere-se às instruções executáveis do pacote Python crm_cloud_demo consideradas pelo Coverage.py durante a suíte.

Ela não significa que:

- Todo comportamento possível foi testado.
- Todos os caminhos de combinação ou condições foram formalmente verificados.
- As dependências de terceiros ou os templates HTML possuem 100% de cobertura.
- A aplicação recebeu auditoria de segurança ou teste de invasão.
- O projeto está pronto para operar sistemas empresariais reais.

A cobertura é uma evidência útil, mas deve ser analisada junto com os cenários, as verificações E2E, as limitações conhecidas e a revisão do código.

## 6. Limitações e escopo

- Os testes cambiais usam respostas controladas para garantir resultados determinísticos; a disponibilidade da API externa depende de conexão e do provedor.
- O E2E comprova o fluxo nas aplicações fictícias locais, não em CRMs, bibliotecas ou sistemas corporativos reais.
- A proteção CSRF e a limitação de tentativas de login permanecem pendentes antes de qualquer exposição pública.
- A suíte não constitui uma certificação de segurança nem substitui revisão independente.

O resultado deve ser apresentado como validação automatizada de uma demonstração independente e educacional.
