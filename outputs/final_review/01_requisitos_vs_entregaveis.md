# Matriz de requisitos e evidências do repositório

## Objetivo

Este documento relaciona cada frente do case aos artefatos públicos existentes e registra o nível real de atendimento.

Classificações:

- atendido;
- atendido com limitações;
- pendente de consolidação.

## T1 - Suspeitos, investigação e SAR

### Requisitos

- Priorizar até 30 clientes.
- Priorizar até 30 transações.
- Identificar tipologias.
- Explicar o raciocínio.
- Produzir um SAR estruturado.
- Apresentar timeline e evidências.

### Evidências

- `outputs/t1_suspects/02_suspicious_transactions_top30.csv`
- `outputs/t1_suspects/03_suspicious_clients_top30.csv`
- `outputs/t1_suspects/06_sar_candidate_timeline_C101208.csv`
- `outputs/t1_suspects/07_SAR_draft_C101208.md`
- `outputs/t1_suspects/08_sar_entity_graph_nodes_C101208.csv`
- `outputs/t1_suspects/09_sar_entity_graph_edges_C101208.csv`
- `outputs/t1_suspects/11_sar_entity_graph_C101208.png`
- `docs/02_t1_suspeitos_sar_explicacao.md`

### Estado

Atendido com base sintética e revisão humana obrigatória.

O SAR registra suspeita fundamentada e não afirma crime.

## T2 - Rule Engineering

### Requisitos

- Pelo menos 15 regras.
- Lógica e parâmetros.
- Thresholds.
- Tipologia e rail.
- Severidade.
- Exemplo na base.
- Justificativa e ação operacional.
- Cobertura de diferentes frentes de risco.

### Evidências

- `outputs/t1_suspects/01_rule_catalog_t1.csv`
- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/02_rule_coverage_by_typology.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`
- `docs/03_t2_sistema_alertas_explicacao.md`
- `src/rules.py`
- `src/alerts.py`

### Estado

Atendido parcialmente.

O motor principal possui 28 regras reproduzíveis:

- 16 transacionais;
- 12 cliente-mês.

A R17 de geo-salto foi adicionada posteriormente como enriquecimento contextual, mas ainda não está integrada de forma reproduzível ao motor principal.

Pendências:

- corrigir `src/alerts.py`;
- integrar ou separar formalmente a R17;
- adicionar testes positivos e negativos;
- registrar falsos positivos possíveis;
- avaliar redundância e conflito;
- implementar backtesting e homologação;
- criar matriz regra por rail.

## T3 - Machine Learning explicável

### Requisitos

- Label documentado.
- Features relevantes.
- Split e métricas.
- Thresholds.
- Explicabilidade.
- Discussão de limitações.

### Evidências

- `outputs/t3_ml/01_model_dataset_customer_month.csv`
- `outputs/t3_ml/02_label_distribution.csv`
- `outputs/t3_ml/03_metrics_summary.csv`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`
- `outputs/t3_ml/06_shap_top_features.csv`
- `outputs/t3_ml/07_validation_scored_top30.csv`
- `outputs/t3_ml/model_xgboost_pf_pipeline.pkl`
- `docs/04_t3_ml_explicacao.md`
- `src/features.py`
- `src/ml_model.py`

### Estado

Atendido como experimento aplicado, com limitações de reprodução.

O baseline registrado usa:

- unidade cliente-mês;
- população PF;
- XGBoost;
- label fraco de três ou mais regras;
- split temporal;
- métricas para classes desbalanceadas.

Limitações:

- circularidade conceitual do label;
- possível sobreposição de clientes;
- outubro incompleto;
- possível leakage temporal geográfico;
- threshold selecionado na validação;
- ausência de calibragem e teste independentes;
- geração de SHAP e demais outputs ainda não totalmente versionada.

## T4 - Arquitetura multiagente

### Requisitos

- Cinco papéis especializados.
- Código Python.
- Prompts.
- Diagrama.
- Entradas e saídas.
- Fluxo integrado e auditável.

### Evidências

- `src/agents.py`
- `notebooks/04_agents.ipynb`
- `outputs/t4_agents/01_agent_prompts.md`
- `outputs/t4_agents/02_agent_workflow_run.md`
- `outputs/t4_agents/03_agent_workflow_run.json`
- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/05_agent_roles.csv`
- `docs/05_t4_multi_agente_explicacao.md`

### Estado

Atendido como protótipo determinístico inicial.

A implementação atual demonstra:

- Dados;
- Detecção;
- Investigação;
- Reporte;
- Compliance;
- execução sequencial;
- prompts de referência;
- resultados estruturados;
- referências de evidência.

Ainda não demonstra:

- inferência ativa por LLM;
- orquestrador condicional;
- contratos tipados completos;
- eventos e filas;
- checkpoints humanos executáveis;
- decisão `approve`, `revise` ou `escalate`;
- logs por `run_id`;
- integração por API;
- produção.

## Notebooks

### Evidências

- `notebooks/01_eda.ipynb`
- `notebooks/02_rules.ipynb`
- `notebooks/03_ml.ipynb`
- `notebooks/04_agents.ipynb`

### Estado

Pendente de consolidação.

Os notebooks estão sem execução versionada, possuem caminhos antigos e ainda não regeneram integralmente os outputs.

## Relatório

### Fonte canônica atual

- `reports/AML_FT_Case_Report.md`

### Estado

Markdown atualizado.

O PDF anterior foi removido por estar desatualizado. Um novo PDF será gerado depois da validação técnica e narrativa.

## Mensagem final

“O repositório demonstra uma arquitetura analítica de Financial Crime que conecta dados, regras, investigação, SAR, ML experimental e agentes de IA controlados. Cada capacidade é apresentada de acordo com sua evidência atual, sem confundir protótipo, experimento e produção.”
