# Estado dos notebooks e reprodutibilidade

## Objetivo

Os notebooks documentam o raciocínio técnico das quatro etapas do case:

- EDA;
- regras;
- machine learning;
- arquitetura multiagente.

Eles devem ser apresentados atualmente como cadernos técnicos de demonstração, não como prova de reprodução integral do repositório.

## Estado atual

Os quatro notebooks possuem células de código, mas estão versionados:

- sem contadores de execução;
- sem outputs;
- sem evidência de execução ponta a ponta.

Os notebooks 01, 02 e 03 ainda apontam para o nome antigo da planilha.

## Notebook 01 - EDA

Demonstra:

- leitura da base;
- shapes;
- nulos;
- duplicatas;
- coerência por rail;
- sinais AML iniciais.

A estrutura é útil para explicar a análise, mas o caminho da base precisa ser corrigido e a execução precisa ser validada.

## Notebook 02 - Regras

Apresenta regras demonstrativas e valida alguns outputs.

Ele não substitui o motor completo de regras. A lógica principal permanece em `src/rules.py` e no catálogo `src/alerts.py`.

O arquivo `src/alerts.py` possui atualmente um erro de sintaxe que será tratado em incremento posterior.

## Notebook 03 - Machine learning

Demonstra:

- leitura das tabelas;
- criação de features;
- treino do modelo;
- cálculo básico de AUC-PR e AUC-ROC.

Ele não regenera atualmente:

- tabela completa de thresholds;
- importância de features;
- SHAP;
- gráficos;
- ranking completo;
- arquivo do modelo.

## Notebook 04 - Arquitetura multiagente

Demonstra a execução do fluxo determinístico definido em `src/agents.py`.

Ele não realiza chamadas a provedores externos de LLM.

## Formulação correta

Os notebooks reforçam a narrativa técnica e permitem inspecionar partes do processo.

Ainda não é correto afirmar que eles provam reprodução integral ou regeneram todos os artefatos versionados.

## Próximos passos

- corrigir os caminhos da planilha;
- corrigir `src/alerts.py`;
- alinhar notebooks e scripts;
- executar com Python 3.11;
- registrar kernel e dependências;
- gerar outputs de forma determinística;
- validar os artefatos produzidos;
- adicionar testes;
- documentar um comando único de execução.
