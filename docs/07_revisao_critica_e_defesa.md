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

## 5. Por que as métricas ficaram altas?

O label fraco foi derivado de regras e as features capturam comportamentos próximos aos critérios dessas regras.

As colunas das regras e `rule_count` foram excluídas do treino, reduzindo leakage direto. Ainda permanece circularidade conceitual.

A leitura correta é:

- baseline experimental;
- resultado útil para discutir ranking;
- validação limitada à base sintética;
- necessidade de calibragem e teste independente;
- ausência de generalização automática.

Formulação:

“O desempenho alto é compatível com um label derivado das próprias regras. Por isso, não apresento as métricas como validação produtiva definitiva.”

## 6. Como interpretar o threshold?

O threshold de 0,9 apresentou a maior MCC na própria validação.

Ele não é um corte operacional definitivo.

A escolha real deveria considerar:

- capacidade de investigação;
- severidade;
- apetite de risco;
- SLA;
- custo de falso positivo;
- custo de falso negativo;
- cobertura por tipologia;
- calibragem independente.

Formulação:

“O threshold é uma decisão estatística e operacional. Um corte só pode ser adotado depois de avaliar volume, risco e capacidade do time.”

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
- R17 ainda separada do motor principal.
- Notebooks sem execução versionada.
- Outputs de ML ainda não totalmente regeneráveis.
- SHAP ainda sem geração pública completa.
- T4 sem integração ativa com LLM.
- Ausência de backtesting com decisões investigativas reais.

Formulação:

“Quando os dados ou o código não sustentam uma conclusão, registro a limitação em vez de forçar a tipologia.”

## 10. Mensagem central

“Este case demonstra como conectar qualidade de dados, regras explicáveis, priorização, investigação, SAR, ML experimental e uma arquitetura controlada de agentes. O valor está na rastreabilidade das decisões e na supervisão humana.”
