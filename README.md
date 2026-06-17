# AML-FT Case - CloudWalk

Projeto de case AML/FT com foco em análise exploratória, regras de detecção, modelo de ML explicável, SAR e arquitetura multi-agente.

## Como apresentar este repositório

Comece pelo roteiro:

`presentation/roteiro_final_30_40_min.md`

Depois navegue nesta ordem:

1. `outputs/eda_day1/` - EDA e qualidade da base.
2. `outputs/t1_suspects/` - suspeitos e SAR.
3. `outputs/t2_alert_system/` - sistema de alertas.
4. `outputs/t3_ml/` - modelo de ML e explicabilidade.
5. `outputs/t4_agents/` - fluxo multi-agente.
6. `reports/AML_FT_Case_Report.pdf` - relatório consolidado.

## Estrutura

```text
aml-ft-case/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_rules.ipynb
│   ├── 03_ml.ipynb
│   └── 04_agents.ipynb
├── src/
│   ├── rules.py
│   ├── alerts.py
│   ├── features.py
│   ├── ml_model.py
│   ├── agents.py
│   └── utils.py
├── outputs/
│   ├── eda_day1/
│   ├── t1_suspects/
│   ├── t2_alert_system/
│   ├── t3_ml/
│   ├── t4_agents/
│   └── final_review/
├── docs/
├── reports/
└── presentation/
```

## Entregas

### T1 - Suspeitos + SAR

- Top 30 transações suspeitas.
- Top 30 clientes suspeitos.
- SAR draft do cliente C101208.

### T2 - Sistema de alertas

- 28 regras documentadas.
- Lógica, parâmetros, severidade, exemplo na base e ação operacional.

### T3 - Modelo de ML

- XGBoost PF cliente-mês.
- Label fraco: três ou mais regras disparadas.
- Split temporal.
- Métricas: AUC-PR, AUC-ROC, precision, recall, FPR e MCC.

### T4 - Multi-agente LLM

- 5 agentes sequenciais: Dados, Detecção, Investigação, Reporte e Compliance.
- Prompts, diagrama e script Python.

## Frase central do case

O valor do case está em transformar dados brutos em uma fila AML auditável, priorizada e defensável para investigação.
