# T3 — Modelo de ML

## Objetivo

Construir um modelo de priorização AML usando as regras da T2 como label fraco.

## Abordagem

- Unidade de modelagem: cliente-mês.
- Modelagem PF: executada com XGBoost.
- Modelagem PJ: não executada nesta versão porque a base KYC disponível está majoritariamente estruturada como PF/CPF, sem CNAE cadastral suficiente para um modelo PJ separado.
- Label fraco: `suspicious_label = 1` quando `rule_count >= 3`.
- Split temporal: meses antigos no treino e meses recentes na validação.
- `random_state=42`.

## Features

As features foram agrupadas em três blocos:

1. Cadastrais: renda, profissão, idade, risco KYC, PEP, sanções e tempo de relacionamento.
2. Transacionais: volume, contagem, valor médio, máximo, cash-in, cash-out, cross-border, alto valor, MCC de risco, device rooted, IP anomaly e e-commerce sem 3DS.
3. Semelhança por grupo: comparação do volume mensal contra a mediana da mesma profissão no mesmo mês.

## Métricas principais

| Métrica | Valor |
|---|---:|
| AUC-PR | 0.9416 |
| AUC-ROC | 0.9970 |
| Threshold selecionado | 0.9 |
| Precision | 0.9241 |
| Recall | 0.7725 |
| FPR | 0.0031 |
| MCC | 0.8382 |

## Leitura do resultado

O modelo teve desempenho alto porque o label fraco foi derivado de regras que também usam variáveis comportamentais. Para evitar vazamento direto, as colunas de regras e `rule_count` foram removidas das features de treino. Mesmo assim, o modelo aprende padrões próximos aos critérios do motor de alertas.

Isso é aceitável para um baseline operacional, desde que fique claro que o objetivo é priorização e não decisão automática final.
