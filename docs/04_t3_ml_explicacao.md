# T3 - Baseline de machine learning

## Objetivo

A T3 estrutura um baseline experimental para priorizar a fila AML na unidade cliente-mês.

O objetivo não é substituir as regras nem a investigação humana. O modelo procura ordenar casos a partir de combinações de sinais cadastrais e comportamentais.

## Label fraco

A base não possui um rótulo final de investigação ou lavagem confirmada.

Por isso, foi adotado um label fraco:

`suspicious_label = 1` quando `rule_count >= 3`.

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

Foi estruturado um pipeline XGBoost para PF com:

- `random_state=42`;
- tratamento de variáveis categóricas;
- ponderação de classe;
- exclusão das colunas de regras e de `rule_count`;
- ausência de normalização, compatível com boosting;
- preservação de outliers e valores ausentes informativos.

A base disponível não sustenta um modelo PJ separado com a mesma qualidade cadastral. Seriam necessários campos mais robustos de CNPJ, CNAE, setor, porte, faturamento e beneficiário final.

## Split temporal

O split registrado foi:

- treino: julho e agosto de 2025;
- validação: setembro e outubro de 2025.

O uso de meses posteriores na validação é mais adequado que um split aleatório, mas não garante ausência completa de leakage.

Pontos de atenção:

- os mesmos clientes podem aparecer nos dois períodos;
- a tabela `GeoBehavior` pode agregar informações do período completo;
- outubro contém dados somente até o dia 4;
- features de comparação utilizam o grupo do próprio mês.

## Métricas registradas

Os artefatos versionados registram:

- treino: 4.998 linhas e 422 positivos;
- validação: 4.109 linhas e 189 positivos;
- AUC-PR: 0,9416;
- AUC-ROC: 0,9970;
- threshold com maior MCC na validação: 0,9;
- precision: 0,9241;
- recall: 0,7725;
- FPR: 0,0031;
- MCC: 0,8382.

## Interpretação

O desempenho elevado é esperado porque o label fraco deriva de regras construídas sobre variáveis próximas às features do modelo.

As colunas das regras e `rule_count` foram excluídas, evitando vazamento direto do rótulo. Ainda permanece circularidade conceitual entre os critérios das regras, as features e o label fraco.

O threshold de 0,9 foi selecionado pela maior MCC na própria validação. Ele deve ser tratado como referência estatística do experimento, não como threshold operacional calibrado.

## Explicabilidade

Existem outputs versionados de:

- importância nativa do XGBoost;
- valores SHAP médios absolutos;
- ranking de casos da validação.

O código público atual ainda não contém a geração completa desses artefatos. Portanto, não é correto afirmar que o pipeline público reproduz hoje toda a etapa de SHAP.

## Como apresentar

“Na T3, usei as regras para criar um label fraco e estruturei um baseline XGBoost na unidade cliente-mês. Removi as colunas de regras do treino para evitar vazamento direto, mas reconheço que ainda existe circularidade conceitual. As métricas são fortes, porém devem ser lidas como resultado experimental de priorização, não como validação de um modelo pronto para produção.”

## Próximos passos

- reconstruir todos os outputs por código versionado;
- incorporar a geração de SHAP;
- separar treino, calibragem e teste;
- avaliar sobreposição de clientes;
- reconstruir features geográficas por janela temporal;
- calibrar thresholds com capacidade operacional;
- validar com feedback investigativo real;
- monitorar drift e falsos positivos.
