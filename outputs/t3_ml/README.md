# T3 — Modelo de ML AML

## O que tem nesta pasta

Esta pasta contém os artefatos da T3: base modelada cliente-mês, label fraco, métricas, tabela de thresholds, explicabilidade por SHAP e top casos ranqueados pelo modelo.

## Arquivos principais

- `01_model_dataset_customer_month.csv`: dataset analítico cliente-mês com features cadastrais, transacionais e semelhança por profissão.
- `02_label_distribution.csv`: distribuição do label fraco por mês e tipo de entidade.
- `02b_weak_label_rule_contribution.csv`: contribuição das regras para o label fraco.
- `03_metrics_summary.csv`: métricas principais do XGBoost PF.
- `04_threshold_metrics.csv`: precision, recall, FPR e MCC de 0.1 a 0.9.
- `05_feature_importance.csv`: importância nativa do XGBoost.
- `06_shap_top_features.csv`: explicabilidade por SHAP médio absoluto.
- `07_validation_scored_top30.csv`: top 30 cliente-mês por score na validação.
- `model_xgboost_pf_pipeline.pkl`: pipeline treinado com preprocessamento + XGBoost.

## Resultado resumido

- Unidade de modelagem: cliente-mês.
- Modelo usado: XGBoost PF.
- Label fraco: `suspicious_label = 1` quando `rule_count >= 3`.
- Split: treino em 2025-07 e 2025-08; validação em 2025-09 e 2025-10.
- Linhas de treino: 4998.
- Linhas de validação: 4109.
- Positivos no treino: 422.
- Positivos na validação: 189.
- AUC-PR: 0.9416.
- AUC-ROC: 0.9970.
- Threshold operacional sugerido pela maior MCC: 0.9.
- Precision nesse threshold: 0.9241.
- Recall nesse threshold: 0.7725.
- FPR nesse threshold: 0.0031.
- MCC nesse threshold: 0.8382.

## Como explicar em 1 minuto

“Na T3 eu usei as regras da T2 para criar um label fraco. A regra foi: se um cliente-mês dispara três ou mais regras AML, ele vira suspeito para treino. Depois criei features cadastrais, transacionais e de comparação por profissão, treinei um XGBoost para PF e validei em meses mais recentes. A ideia não é substituir as regras nem o analista, mas priorizar melhor a fila e capturar combinações de sinais.”

## Limitações e trade-offs

A base tem KYC principalmente de PF, então o modelo PJ não foi treinado de forma separada nesta versão. Para PJ, seria necessário ter uma base cadastral robusta de CNPJ/CNAE e histórico transacional suficiente.

O label é fraco porque foi derivado das regras. Isso é útil para construir um baseline explicável, mas não equivale a uma marcação oficial de SAR confirmado. Em produção, eu calibraria os thresholds com feedback de analistas, casos confirmados, falsos positivos e custo operacional da fila.
