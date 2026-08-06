# T3 - Baseline de Machine Learning para priorização AML/FT

## Objetivo

Esta pasta reúne os artefatos experimentais da modelagem na unidade cliente-mês.

O modelo atua como camada complementar de priorização sobre o motor de regras. Ele não substitui investigação humana, decisão de compliance ou comunicação regulatória.

## Desenho experimental

- Unidade: cliente-mês.
- População modelada: PF.
- Modelo: XGBoost.
- `random_state=42`.
- Label fraco: `suspicious_label = 1` quando `rule_count >= 3`.
- Treino: julho e agosto de 2025.
- Validação: setembro e outubro de 2025.

O label não representa:

- lavagem confirmada;
- fraude confirmada;
- caso investigado e encerrado;
- SAR aceito;
- decisão regulatória.

## Arquivos principais

- `01_model_dataset_customer_month.csv`: dataset analítico cliente-mês.
- `02_label_distribution.csv`: distribuição do label.
- `02b_weak_label_rule_contribution.csv`: contribuição das regras.
- `03_metrics_summary.csv`: métricas registradas.
- `04_threshold_metrics.csv`: métricas para thresholds de 0,1 a 0,9.
- `05_feature_importance.csv`: importância nativa do XGBoost.
- `06_shap_top_features.csv`: valores SHAP médios absolutos registrados.
- `07_validation_scored_top30.csv`: casos com maior score na validação.
- `model_xgboost_pf_pipeline.pkl`: pipeline serializado.

## Resultados registrados

- Linhas de treino: 4.998.
- Positivos no treino: 422.
- Linhas de validação: 4.109.
- Positivos na validação: 189.
- AUC-PR: 0,9416.
- AUC-ROC: 0,9970.
- Threshold com maior MCC na validação: 0,9.
- Precision: 0,9241.
- Recall: 0,7725.
- FPR: 0,0031.
- MCC: 0,8382.

## Interpretação correta

O desempenho elevado deve ser interpretado com cautela.

As colunas das regras e `rule_count` foram excluídas do treino, reduzindo leakage direto. Entretanto, o label fraco deriva de regras baseadas em comportamentos próximos às features usadas pelo modelo.

Permanece, portanto, circularidade conceitual entre:

- critérios das regras;
- features comportamentais;
- label utilizado no treino.

O threshold de 0,9 foi escolhido na própria validação. Ele é uma referência estatística do experimento, não um corte operacional calibrado.

## Limitações

- Os mesmos clientes podem aparecer em treino e validação.
- A tabela geográfica pode conter informações agregadas do período completo.
- Outubro possui dados somente até o dia 4.
- Não há conjunto independente de calibragem.
- Não há conjunto final de teste.
- O modelo PJ não foi treinado separadamente.
- O label não utiliza resultado final de investigação.
- Não existe avaliação de drift.
- Não há backtesting com decisões humanas reais.

## Explicabilidade e reprodução

Os arquivos de importância e SHAP estão versionados como artefatos do experimento.

O código público atual ainda não contém a geração integral de:

- tabela de thresholds;
- importância de features;
- valores SHAP;
- gráficos;
- ranking completo;
- serialização do modelo.

Esses artefatos podem ser inspecionados, mas ainda não são integralmente regenerados pelo pipeline público.

## Formulação para apresentação

“Na T3, usei as regras para construir um label fraco e treinei um baseline XGBoost na unidade cliente-mês. Removi as colunas das regras para reduzir vazamento direto, mas reconheço a circularidade conceitual. As métricas são experimentais e o threshold ainda não representa calibragem operacional.”

## Próximos passos

- versionar a geração completa dos outputs;
- incorporar SHAP ao código;
- reconstruir features geográficas por janela temporal;
- medir sobreposição de clientes;
- separar treino, calibragem e teste;
- calibrar thresholds por risco e capacidade operacional;
- incorporar feedback investigativo;
- monitorar drift, falsos positivos e falsos negativos.
