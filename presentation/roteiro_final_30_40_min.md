# Roteiro final - apresentação de 30 a 40 minutos

## 1. Abertura - 2 min

"Eu organizei o case como uma investigação AML orientada a dados. Primeiro validei a base, depois criei regras explicáveis, gerei ranking de suspeitos, estruturei um SAR, treinei um modelo de priorização e por fim propus um fluxo multi-agente para apoiar a operação."

## 2. Estrutura dos dados - 4 min

Mostrar: `outputs/eda_day1/EDA_DIA1_resumo.md`

"A base tem cinco abas principais: transações, KYC, merchants, comportamento geográfico e dicionário. A tabela principal tem 52 mil transações e a análise cobre julho a outubro de 2025."

Ponto-chave:
"Antes de criar alerta, eu validei se a base fazia sentido. Em AML, dado ruim vira falso positivo."

## 3. Coerência por rail - 5 min

Mostrar: `outputs/eda_day1/03_rail_coherence_checks.csv`

"Eu separei PIX, Card e Wire porque cada rail tem riscos diferentes. PIX olha muito para velocidade e conta de passagem. Card exige atenção em e-commerce, 3DS e MCC. Wire pede foco em cross-border, país de risco e sanções."

## 4. Sinais AML iniciais - 4 min

Mostrar: `outputs/eda_day1/04_initial_aml_signals.csv`

"Aqui apareceram sinais como sanções, PEP, clientes high risk, cross-border, país de alto risco, device rooted e e-commerce sem 3DS. Um sinal isolado não fecha caso, mas combinações de sinais viram prioridade."

## 5. T1 - Suspeitos e SAR - 7 min

Mostrar:
- `outputs/t1_suspects/03_suspicious_clients_top30.csv`
- `outputs/t1_suspects/02_suspicious_transactions_top30.csv`
- `outputs/t1_suspects/07_SAR_draft_C101208.md`

"Na T1 eu transformei os sinais em uma fila priorizada. Escolhi o cliente C101208 para SAR porque ele combina materialidade, fora de perfil, cross-border, país de alto risco e hit de sanctions screening. O SAR não acusa crime; ele comunica uma suspeita fundamentada para revisão e eventual comunicação."

## 6. T2 - Sistema de alertas - 6 min

Mostrar:
- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`

"Na T2 eu formalizei o motor de alertas. Cada regra tem lógica, parâmetro, severidade, tipologia, exemplo na base e ação operacional. Comecei por regras porque AML precisa de explicabilidade. O analista precisa explicar por que um caso entrou na fila."

## 7. T3 - ML - 7 min

Mostrar:
- `outputs/t3_ml/00_T3_ml_summary.md`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`

"Na T3 eu usei as regras como label fraco. Cliente-mês com três ou mais regras virou positivo. O modelo XGBoost não substitui o analista; ele prioriza a fila. O resultado ficou alto porque o label vem das regras, então eu apresento como baseline operacional, não como modelo perfeito."

## 8. T4 - Multi-agente - 5 min

Mostrar:
- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/01_agent_prompts.md`
- `src/agents.py`

"Na T4 eu desenhei cinco agentes: dados, detecção, investigação, reporte e compliance. O LLM entra para organizar evidência e padronizar análise, não para decidir sozinho. A revisão humana continua no centro do processo."

## 9. Fechamento - 2 min

"O valor do case está em transformar dados brutos em uma fila AML auditável, priorizada e defensável. Eu parti de qualidade de dados, criei regras explicáveis, usei ML para priorização e propus agentes para escalar a investigação com controle e rastreabilidade."
