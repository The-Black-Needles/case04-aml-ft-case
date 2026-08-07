# T3 - Baseline de machine learning

## Objetivo

A T3 estrutura um baseline experimental para priorizar a fila AML na unidade cliente-mês.

O objetivo não é substituir as regras nem a investigação humana. O modelo procura ordenar casos a partir de combinações de sinais cadastrais e comportamentais.

## Label fraco

A base não possui um rótulo final de investigação ou lavagem confirmada.

Por isso, foi adotado um label fraco:

`weak_label = 1` quando pelo menos três regras determinísticas entre M01–M12 são disparadas no cliente-mês. A R17 permanece fora do label canônico.

Esse rótulo representa uma aproximação operacional baseada no motor de regras. Ele não equivale a:

- crime confirmado;
- SAR aceito;
- comunicação ao COAF;
- decisão investigativa final.

## Unidade de modelagem

A unidade escolhida foi cliente-mês.

Essa granularidade permite representar padrões acumulados, como:

- movimentação fora do perfil;
- velocity;
- concentração cross-border;
- cash-in e cash-out por proxy comportamental;
- recorrência em MCC de risco;
- volume e quantidade de transações.

## Features

As features foram organizadas em três grupos.

### Cadastrais

- renda;
- profissão;
- idade;
- classificação KYC;
- PEP;
- sanções;
- tempo de relacionamento.

### Transacionais

- volume e quantidade;
- valor médio e máximo;
- composição por PIX, Card e Wire;
- cash-in e cash-out;
- cross-border;
- alto valor;
- e-commerce sem 3DS;
- MCC de risco;
- IP anomaly;
- device rooted.

### Comparação por grupo

O comportamento do cliente foi comparado com clientes da mesma profissão no mesmo mês.

Essa comparação é adequada para uma análise mensal em lote, mas exigiria desenho temporal mais rigoroso para scoring online ou no início do mês.

## Modelo

O experimento canônico utiliza XGBoost na unidade cliente-mês com `random_state=42`.

O contrato versionado contém 21 features primárias:

- 5 categóricas;
- 16 numéricas.

O pipeline preserva princípios importantes para este tipo de problema:

- boosting sem normalização desnecessária;
- ausência de imputação cega;
- preservação de missing quando informativo;
- ausência de remoção automática de outliers;
- ponderação do desbalanceamento no treino.

A base disponível não sustenta, neste experimento canônico, uma alegação de modelos PF e PJ independentes com qualidade equivalente. Uma separação posterior deve depender da qualidade e cobertura cadastral disponível.

## Split temporal canônico

O experimento separa explicitamente treino, calibragem e teste:

- treino: julho/2025;
- calibragem: agosto/2025;
- teste temporal: setembro/2025;
- outubro/2025: excluído por mês incompleto.

Distribuição:

- treino: 2.499 registros, 236 positivos, prevalência 0,0944;
- calibragem: 2.499 registros, 254 positivos, prevalência 0,1016;
- teste: 2.498 registros, 220 positivos, prevalência 0,0881.

Esse desenho é superior ao split aleatório para o objetivo do case, mas não é `entity-independent`. Há forte sobreposição das mesmas entidades entre meses sucessivos.

## Métricas canônicas

### Calibragem — agosto/2025

- AUC-PR: 0,3396;
- AUC-ROC: 0,8150;
- precision no threshold selecionado: 0,2220;
- recall: 0,8031;
- FPR: 0,3185;
- MCC: 0,3037;
- alertas: 919 de 2.499;
- alert rate: aproximadamente 36,77%.

### Teste temporal — setembro/2025

- AUC-PR: 0,3167;
- AUC-ROC: 0,8269;
- precision: 0,2096;
- recall: 0,7773;
- FPR: 0,2831;
- MCC: 0,2986;
- alertas: 816 de 2.498;
- alert rate: aproximadamente 32,67%.

As métricas avaliam a capacidade de aproximar o `weak_label`. Elas não medem diretamente ocorrência de ilícito, SAR aceito ou decisão investigativa confirmada.

## Threshold

Os thresholds de 0,1 a 0,9 são avaliados exclusivamente na calibragem de agosto/2025.

O threshold 0,3 apresentou o maior MCC nessa grade e foi marcado como:

`max_mcc_statistical_baseline`

Esse corte é uma referência estatística experimental.

Ele não foi homologado operacionalmente e não incorpora restrições de:

- capacidade diária da fila;
- SLA;
- custo de falso positivo;
- custo de falso negativo;
- apetite a risco;
- cobertura mínima por tipologia.

Portanto, não deve ser apresentado como threshold de produção.

## Leakage e circularidade

As colunas das regras e a contagem agregada de regras não são utilizadas diretamente como preditores do label.

Isso reduz leakage direto, mas não elimina circularidade conceitual.

O `weak_label` deriva das regras M01–M12, enquanto várias features representam conceitos comportamentais correlatos aos mesmos sinais. Assim, o modelo aprende uma aproximação do mecanismo de rotulagem e não uma verdade independente sobre atividade ilícita.

Também permanece a limitação de sobreposição das mesmas entidades entre os meses do split.

## Explicabilidade

A explicabilidade canônica é reproduzível por código.

São gerados:

- feature importance nativa do XGBoost por `gain`;
- resumo SHAP sobre as 2.498 linhas do teste temporal;
- ranking dos 30 maiores scores do teste;
- cinco gráficos canônicos em português;
- manifests com hashes dos artefatos.

SHAP e feature importance são análises pós-hoc.

Eles:

- não participam do treino;
- não participam da seleção do threshold;
- não demonstram causalidade;
- devem ser interpretados em conjunto com o desenho do label e as limitações do experimento.

## Artefatos canônicos

A fonte pública atual da T3 é:

- `outputs/t3_ml_canonical/00_ml_canonical_summary.md`
- `outputs/t3_ml_canonical/01_canonical_model_dataset.csv`
- `outputs/t3_ml_canonical/02_split_distribution.csv`
- `outputs/t3_ml_canonical/03_metrics_summary.csv`
- `outputs/t3_ml_canonical/04_threshold_metrics_calibration.csv`
- `outputs/t3_ml_canonical/05_feature_importance_gain.csv`
- `outputs/t3_ml_canonical/06_shap_summary_test.csv`
- `outputs/t3_ml_canonical/07_test_scored_top30.csv`
- `outputs/t3_ml_canonical/08_run_manifest.json`
- gráficos `09` a `13`;
- `outputs/t3_ml_canonical/14_charts_manifest.json`.

## Como apresentar

“Na T3, usei as regras M01–M12 para criar um label fraco e estruturei um baseline XGBoost na unidade cliente-mês. Separei julho para treino, agosto para calibragem e setembro para teste temporal, excluindo outubro por estar incompleto. O threshold 0,3 é somente o baseline estatístico de maior MCC na calibragem e não foi homologado operacionalmente. No teste, obtive AUC-PR de 0,3167 e AUC-ROC de 0,8269. Como o label deriva das regras e há sobreposição de entidades entre meses, interpreto as métricas como capacidade de aproximar esse label fraco, não como validação produtiva ou prova independente de atividade ilícita.”

## Próximos passos

- calibrar thresholds com capacidade operacional e custos de erro;
- avaliar splits adicionais com independência por entidade;
- validar com feedback investigativo real;
- reduzir circularidade do label quando houver rótulos mais independentes;
- avaliar calibragem probabilística;
- testar estabilidade temporal e generalização;
- monitorar drift e falsos positivos/negativos;
- separar PF e PJ somente quando os dados sustentarem;
- manter revisão humana obrigatória.
