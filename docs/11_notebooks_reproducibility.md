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

Os notebooks 01 e 02 usam a entrada sintética sanitizada `data/raw/AML_FT_Case_Synthetic_Data.xlsx`. O Notebook 03 não depende diretamente da planilha: ele opera sobre o contrato canônico da T3 e compara outputs regenerados com `outputs/t3_ml_canonical/`.

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

O arquivo `src/alerts.py` compila no estado atual do repositório. A T2 continua separada deste incremento de documentação de ML.

## Notebook 03 - Machine learning

Demonstra:

- construção do dataset canônico cliente-mês;
- split temporal explícito entre treino, calibragem e teste;
- treino do XGBoost com `random_state=42`;
- métricas canônicas de classificação;
- seleção estatística de threshold na calibragem;
- feature importance por gain;
- SHAP no teste temporal;
- ranking canônico do teste;
- geração dos outputs tabulares por código versionado.

Os gráficos canônicos são gerados separadamente por `src/plot_ml.py`, a partir dos outputs tabulares de `outputs/t3_ml_canonical/`.

O modelo treinado não é persistido como artefato de produção; o objetivo é reproduzir o experimento e seus outputs analíticos.

## Notebook 04 - Arquitetura multiagente

Demonstra a execução do fluxo determinístico definido em `src/agents.py`.

Ele não realiza chamadas a provedores externos de LLM.

## Formulação correta

Os notebooks têm escopos diferentes e não devem ser tratados de forma uniforme.

O Notebook 03 está alinhado ao pipeline canônico de ML e à geração reproduzível dos artefatos tabulares da T3.

Os gráficos são gerados pelo script tipado `src/plot_ml.py`.

Os notebooks 01, 02 e 04 continuam devendo ser apresentados de acordo com seus respectivos escopos demonstráveis, sem extrapolar para uma afirmação de reprodução integral de todo o repositório.

A evidência principal de reprodutibilidade da T3 é o conjunto formado por:

- código versionado;
- testes automatizados;
- outputs em `outputs/t3_ml_canonical/`;
- manifests com hashes;
- Notebook 03 alinhado ao pipeline;
- gerador reproduzível dos gráficos.

## Próximos passos

- manter notebooks executáveis ponta a ponta;
- preservar contratos de entrada e saída;
- evitar divergência entre notebooks, scripts e outputs;
- registrar versões de dependências;
- manter testes de regressão e hashes dos artefatos;
- não confundir reprodutibilidade experimental com prontidão produtiva.
