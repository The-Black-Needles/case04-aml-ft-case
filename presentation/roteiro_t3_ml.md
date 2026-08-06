# Roteiro T3 - Machine Learning explicável

## Tempo sugerido

5 a 7 minutos.

## Introdução

“Depois de construir o motor de regras, usei seus resultados para criar um label fraco e estruturar um baseline de priorização cliente-mês.”

## Arquivos para mostrar

- `outputs/t3_ml/03_metrics_summary.csv`
- `outputs/t3_ml/04_threshold_metrics.csv`
- `outputs/t3_ml/05_feature_importance.csv`
- `outputs/t3_ml/06_shap_top_features.csv`
- `outputs/t3_ml/07_validation_scored_top30.csv`
- `docs/04_t3_ml_explicacao.md`

## Desenho experimental

- Modelo: XGBoost.
- População: PF.
- Unidade: cliente-mês.
- Label: três ou mais regras disparadas.
- Treino: julho e agosto de 2025.
- Validação: setembro e outubro de 2025.
- `random_state=42`.

Fala:

“O label não representa fraude ou lavagem confirmada. Ele funciona como proxy experimental de relevância para a fila.”

## Leakage e circularidade

Fala:

“Removi do treino as colunas das regras e `rule_count`, reduzindo vazamento direto. Mesmo assim, existe circularidade conceitual porque o label e as features representam comportamentos próximos.”

## Métricas

Resultados registrados:

- AUC-PR: 0,9416.
- AUC-ROC: 0,9970.
- Precision: 0,9241.
- Recall: 0,7725.
- FPR: 0,0031.
- MCC: 0,8382.

Fala:

“As métricas são altas, mas devem ser interpretadas no contexto do label fraco e da base sintética. Elas não validam um modelo produtivo.”

## Threshold

Fala:

“O threshold de 0,9 apresentou a maior MCC na própria validação. Portanto, ele é uma referência estatística, não um corte operacional calibrado.”

Explicar que a decisão real depende de:

- capacidade da fila;
- severidade;
- SLA;
- custo de falso positivo;
- custo de falso negativo;
- cobertura de risco;
- apetite da instituição.

## Explicabilidade

Fala:

“Os artefatos de importância e SHAP mostram como a explicabilidade foi analisada no experimento. A geração completa desses outputs ainda precisa ser incorporada ao código público.”

## Limitações

- mesmos clientes podem aparecer em treino e validação;
- possível agregação geográfica do período completo;
- outubro incompleto;
- ausência de conjunto de calibragem;
- ausência de teste final;
- ausência de feedback investigativo;
- modelo PJ não treinado.

## Fechamento

“O ML agrega como camada complementar de priorização. Regras preservam a explicação operacional, enquanto o modelo ajuda a ordenar combinações de sinais.”
