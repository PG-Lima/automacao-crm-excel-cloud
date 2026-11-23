# Arquitetura do Projeto

**English:** [Read the English version](architecture.en.md).

**Guia de aprendizagem:** [consulte o roteiro de estudo](learning-guide.md).

**Garantia de qualidade:** [consulte a estratégia e a execução dos testes](quality-assurance.md).

## 1. Visão geral

O projeto `automacao-crm-excel-cloud` demonstra um processo de automação web desenvolvido em Python, utilizando Playwright para controlar um navegador e interagir com duas aplicações web independentes.

Esta documentação atende a dois propósitos: registrar a arquitetura do projeto como parte de um portfólio de desenvolvimento e servir como material de aprendizagem para quem deseja compreender, reproduzir ou adaptar uma automação semelhante.

A solução contém três componentes principais:

- **CRM demonstrativo:** gera relatórios comerciais fictícios em Excel.
- **Cloud Library:** recebe, valida e armazena os documentos enviados.
- **Automação Python:** controla o navegador e executa o processo de transferência entre as aplicações.

Todos os componentes são executados localmente e utilizam dados sintéticos.

## 2. Componentes da arquitetura

### 2.1 CRM demonstrativo

Aplicação web desenvolvida com FastAPI.

Responsabilidades:

- Apresentar uma tela de autenticação.
- Autenticar usuários com credenciais fictícias.
- Disponibilizar dados comerciais sintéticos.
- Apresentar negociações em um painel.
- Permitir a consulta por período.
- Gerar relatórios em Excel utilizando openpyxl.
- Disponibilizar o download dos relatórios.
- Exibir a interface em português (PT-BR) e inglês.
- Gerar o relatório Excel com cabeçalhos, status e resumo no idioma selecionado.

Endereço local:

`http://127.0.0.1:8000`

### 2.2 Automação Python

Componente responsável por executar o fluxo entre as aplicações.

Responsabilidades:

- Inicializar o navegador Chromium utilizando Playwright.
- Configurar um contexto com suporte a downloads.
- Acessar o CRM demonstrativo.
- Realizar autenticação.
- Acionar a exportação do relatório.
- Baixar o arquivo Excel.
- Acessar a biblioteca de documentos.
- Realizar autenticação independente.
- Enviar o arquivo por meio da interface web.
- Aguardar e verificar a confirmação do upload.

O fluxo principal utiliza a interface do navegador para realizar as operações, sem depender de chamadas diretas às APIs internas das aplicações.

O período do relatório utiliza os valores padrão apresentados pelo CRM na implementação atual.

### 2.3 Biblioteca de documentos

Aplicação web independente, também desenvolvida com FastAPI.

Responsabilidades:

- Apresentar uma tela de autenticação em português e inglês.
- Permitir a alternância de idioma na tela de login e no painel.
- Receber arquivos no formato `.xlsx`.
- Validar os arquivos recebidos.
- Aplicar limites de tamanho e estrutura.
- Armazenar os documentos no sistema de arquivos local.
- Gerar identificadores únicos para os arquivos armazenados.
- Calcular hashes SHA-256.
- Registrar metadados no SQLite.
- Controlar versões dos documentos.
- Apresentar o histórico de arquivos enviados.

Endereço local:

`http://127.0.0.1:8001`

### 2.4 Idiomas e localização

O CRM e a Cloud Library oferecem interface em português (PT-BR) e inglês.

A preferência é armazenada na sessão de cada aplicação e pode ser alterada pelo seletor `PT-BR / EN`. Como as aplicações possuem sessões independentes, o idioma pode ser escolhido separadamente em cada sistema.

A localização altera os textos exibidos, mensagens de validação, formatação de datas e moedas e conteúdo do relatório Excel. Em PT-BR, os valores permanecem em reais (BRL). Em inglês, o CRM converte os valores de BRL para USD usando a taxa de referência mais recente obtida pela API Frankfurter. A data da taxa e sua origem são exibidas no painel e registradas no resumo do Excel. Os registros originais continuam em BRL; a conversão ocorre na camada de apresentação e exportação.

O módulo `src/crm_cloud_demo/currency.py` consulta o par BRL/USD, valida a resposta, mantém a taxa em cache por seis horas e realiza os cálculos com `Decimal`. A Frankfurter oferece taxas de referência, não cotações de negociação em tempo real. Se a consulta falhar e não houver uma taxa em cache válida, a interface inglesa informa a indisponibilidade e o relatório em USD não é gerado. Os nomes técnicos dos campos, rotas, formulários e seletores usados pelo Playwright permanecem estáveis para não quebrar a automação.

## 3. Fluxo de execução

O processo de automação segue esta sequência:

1. A automação inicializa o Chromium.
2. O Playwright acessa o CRM demonstrativo.
3. A automação realiza o login.
4. O Playwright localiza e aciona o formulário de exportação.
5. O CRM gera o relatório Excel.
6. O Playwright realiza o download do arquivo.
7. O arquivo é armazenado no diretório local de downloads.
8. O navegador acessa a biblioteca de documentos.
9. A automação realiza o segundo login.
10. O arquivo é selecionado no formulário de upload.
11. A biblioteca recebe e valida o documento.
12. O arquivo é armazenado no sistema de arquivos local.
13. O SQLite registra os metadados e a versão.
14. A automação aguarda a mensagem de confirmação.
15. O processo é finalizado.

## 4. Diagrama da arquitetura

```mermaid
flowchart TD
    A[Orquestrador Python] --> B[Playwright]
    B --> C[CRM demonstrativo]
    C --> D[Geracao do Excel]
    D --> E[Download local]
    E --> F[Biblioteca de documentos]
    F --> G[Validacao XLSX]
    G --> H[Armazenamento local]
    G --> I[Banco SQLite]
    H --> I
    F --> J[Confirmacao do upload]
    J --> A
```

## 5. Comunicação entre componentes

A comunicação do fluxo principal ocorre por meio das interfaces web locais.

| Origem | Destino | Finalidade |
|---|---|---|
| Playwright | CRM | Autenticação e exportação |
| CRM | Navegador | Disponibilização do Excel |
| Playwright | Biblioteca | Autenticação e upload |
| Biblioteca | Validação | Verificação do arquivo recebido |
| Biblioteca | Sistema de arquivos | Armazenamento dos documentos |
| Biblioteca | SQLite | Registro dos metadados e versões |

A automação utiliza interações reais de navegador para executar login, exportação e upload.

## 6. Armazenamento e versionamento

O armazenamento utiliza o sistema de arquivos local e um banco de dados SQLite.

Os documentos enviados:

- São armazenados com identificadores únicos.
- Mantêm o nome original registrado nos metadados.
- Recebem um hash SHA-256.
- Possuem registro de tamanho e data de envio.
- Recebem numeração de versão.
- Não substituem destrutivamente os arquivos de versões anteriores.

O banco SQLite mantém informações como:

- Identificador do documento.
- Nome original do arquivo.
- Nome utilizado no armazenamento.
- Hash SHA-256.
- Tamanho em bytes.
- Número da versão.
- Data e horário do envio.

## 7. Tratamento de erros

A implementação atual possui verificações para situações como:

- Credenciais inválidas.
- Arquivo inexistente para upload.
- Extensão diferente de `.xlsx`.
- Arquivo vazio ou acima do limite permitido.
- Estrutura inválida de arquivo Excel.
- Falhas durante a navegação ou download.
- Ausência de confirmação do upload.

O fluxo utiliza exceções do Python e verificações do Playwright para identificar falhas durante a execução.

A integração completa do sistema de logs e a ampliação do tratamento de falhas fazem parte das próximas melhorias.

## 8. Segurança e isolamento

O projeto segue princípios de isolamento e segurança:

- Aplicações fictícias e independentes.
- Utilização exclusiva de dados sintéticos.
- Servidores vinculados ao endereço local `127.0.0.1`.
- Credenciais exclusivas para demonstração.
- Segredos de sessão independentes.
- Separação entre código e configurações.
- Proteção de arquivos locais pelo `.gitignore`.
- Validação dos arquivos recebidos.
- Limitação de tamanho e conteúdo dos uploads.
- Armazenamento com identificadores únicos.
- Ausência de integração com sistemas corporativos reais.

O projeto é educacional e não deve ser considerado uma solução pronta para produção.

## 9. Estado atual e evolução

O fluxo principal já foi implementado e executado com sucesso em ambiente local.

As etapas concluídas incluem:

1. Configuração do ambiente Python.
2. Implementação do CRM demonstrativo.
3. Implementação da biblioteca de documentos.
4. Configuração do Chromium e Playwright.
5. Automação do login nas duas aplicações.
6. Download automático do relatório Excel.
7. Upload automatizado para a biblioteca.
8. Registro e confirmação do versionamento.

Próximas melhorias:

- Integrar o módulo de logging ao orquestrador para registrar as etapas da execução.
- Validar independentemente o conteúdo do relatório baixado antes do upload.
- Ampliar a observabilidade e padronizar o tratamento de falhas.
- Avaliar a execução programada pelo Agendador de Tarefas do Windows.
- Avaliar uma implantação demonstrativa pública com controles adicionais, sem utilizar dados reais.
- Ampliação da documentação e auditoria de segurança.

## 10. Considerações finais

A arquitetura foi organizada para resolver um cenário prático de transferência de relatórios e, ao mesmo tempo, tornar visíveis as decisões técnicas envolvidas. Ela documenta como as aplicações, o robô, o navegador, o armazenamento e o banco de dados trabalham em conjunto.

O projeto cumpre dois objetivos de igual importância: demonstrar competências práticas em um portfólio de desenvolvimento e compartilhar conhecimento para que outras pessoas possam estudar a arquitetura, reproduzir o fluxo e adaptar a solução a problemas semelhantes.

A implementação é independente, utiliza aplicações fictícias e infraestrutura local e foi desenvolvida no Brasil.