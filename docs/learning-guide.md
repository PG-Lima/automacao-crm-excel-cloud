# Guia de Aprendizagem

**English:** [Read the English version](learning-guide.en.md).

## 1. Por que este guia existe?

Este projeto tem dois objetivos de igual importância:

1. **Portfólio de desenvolvimento:** apresentar uma solução construída a partir de um problema prático e registrar decisões técnicas, implementação e evolução.
2. **Aprendizagem e compartilhamento:** ajudar outras pessoas a compreender o problema, acompanhar a construção da solução, reproduzi-la localmente e adaptá-la a necessidades semelhantes.

Este guia transforma o repositório em um caminho de estudo, não apenas em um conjunto de arquivos para copiar.

## 2. O problema que estamos simulando

Imagine um processo que uma pessoa faria manualmente:

1. Acessar um CRM e entrar com suas credenciais.
2. Gerar um relatório de negociações.
3. Baixar esse relatório em Excel.
4. Acessar outro sistema, destinado a armazenar documentos.
5. Entrar nesse segundo sistema.
6. Enviar o arquivo baixado.

O projeto demonstra como automatizar esse fluxo com um robô que controla um navegador.

**Importante:** o CRM e a Cloud Library deste repositório são aplicações fictícias, criadas para a demonstração. O projeto não se conecta a CRMs, nuvens ou sistemas corporativos reais.

## 3. O que você vai aprender

Ao estudar o projeto, você poderá compreender:

- Como dividir um problema em etapas automatizáveis.
- Como Python organiza a lógica de uma aplicação.
- Como FastAPI e Uvicorn disponibilizam aplicações web localmente.
- Como Playwright controla um navegador pela interface.
- Como um relatório Excel pode ser gerado com openpyxl.
- Como arquivos podem ser recebidos, validados e armazenados.
- Como SQLite registra metadados e histórico de versões.
- Como configurações e credenciais demonstrativas são separadas do código.
- Como documentar, executar e verificar uma solução.

## 4. Caminho de estudo recomendado

### Etapa 1 — Entenda o cenário antes do código

Leia as seções iniciais do [README](../README.md) e a [Arquitetura do Projeto](architecture.md).

Antes de abrir os arquivos Python, tente responder:

- Qual trabalho manual estamos automatizando?
- Quais são os dois sistemas envolvidos?
- Qual é a função do robô?
- Por que os sistemas foram simulados localmente?

**Objetivo:** compreender o problema e os componentes sem se perder nos detalhes da implementação.

### Etapa 2 — Prepare e execute o ambiente

Siga os requisitos, a instalação, a configuração e a execução descritos no [README](../README.md).

O projeto utiliza três processos locais:

| Componente | Endereço ou comando | Função |
|---|---|---|
| CRM demonstrativo | http://127.0.0.1:8000 | Gera o relatório |
| Cloud Library | http://127.0.0.1:8001 | Recebe e armazena o relatório |
| Robô | python -m crm_cloud_demo.automation.run | Controla o navegador e transfere o arquivo |

Execute primeiro os dois sistemas e abra suas páginas no navegador. Depois execute o robô e observe o fluxo.

**Objetivo:** perceber que o CRM, a Cloud Library e a automação são componentes distintos.

### Etapa 3 — Siga o caminho do robô

Leia os arquivos nesta ordem:

1. **src/crm_cloud_demo/automation/run.py** — ponto de entrada e sequência principal. A função run_automation coordena as etapas.
2. **src/crm_cloud_demo/automation/browser.py** — cria a sessão do navegador, habilita downloads e fecha os recursos ao final.
3. **src/crm_cloud_demo/automation/crm.py** — contém o login no CRM e o download do relatório.
4. **src/crm_cloud_demo/automation/cloud.py** — contém o login na Cloud Library e o envio do arquivo.
5. **src/crm_cloud_demo/config.py** — reúne as configurações usadas pelas aplicações e pela automação.

Enquanto lê, acompanhe esta sequência:

**run_automation → browser_session → login no CRM → download do Excel → login na Cloud Library → upload → confirmação.**

Observe especialmente estas operações do Playwright:

- **page.goto()**: navega para uma página.
- **page.locator()**: localiza elementos da interface.
- **fill()**: preenche um campo.
- **click()**: aciona um elemento.
- **page.expect_download()**: aguarda um download.
- **set_input_files()**: seleciona um arquivo para envio.

Essas operações são chamadas do Playwright a partir do Python. No fluxo principal, o robô interage com as interfaces web, em vez de chamar diretamente as APIs internas dessas duas aplicações.

### Etapa 4 — Entenda como o CRM cria o Excel

Leia:

- **src/crm_cloud_demo/apps/crm/routes.py** — rotas que recebem as solicitações do navegador.
- **src/crm_cloud_demo/apps/crm/services.py** — dados fictícios, filtros e criação da planilha.

Procure pelas funções **get_deals** e **create_excel_report**.

Perguntas para orientar a leitura:

- De onde vêm os registros de negociação?
- Como o período é aplicado?
- Quais abas são criadas na planilha?
- Como os valores e as datas são formatados?
- Por que a função devolve um arquivo em memória antes de a aplicação disponibilizar o download?

### Etapa 5 — Entenda como a Cloud Library recebe e armazena o arquivo

Leia:

- **src/crm_cloud_demo/apps/cloud/routes.py** — rotas de login, painel e upload.
- **src/crm_cloud_demo/apps/cloud/storage.py** — validação, armazenamento e registro no banco de dados.

Observe estas funções e conceitos:

- **_safe_filename**: trata o nome do arquivo recebido.
- **_validate_xlsx**: verifica se o conteúdo tem características esperadas de uma planilha XLSX.
- **save_document**: grava o arquivo e registra seus metadados.
- **list_documents**: consulta os documentos registrados.
- **SQLite:** armazena informações sobre o documento, como nome, tamanho, hash, versão e data de envio.

Uma distinção importante: o arquivo Excel é armazenado no sistema de arquivos local; o SQLite guarda os metadados e o histórico. O banco de dados não é, por si só, o arquivo Excel.

### Etapa 6 — Entenda como verificar o funcionamento

Não basta observar uma mensagem de sucesso. Pense em evidências para cada etapa:

- O login levou à página esperada?
- O relatório foi baixado?
- O arquivo existe e não está vazio?
- O upload foi aceito?
- A Cloud Library apresentou a confirmação?
- O documento aparece no histórico, com a versão e os metadados esperados?

**Estado dos testes no repositório:** a versão atualmente publicada declara pytest como dependência de desenvolvimento, mas ainda não contém a pasta de testes automatizados. Portanto, não confunda a dependência instalada com uma suíte de testes publicada. Acompanhe futuras atualizações para obter os testes junto com o código correspondente.

### Etapa 7 — Pense em como adaptar a solução

Depois de entender a simulação, pense em como ela mudaria em outro contexto:

- O sistema de origem poderia ter outros campos ou filtros?
- O relatório poderia conter outras colunas?
- O sistema de destino poderia exigir outra validação?
- Como seriam tratadas falhas de login, download ou upload?
- Quais controles adicionais seriam necessários antes de qualquer uso com sistemas reais?

Nunca use credenciais, dados ou sistemas de terceiros sem autorização. A implementação atual é uma demonstração local e não deve ser colocada diretamente em produção.

## 5. Glossário rápido

| Termo | Significado neste projeto |
|---|---|
| Automação | Execução de tarefas por instruções programadas |
| CRM | Sistema demonstrativo que fornece os dados e o relatório |
| Cloud Library | Sistema demonstrativo que recebe e armazena o arquivo |
| Navegador | Aplicação que abre e apresenta as páginas web |
| Playwright | Ferramenta que permite controlar o navegador por código |
| FastAPI | Framework Python usado para construir as aplicações web |
| Uvicorn | Servidor que executa as aplicações ASGI |
| Excel / XLSX | Formato do relatório transferido |
| SQLite | Banco de dados local usado para metadados e versões |
| Rota | Endereço e operação que uma aplicação web disponibiliza |
| Upload | Envio de um arquivo para outra aplicação |
| Download | Transferência de um arquivo para o computador |

## 6. Como usar este material

Você não precisa entender tudo de uma vez. Estude uma etapa por vez, execute o exemplo, abra o arquivo indicado e tente explicar o que ele faz com suas próprias palavras.

Ao final, o objetivo é que você consiga:

- Descrever o problema que a automação resolve.
- Explicar a responsabilidade de cada componente.
- Justificar por que as tecnologias foram escolhidas.
- Acompanhar o fluxo no código.
- Identificar o que já está implementado e o que ainda precisa evoluir.
- Adaptar a ideia com segurança a um cenário semelhante.

Este projeto foi desenvolvido de forma independente no Brasil e documentado em português e inglês para compartilhar conhecimento com uma comunidade mais ampla.
