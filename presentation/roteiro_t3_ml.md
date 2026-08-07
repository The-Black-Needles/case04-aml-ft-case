# Roteiro de apresentação - T3 Machine Learning

## Tempo sugerido

5 a 7 minutos.

## Introdução

“Depois de construir o motor de regras, usei os resultados das regras M01–M12 para criar um label fraco e estruturar um baseline de priorização cliente-mês.”

## Arquivos para mostrar

- `outputs/t3_ml_canonical/03_metrics_summary.csv`
- `outputs/t3_ml_canonical/04_threshold_metrics_calibration.csv`
- `outputs/t3_ml_canonical/05_feature_importance_gain.csv`
- `outputs/t3_ml_canonical/06_shap_summary_test.csv`
- `outputs/t3_ml_canonical/07_test_scored_top30.csv`
- `outputs/t3_ml_canonical/10_chart_02_tradeoff_thresholds_calibracao.png`
- `outputs/t3_ml_canonical/13_chart_05_shap_top_features.png`
- `docs/04_t3_ml_explicacao.md`

## Desenho experimental

- Unidade: cliente-mês.
- Label: `weak_label` derivado exclusivamente de M01–M12.
- R17: fora do label canônico.
- Treino: julho/2025.
- Calibragem: agosto/2025.
- Teste temporal: setembro/2025.
- Outubro/2025: excluído por mês incompleto.
- Features: 5 categóricas + 16 numéricas.
- `random_state=42`.

Fala:

“Separei treino, calibragem e teste por mês. Isso é melhor que um split aleatório para este case, mas não elimina a sobreposição de entidades entre meses.”

## Métricas

Resultados no teste temporal:

- AUC-PR: 0,3167.
- AUC-ROC: 0,8269.
- Precision: 0,2096.
- Recall: 0,7773.
- FPR: 0,2831.
- MCC: 0,2986.
- 816 alertas em 2.498 registros.

Fala:

“Essas métricas mostram capacidade moderada de aproximar o label fraco. Como o rótulo deriva das regras, não trato o resultado como prova independente de detecção nem como validação produtiva.”

## Threshold

Fala:

“Na calibragem de agosto, comparei thresholds de 0,1 a 0,9. O threshold 0,3 teve o maior MCC pela regra `max_mcc_statistical_baseline`, mas não foi homologado operacionalmente.”

Explicar que a decisão real depende de:

- capacidade da fila;
- SLA;
- custo de falso positivo;
- custo de falso negativo;
- cobertura de risco;
- apetite da instituição.

## Explicabilidade

Fala:

“Feature importance por gain e SHAP são regeneráveis por código. O SHAP foi calculado nas 2.498 linhas do teste temporal e é usado como explicabilidade pós-hoc, sem participar do treino ou da seleção do threshold.”

## Limitações

- base integralmente sintética;
- label fraco e circularidade conceitual;
- split temporal sem independência por entidade;
- outubro excluído por mês incompleto;
- threshold estatístico sem homologação operacional;
- ausência de feedback investigativo real e independente;
- modelo PJ separado não sustentado pelos dados atuais;
- explicabilidade pós-hoc não implica causalidade.

## Fechamento

“O modelo complementa as regras como camada experimental de priorização. Regras continuam sendo o núcleo explicável, e qualquer uso operacional exigiria calibragem, validação independente e revisão humana.”
