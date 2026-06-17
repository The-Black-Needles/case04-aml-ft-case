# Mapa rápido para apresentar o repo

Este é o caminho recomendado para apresentar o case navegando pelo repositório.

## 1. Começar pelo README

Arquivo:

- `README.md`

Fala:

“Esse é o mapa geral do case. Eu organizei o projeto como uma esteira AML completa, saindo de dados brutos até relatório, SAR, ML e multi-agente.”

---

## 2. Mostrar EDA

Pasta:

- `outputs/eda_day1/`

Arquivos principais:

- `EDA_DIA1_resumo.md`
- `03_rail_coherence_checks.csv`
- `04_initial_aml_signals.csv`

Fala:

“Antes de criar regras, eu validei qualidade e coerência dos dados. Separei por rail porque PIX, cartão e wire têm riscos diferentes.”

---

## 3. Mostrar suspeitos e SAR

Pasta:

- `outputs/t1_suspects/`

Arquivos principais:

- `02_suspicious_transactions_top30.csv`
- `03_suspicious_clients_top30.csv`
- `07_SAR_draft_C101208.md`

Fala:

“Aqui está a fila de investigação. Eu priorizei clientes e transações com maior concentração de sinais, e escolhi um caso com materialidade e timeline para estruturar o SAR.”

---

## 4. Mostrar sistema de alertas

Pasta:

- `outputs/t2_alert_system/`

Arquivo principal:

- `01_alert_rules_catalog_t2.csv`

Fala:

“Esse é o catálogo do motor de alertas. Cada regra tem lógica, parâmetro, severidade, tipologia, exemplo na base e ação operacional sugerida.”

---

## 5. Mostrar ML

Pasta:

- `outputs/t3_ml/`

Arquivos principais:

- `00_T3_ml_summary.md`
- `04_threshold_metrics.csv`
- `05_feature_importance.csv`
- `06_shap_top_features.csv`

Fala:

“O modelo usa label fraco vindo das regras. Ele não substitui o analista; ele prioriza a fila e ajuda a entender quais fatores pesaram no score.”

---

## 6. Mostrar multi-agente

Pasta:

- `outputs/t4_agents/`

Arquivos principais:

- `01_agent_prompts.md`
- `04_agent_diagram.mmd`
- `02_agent_workflow_run.md`

Fala:

“O fluxo multi-agente organiza a operação em cinco etapas: dados, detecção, investigação, reporte e compliance. A proposta é aumentar padronização e produtividade, mantendo revisão humana.”

---

## 7. Mostrar relatório final

Pasta:

- `reports/`

Arquivo principal:

- `AML_FT_Case_Report.pdf`

Fala:

“Este PDF consolida a entrega executiva em 5 páginas, cobrindo metodologia, achados, regras, SAR, ML e multi-agente.”

---

## 8. Fechar com defesa

Arquivos:

- `docs/07_revisao_critica_e_defesa.md`
- `presentation/perguntas_e_respostas_banca.md`

Fala:

“Também deixei registrada uma revisão crítica, com limitações, trade-offs e respostas para perguntas prováveis. Isso mostra que eu não tratei o case como modelo perfeito, mas como uma solução defensável e evolutiva.”

---

## Frase final

“Meu objetivo foi transformar uma base transacional em uma fila AML auditável, explicável e priorizada, conectando investigação, regras, ML e automação com LLM.”
