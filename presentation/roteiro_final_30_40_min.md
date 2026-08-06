# Roteiro técnico principal - 30 a 40 minutos

## 1. Abertura - 2 minutos

“Organizei o case como uma investigação de Financial Crime orientada a dados. O fluxo parte da qualidade da base, transforma sinais em regras explicáveis, prioriza suspeitos, estrutura um SAR, experimenta ML e propõe uma arquitetura controlada de agentes.”

## 2. Dados e coerência por rail - 5 minutos

Mostrar:

- `outputs/eda_day1/EDA_DIA1_resumo.md`
- `outputs/eda_day1/03_rail_coherence_checks.csv`

Pontos:

- 52 mil transações;
- KYC, merchants e comportamento geográfico;
- PIX, Card e Wire tratados separadamente;
- missing e outliers preservados como sinais potenciais.

Fala:

“Antes de criar alertas, validei se os dados eram coerentes. Em risco financeiro, qualidade de dados faz parte do controle.”

## 3. Sinais e hipóteses - 4 minutos

Mostrar:

- `outputs/eda_day1/04_initial_aml_signals.csv`

Pontos:

- sanções;
- PEP;
- países de risco;
- MCC;
- cross-border;
- device e IP;
- e-commerce sem 3DS;
- fora de perfil.

Fala:

“Um sinal isolado não fecha um caso. A prioridade vem da combinação, materialidade, recorrência e contexto.”

## 4. T1 - Suspeitos e SAR - 7 minutos

Mostrar:

- `outputs/t1_suspects/03_suspicious_clients_top30.csv`
- `outputs/t1_suspects/02_suspicious_transactions_top30.csv`
- `outputs/t1_suspects/06_sar_candidate_timeline_C101208.csv`
- `outputs/t1_suspects/07_SAR_draft_C101208.md`
- `outputs/t1_suspects/11_sar_entity_graph_C101208.png`

Fala:

“O cliente C101208 foi selecionado pela combinação de materialidade, incompatibilidade com renda, cross-border, país de alto risco e sanctions screening. O SAR registra suspeita fundamentada e limitações, sem afirmar crime.”

## 5. T2 - Rule Engineering - 7 minutos

Mostrar:

- `outputs/t1_suspects/01_rule_catalog_t1.csv`
- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`

Pontos:

- 28 regras no motor principal;
- 16 transacionais;
- 12 cliente-mês;
- lógica, threshold, severidade e evidência;
- R17 separada como enriquecimento contextual.

Fala:

“Comecei pelas regras porque o analista precisa explicar por que o caso entrou na fila e qual ação faz sentido.”

Destacar evolução:

- testes positivos e negativos;
- falsos positivos possíveis;
- matriz regra por rail;
- conflito e redundância;
- backtesting;
- homologação.

## 6. T3 - Machine Learning - 6 minutos

Mostrar:

- `outputs/t3_ml/03_metrics_summary.csv`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`

Fala:

“Usei as regras para construir um label fraco e treinei um baseline XGBoost cliente-mês para PF. As colunas das regras foram removidas, mas permanece circularidade conceitual.”

Destacar:

- split temporal;
- métricas de classe desbalanceada;
- threshold de 0,9 como referência estatística;
- ausência de calibragem e teste independentes;
- outubro incompleto;
- mesma entidade potencialmente em treino e validação.

## 7. T4 - Arquitetura multiagente - 5 minutos

Mostrar:

- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/01_agent_prompts.md`
- `src/agents.py`

Fala:

“A T4 atual é um protótipo determinístico com cinco papéis: Dados, Detecção, Investigação, Reporte e Compliance. Ela demonstra passagem de contexto e evidências, mas ainda não chama um LLM.”

Evolução:

- orquestrador;
- estado compartilhado;
- contratos tipados;
- handoffs;
- eventos e filas;
- checkpoints humanos;
- decisão `approve`, `revise` ou `escalate`;
- integração LLM opcional.

## 8. Limitações e próximos passos - 3 minutos

Limitações:

- base sintética;
- label fraco;
- R17 não integrada;
- notebooks sem execução versionada;
- SHAP sem geração completa pública;
- T4 sem inferência ativa por LLM;
- ausência de backtesting real.

Próximos passos:

- fundação reproduzível;
- testes de regras;
- ML regenerável;
- agentes v2;
- novo PDF canônico.

## 9. Fechamento - 1 minuto

“O principal valor do case está em conectar dados, investigação, regras, ML e agentes sem perder explicabilidade, rastreabilidade e responsabilidade humana.”
