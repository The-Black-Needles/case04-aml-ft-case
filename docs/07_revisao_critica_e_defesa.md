# Revisão crítica e defesa do case

## Objetivo

Este documento organiza os principais argumentos técnicos para apresentação e entrevista.

O objetivo não é decorar respostas, mas explicar decisões, evidências, limitações e trade-offs com clareza.

## 1. Por que começar pela EDA?

Em AML/FT, uma regra aplicada sobre dados incoerentes pode gerar falsos positivos, falsos negativos e perda de confiança operacional.

Antes de priorizar suspeitos, foram avaliados:

- estrutura e volume das tabelas;
- tipos de transação;
- valores ausentes;
- duplicatas;
- datas;
- valores inconsistentes;
- relacionamentos entre clientes, transações e merchants;
- coerência por rail.

Formulação:

“Antes de criar alertas, validei se os dados faziam sentido. Em Financial Crime, qualidade de dados faz parte do controle.”

## 2. Por que separar por rail?

PIX, Card e Wire possuem campos, comportamentos e riscos diferentes.

PIX exige atenção a:

- velocity;
- cash-in e cash-out;
- conta de passagem;
- mule account;
- concentração de contrapartes.

Card exige atenção a:

- e-commerce;
- 3DS e ECI;
- MCC;
- chargeback;
- card-present e card-not-present.

Wire exige atenção a:

- cross-border;
- país de destino;
- sanções;
- alto valor;
- moeda e origem.

Formulação:

“Tratar todos os rails como equivalentes aumentaria ruído e reduziria a qualidade das regras.”

## 3. Por que usar regras antes de ML?

Regras permitem identificar:

- o que aconteceu;
- qual parâmetro foi utilizado;
- por que o sinal é relevante;
- qual evidência sustenta o alerta;
- qual ação operacional pode ser avaliada.

O ML entra como camada complementar de priorização.

Formulação:

“As regras oferecem explicabilidade e controle. O ML pode ajudar a ordenar a fila e capturar combinações não lineares.”

## 4. Por que usar label fraco?

A base não possui label investigativo final.

Foi adotada a aproximação:

- cliente-mês com três ou mais regras: positivo;
- demais casos: negativo no experimento.

Esse label não representa:

- crime confirmado;
- fraude confirmada;
- SAR aceito;
- comunicação regulatória;
- conclusão investigativa.

Formulação:

“Como não havia label final, usei as regras como proxy para construir um baseline de priorização.”

## 5. Como interpretar as métricas?

O baseline canônico possui desempenho moderado na aproximação do label fraco.

No teste temporal de setembro/2025:

- AUC-PR: 0,3167;
- AUC-ROC: 0,8269;
- precision: 0,2096;
- recall: 0,7773;
- FPR: 0,2831;
- MCC: 0,2986;
- 816 alertas em 2.498 registros.

O ponto central não é tratar esses números como evidência de detecção independente de ilícito.

O label fraco foi derivado das regras M01–M12 e as features capturam conceitos comportamentais correlatos. As colunas das regras e a contagem agregada não entram diretamente no treino, reduzindo leakage direto, mas permanece circularidade conceitual.

Além disso, o split é temporal, mas as mesmas entidades aparecem em meses sucessivos.

A leitura correta é:

- baseline experimental;
- resultado útil para discutir priorização;
- validação limitada à base sintética;
- teste temporal separado da calibragem;
- ausência de independência entre entidades;
- ausência de generalização automática;
- ausência de validação produtiva.

Formulação:

“O modelo apresenta capacidade moderada de aproximar o label fraco no teste temporal. Como o rótulo deriva das próprias regras e há sobreposição de entidades entre meses, não apresento as métricas como prova independente de detecção nem como validação produtiva.”

## 6. Como interpretar o threshold?

O threshold 0,3 apresentou o maior MCC na grade de 0,1 a 0,9 avaliada exclusivamente na calibragem de agosto/2025.

A regra registrada é:

`max_mcc_statistical_baseline`

Ele não é um corte operacional definitivo.

A escolha real deveria considerar:

- volume de alertas;
- capacidade da fila;
- SLA;
- custo de falso positivo;
- custo de falso negativo;
- cobertura por tipologia;
- apetite a risco;
- calibragem e feedback operacional.

No teste temporal, esse baseline gera 816 alertas em 2.498 registros, aproximadamente 32,67% da população. Esse volume reforça por que a escolha estatística não deve ser confundida com homologação operacional.

Formulação:

“O threshold 0,3 é somente o baseline estatístico de maior MCC na calibragem. Um corte operacional precisaria equilibrar risco, volume, custo dos erros e capacidade real de investigação.”

## 7. Por que o SAR não afirma crime?

SAR ou comunicação de suspeita não equivale a condenação.

O documento organiza:

- fatos;
- alertas;
- materialidade;
- timeline;
- evidências;
- limitações;
- recomendação para revisão.

Formulação:

“O SAR registra uma suspeita fundamentada. A decisão final continua sujeita aos processos internos e às autoridades competentes.”

## 8. Como defender a T4 atual?

A T4 atual é um protótipo determinístico de arquitetura multiagente.

Ela demonstra:

- cinco papéis especializados;
- prompts de referência;
- execução sequencial;
- passagem de contexto;
- evidências;
- revisão humana como princípio.

Ela ainda não demonstra:

- inferência real por LLM;
- orquestrador completo;
- eventos e filas executáveis;
- checkpoints humanos implementados;
- decisões `approve`, `revise` ou `escalate`;
- integração com API;
- operação produtiva.

Formulação:

“Na versão atual, construí uma simulação determinística dos cinco papéis. A evolução planejada inclui estado compartilhado, contratos tipados, handoffs, checkpoints humanos, logs e integração LLM opcional.”

## 9. Principais limitações

- Base integralmente sintética.
- Ausência de label investigativo final.
- Ausência de campo explícito de espécie.
- Device e IP com baixa reutilização para análise de rings.
- R17 ainda separada do motor principal e fora do label canônico.
- O split canônico é temporal, mas não independente por entidade.
- O label fraco mantém circularidade conceitual com parte das features.
- O threshold estatístico ainda não possui homologação operacional.
- Os outputs canônicos de ML, SHAP e gráficos são regeneráveis por código; isso não equivale a validação produtiva.
- T4 sem integração ativa com LLM.
- Ausência de backtesting com decisões investigativas reais.

Formulação:

“Quando os dados ou o código não sustentam uma conclusão, registro a limitação em vez de forçar a tipologia.”

## 10. Mensagem central

“Este case demonstra como conectar qualidade de dados, regras explicáveis, priorização, investigação, SAR, ML experimental e uma arquitetura controlada de agentes. O valor está na rastreabilidade das decisões e na supervisão humana.”
