# Mapa rápido para apresentar o repositório

Este é o caminho recomendado para uma apresentação técnica curta e estruturada.

## 1. Contexto e objetivo

Abrir:

- `README.md`

Fala:

“O objetivo do case é transformar dados sintéticos de Financial Crime em uma fila de investigação priorizada, explicável e auditável.”

## 2. EDA e coerência

Abrir:

- `outputs/eda_day1/EDA_DIA1_resumo.md`
- `outputs/eda_day1/03_rail_coherence_checks.csv`
- `outputs/eda_day1/04_initial_aml_signals.csv`

Fala:

“Antes de criar regras, validei qualidade e coerência. PIX, Card e Wire foram analisados separadamente porque possuem riscos e campos distintos.”

## 3. Suspeitos, timeline e SAR

Abrir:

- `outputs/t1_suspects/02_suspicious_transactions_top30.csv`
- `outputs/t1_suspects/03_suspicious_clients_top30.csv`
- `outputs/t1_suspects/06_sar_candidate_timeline_C101208.csv`
- `outputs/t1_suspects/07_SAR_draft_C101208.md`
- `outputs/t1_suspects/11_sar_entity_graph_C101208.png`

Fala:

“A fila prioriza combinação de sinais, materialidade e recorrência. O SAR organiza uma suspeita fundamentada, sem afirmar crime.”

## 4. Rule Engineering

Abrir:

- `outputs/t1_suspects/01_rule_catalog_t1.csv`
- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`

Fala:

“O motor principal possui 28 regras explicáveis. A R17 foi adicionada posteriormente como enriquecimento contextual e ainda permanece separada do pipeline principal.”

Pontos para discutir:

- lógica e thresholds;
- severidade;
- rail;
- falso positivo;
- evidência;
- ação operacional;
- impacto na fila.

## 5. Machine Learning

Abrir:

- `outputs/t3_ml/03_metrics_summary.csv`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`
- `outputs/t3_ml/06_shap_top_features.csv`

Fala:

“O XGBoost foi estruturado como baseline cliente-mês com label fraco. As métricas são altas, mas devem ser interpretadas à luz da circularidade do label, do split e das limitações de reprodução.”

Ponto de transparência:

“Os artefatos de SHAP estão versionados, mas sua geração completa ainda precisa ser incorporada ao código público.”

## 6. Arquitetura de agentes

Abrir:

- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/01_agent_prompts.md`
- `src/agents.py`

Fala:

“A T4 atual demonstra cinco papéis em uma simulação determinística: Dados, Detecção, Investigação, Reporte e Compliance. Ainda não há inferência real por LLM.”

Evolução planejada:

- orquestrador explícito;
- estado compartilhado;
- contratos tipados;
- handoffs;
- eventos e filas;
- checkpoints humanos;
- decisão `approve`, `revise` ou `escalate`;
- logs e testes.

## 7. Relatório técnico

Abrir:

- `reports/AML_FT_Case_Report.md`

Fala:

“O Markdown é a fonte canônica do relatório. O PDF anterior foi removido e será regenerado após a validação completa do repositório.”

## 8. Limitações e defesa

Abrir:

- `docs/07_revisao_critica_e_defesa.md`
- `presentation/perguntas_e_respostas_banca.md`

Fala:

“O case separa claramente resultado experimental, capacidade demonstrada e itens ainda não implementados.”

## Fechamento

“O principal valor está em conectar investigação, regras, dados, ML e agentes de IA sem perder explicabilidade, rastreabilidade ou responsabilidade humana.”
