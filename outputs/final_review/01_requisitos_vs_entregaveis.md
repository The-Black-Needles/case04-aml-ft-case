# Requisitos do case x entregáveis no repositório

Este arquivo mapeia os requisitos originais do case para os arquivos entregues no repositório.

## T1 — Suspeitos + SAR

### Requisito

- Até 30 clientes e/ou 30 transações suspeitas.
- Tipologias AML como structuring, velocity, PEP, MCC risco, self-merchant, cash-in/cash-out, e-commerce sem 3DS, países de risco/sanções e fora de perfil.
- 1 SAR completo.

### Onde está no repo

- `outputs/t1_suspects/02_suspicious_transactions_top30.csv`
- `outputs/t1_suspects/03_suspicious_clients_top30.csv`
- `outputs/t1_suspects/07_SAR_draft_C101208.md`
- `outputs/t1_suspects/06_sar_candidate_timeline_C101208.csv`
- `docs/02_t1_suspeitos_sar_explicacao.md`
- `src/rules.py`

### Como explicar

“Na T1 eu transformei os sinais da EDA em uma fila de investigação. O ranking traz as 30 transações e os 30 clientes mais relevantes, e o SAR foi montado para um caso com combinação de sinais, materialidade e timeline investigável.”

---

## T2 — Sistema de Alertas

### Requisito

- Pelo menos 15 regras.
- Cada regra com nome, lógica, parâmetros, exemplo na base e justificativa.
- Limiares dinâmicos quando aplicável.

### Onde está no repo

- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/02_rule_coverage_by_typology.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`
- `outputs/t2_alert_system/README.md`
- `docs/03_t2_sistema_alertas_explicacao.md`
- `src/alerts.py`

### Como explicar

“Na T2 eu formalizei o motor de alertas. Cada regra tem lógica, parâmetro, severidade, tipologia, exemplo real na base e ação operacional. A prioridade vem da combinação de sinais, não de uma regra isolada.”

---

## T3 — Modelo de ML

### Requisito

- Modelo separado PF/PJ se os dados permitirem.
- Label fraco: três ou mais regras igual a suspeito.
- Features cadastrais, transacionais e semelhança por grupo.
- Modelo explicável com métricas.
- Tabela por threshold.
- Discussão de desbalanceamento, trade-offs e calibragem.

### Onde está no repo

- `outputs/t3_ml/00_T3_ml_summary.md`
- `outputs/t3_ml/01_model_dataset_customer_month.csv`
- `outputs/t3_ml/03_metrics_summary.csv`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`
- `outputs/t3_ml/06_shap_top_features.csv`
- `outputs/t3_ml/07_validation_scored_top30.csv`
- `outputs/t3_ml/README.md`
- `docs/04_t3_ml_explicacao.md`
- `notebooks/03_ml.ipynb`
- `src/features.py`
- `src/ml_model.py`

### Como explicar

“Na T3 eu usei o motor de regras para criar um label fraco e treinei um modelo de priorização. O objetivo não é substituir o analista, mas ordenar a fila AML e indicar quais fatores mais pesaram no score.”

---

## T4 — Multi-Agente LLM

### Requisito

- Script Python sequencial.
- 5 agentes:
  1. Dados
  2. Detecção
  3. Investigação
  4. Reporte
  5. Compliance
- Diagrama, código e prompts.

### Onde está no repo

- `src/agents.py`
- `notebooks/04_agents.ipynb`
- `outputs/t4_agents/01_agent_prompts.md`
- `outputs/t4_agents/02_agent_workflow_run.md`
- `outputs/t4_agents/03_agent_workflow_run.json`
- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/05_agent_roles.csv`
- `docs/05_t4_multi_agente_explicacao.md`

### Como explicar

“Na T4 eu desenhei um fluxo multi-agente sequencial. O LLM não decide sozinho. Ele organiza dados, alertas, investigação, SAR e revisão de compliance, sempre com evidências e revisão humana.”

---

## Entregáveis finais

### Relatório PDF

- `reports/AML_FT_Case_Report.pdf`
- `reports/AML_FT_Case_Report.md`

### Notebooks

- `notebooks/01_eda.ipynb`
- `notebooks/02_rules.ipynb`
- `notebooks/03_ml.ipynb`
- `notebooks/04_agents.ipynb`

### Scripts Python

- `src/rules.py`
- `src/alerts.py`
- `src/features.py`
- `src/ml_model.py`
- `src/agents.py`
- `src/utils.py`

### README

- `README.md`

### Planilhas auxiliares

As planilhas auxiliares estão em formato CSV dentro de:

- `outputs/eda_day1/`
- `outputs/t1_suspects/`
- `outputs/t2_alert_system/`
- `outputs/t3_ml/`
- `outputs/t4_agents/`
- `outputs/final_review/`

### Roteiros de apresentação

- `presentation/roteiro_final_30_40_min.md`
- `presentation/perguntas_e_respostas_banca.md`
- `presentation/roteiro_t2_sistema_alertas.md`
- `presentation/roteiro_t3_ml.md`
- `presentation/roteiro_t4_multi_agente.md`

---

## Mensagem final da entrega

“O repositório entrega uma esteira AML completa: validação de dados, EDA, regras explicáveis, ranking de suspeitos, SAR, modelo de ML com label fraco, explicabilidade e arquitetura multi-agente para apoiar a operação.”
