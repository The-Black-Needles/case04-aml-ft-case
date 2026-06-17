# Roteiro T3 — Modelo de ML

## Tempo sugerido

6 a 8 minutos.

## Como introduzir

“Depois de criar as regras, eu usei essas regras para construir um label fraco e treinar um modelo de priorização.”

## O que abrir no repo

Abrir:

`outputs/t3_ml/README.md`

Depois mostrar:

- `03_metrics_summary.csv`
- `04_threshold_metrics.csv`
- `06_shap_top_features.csv`
- `07_validation_scored_top30.csv`

## Fala principal

“Na T3 eu não tratei o ML como uma caixa mágica. Primeiro criei regras explicáveis. Depois usei a regra de três ou mais alertas para criar o label fraco. Com isso, montei uma base cliente-mês e treinei um XGBoost para PF.”

## Ponto de explicação

“O split foi temporal: treino nos meses antigos e validação nos meses recentes. Isso é mais realista do que um split aleatório, porque em produção eu quero prever o que vem depois, não embaralhar passado e futuro.”

## Trade-off

“O threshold não é uma decisão puramente estatística. Ele depende da capacidade operacional do time. Um threshold menor aumenta recall, mas gera mais alertas. Um threshold maior reduz falsos positivos, mas pode deixar caso suspeito passar.”

## Explicabilidade

“Usei SHAP para mostrar quais variáveis mais pesaram no score. Isso é essencial em AML porque o modelo precisa ser defensável para investigação, auditoria e compliance.”

## Fechamento

“O modelo não substitui as regras nem o analista. Ele entra como uma camada de priorização, ajudando a ordenar a fila de investigação.”
