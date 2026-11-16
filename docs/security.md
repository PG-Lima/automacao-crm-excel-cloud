# Política de Segurança do Projeto

## 1. Objetivo

Este documento descreve as medidas de segurança implementadas e as melhorias planejadas no projeto `automacao-crm-excel-cloud`.

O projeto é uma demonstração independente de automação web, desenvolvida com Python, Playwright e FastAPI.

Todas as aplicações utilizam dados sintéticos e são executadas localmente.

Este documento diferencia controles implementados de medidas que ainda precisam ser desenvolvidas.

## 2. Isolamento do projeto

**Status: Implementado**

O projeto utiliza aplicações fictícias e independentes.

Medidas adotadas:

- CRM demonstrativo desenvolvido exclusivamente para o projeto.
- Biblioteca de documentos desenvolvida exclusivamente para o projeto.
- Utilização de dados comerciais sintéticos.
- Ausência de integração com sistemas corporativos reais.
- Ausência de reutilização de credenciais, cookies ou sessões externas.
- Execução local das aplicações.
- Utilização de `127.0.0.1` nos comandos de inicialização documentados.

O projeto não utiliza infraestrutura ou informações de empresas reais.

## 3. Gerenciamento de credenciais e segredos

**Status: Parcialmente implementado**

As credenciais são carregadas por meio de variáveis de ambiente, utilizando `python-dotenv`.

Medidas implementadas:

- Separação entre configurações e código-fonte.
- Arquivo `.env` protegido pelo `.gitignore`.
- Arquivo `.env.example` com valores fictícios.
- Credenciais independentes para CRM e Cloud Library.
- Segredos de sessão independentes para as duas aplicações.
- Comparação das credenciais utilizando `secrets.compare_digest`.

Observações:

- As credenciais padrão são previsíveis e servem exclusivamente para a demonstração local.
- Os segredos de sessão podem ser gerados aleatoriamente quando não são definidos no ambiente.
- A troca desses segredos invalida as sessões existentes.

Melhorias planejadas:

- Implementar política de alteração das credenciais demonstrativas.
- Adicionar controle de tentativas de autenticação.
- Avaliar o gerenciamento seguro de segredos em ambientes diferentes do ambiente local.

## 4. Proteção do repositório Git

**Status: Implementado e verificado parcialmente**

O `.gitignore` contém regras para impedir a inclusão de arquivos locais e sensíveis.

Arquivos protegidos:

- `.env` e arquivos de configuração privados.
- `.venv/` e outros ambientes virtuais.
- `logs/` e arquivos de registro.
- `storage/` e bancos de dados locais.
- Relatórios e planilhas gerados.
- Diretórios de downloads.
- Perfis e sessões de navegador.
- Chaves privadas e certificados sensíveis.
- Arquivos temporários.

As regras foram verificadas utilizando `git check-ignore`.

Antes da publicação, será realizada uma revisão dos arquivos efetivamente preparados para o commit.

## 5. Segurança dos logs

**Status: Parcialmente implementado**

O projeto possui um módulo de configuração de logs em `logging_config.py`.

Entretanto, a integração desse módulo ao fluxo principal de automação ainda está pendente.

Diretrizes para os registros:

- Não armazenar senhas.
- Não armazenar tokens de autenticação.
- Não armazenar cookies ou identificadores de sessão.
- Não registrar chaves privadas.
- Não registrar dados pessoais ou informações confidenciais.
- Não registrar o conteúdo integral dos relatórios.

Melhorias planejadas:

- Integrar o módulo de logs ao orquestrador.
- Padronizar os registros das etapas.
- Registrar erros sem expor informações sensíveis.
- Implementar rotação e limite de armazenamento dos arquivos de log.

## 6. Segurança da automação do navegador

**Status: Implementado**

O Playwright utiliza um contexto de navegador independente durante a execução.

Medidas implementadas:

- Inicialização do Chromium pelo Playwright.
- Criação de um contexto isolado.
- Suporte a downloads.
- Configuração de tempo limite para operações.
- Encerramento do contexto e do navegador ao final da execução.
- Ausência de reutilização de perfis pessoais ou corporativos.
- Utilização de credenciais carregadas das configurações locais.

O projeto não importa cookies ou sessões de navegadores externos.

## 7. Segurança no recebimento de arquivos

**Status: Implementado**

A biblioteca de documentos realiza validações antes de armazenar os arquivos.

Controles implementados:

- Aceitação exclusiva de arquivos `.xlsx`.
- Verificação da extensão e assinatura do arquivo.
- Verificação da estrutura ZIP interna.
- Verificação da presença de componentes esperados de um arquivo Excel.
- Verificação de integridade e possibilidade de leitura da planilha.
- Limite máximo de upload de 10 MB.
- Limite de conteúdo descompactado de 50 MB.
- Limite de 250 entradas no arquivo ZIP.
- Sanitização do nome original.
- Utilização de identificadores únicos para os arquivos armazenados.

A validação não considera a extensão `.xlsx` suficiente para determinar a validade do documento.

Essas verificações são voltadas à demonstração e não representam uma garantia contra todas as formas de arquivos maliciosos.

## 8. Banco de dados e armazenamento

**Status: Implementado**

O projeto utiliza SQLite e armazenamento local.

Medidas implementadas:

- Armazenamento separado do código-fonte.
- Geração de nomes internos únicos.
- Registro de metadados dos documentos.
- Cálculo de hash SHA-256.
- Controle de versões.
- Registro do tamanho e horário do envio.
- Utilização de transação para registrar os metadados.
- Limpeza do arquivo criado quando ocorre falha durante a operação de armazenamento.

O banco de dados e os arquivos enviados permanecem fora do controle de versão por meio do `.gitignore`.

O armazenamento não foi projetado para uso compartilhado em ambientes de produção.

## 9. Autenticação e sessões

**Status: Parcialmente implementado**

As duas aplicações utilizam autenticação independente.

Medidas implementadas:

- Credenciais fictícias.
- Comparação segura das credenciais.
- Sessões independentes.
- Segredos de sessão diferentes.
- Nomes de cookies diferentes.
- Encerramento de sessão por meio de logout.

Limitações atuais:

- Não existe proteção CSRF implementada nos formulários.
- Não existe limitação de tentativas de login.
- Os cookies utilizam configurações apropriadas ao ambiente HTTP local, não a uma implantação pública.

Esses pontos deverão ser tratados antes de qualquer adaptação para uso real.

## 10. Tratamento de erros

**Status: Parcialmente implementado**

A implementação atual contempla verificações para:

- Credenciais inválidas.
- Arquivos inexistentes.
- Extensões não permitidas.
- Arquivos vazios.
- Arquivos acima dos limites estabelecidos.
- Estruturas Excel inválidas.
- Falhas de navegação e download.
- Ausência de confirmação do upload.

Melhorias planejadas:

- Padronizar exceções da automação.
- Melhorar o tratamento de indisponibilidade das aplicações.
- Integrar o registro de falhas ao sistema de logs.
- Adicionar testes para cenários de falha.

## 11. Dependências e manutenção

**Status: Parcialmente implementado**

As dependências estão centralizadas no `pyproject.toml`.

O projeto utiliza um ambiente virtual próprio.

Diretrizes:

- Instalar dependências no ambiente virtual do projeto.
- Evitar bibliotecas desnecessárias.
- Manter as dependências documentadas.
- Analisar atualizações relevantes.
- Verificar vulnerabilidades antes de versões importantes.

A auditoria automatizada de vulnerabilidades das dependências ainda está pendente.

## 12. Limites de utilização

Este projeto possui finalidade exclusivamente educacional e demonstrativa.

Não foi desenvolvido para:

- Processar informações reais de empresas.
- Operar sistemas corporativos.
- Armazenar documentos confidenciais.
- Receber arquivos de usuários desconhecidos pela internet.
- Oferecer autenticação ou armazenamento de nível empresarial.

As medidas implementadas não representam certificação de segurança nem garantem adequação para produção.

## 13. Checklist de segurança

### Controles implementados

- [x] Utilização de dados sintéticos.
- [x] Credenciais fictícias.
- [x] Separação entre configurações e código.
- [x] Proteção do `.env` pelo `.gitignore`.
- [x] Proteção dos bancos de dados e relatórios locais.
- [x] Sessões independentes.
- [x] Contexto isolado do Playwright.
- [x] Validação de arquivos Excel.
- [x] Limitação de tamanho e estrutura dos arquivos.
- [x] Armazenamento com identificadores únicos.
- [x] Registro de versões e hashes.

### Melhorias pendentes

- [ ] Proteção CSRF nos formulários.
- [ ] Limitação de tentativas de autenticação.
- [ ] Integração completa dos logs.
- [ ] Rotação de logs.
- [ ] Testes unitários e de integração.
- [ ] Auditoria automatizada de dependências.
- [ ] Revisão final dos arquivos preparados para publicação.

## 14. Compromisso de segurança

A segurança faz parte do desenvolvimento contínuo do projeto.

Novas funcionalidades deverão respeitar os princípios de isolamento, proteção de dados, validação de entradas e controle de acesso.

O escopo permanecerá independente de sistemas corporativos e utilizará exclusivamente ambientes e dados fictícios.