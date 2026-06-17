# T3 — Modelo de ML: explicação para apresentação

## Objetivo da T3

Na T3, o objetivo foi criar um modelo de ML para priorizar a fila AML.

Eu não comecei pelo ML do zero. Primeiro construí regras explicáveis na T2. Depois usei essas regras para criar um label fraco.

A lógica foi: se um cliente-mês dispara três ou mais regras AML, ele recebe `suspicious_label = 1`.

## Por que usar label fraco

Em AML, muitas bases não têm rótulo perfeito de “lavagem confirmada”. O que temos normalmente são alertas, investigações, comunicações, encerramentos ou feedback parcial do time operacional.

Então usei label fraco porque ele permite criar um primeiro modelo mesmo sem ter uma base histórica de casos confirmados.

Mas é importante deixar claro: label fraco não é verdade absoluta. Ele é uma aproximação operacional.

## Unidade de modelagem

A unidade escolhida foi cliente-mês.

Isso faz sentido porque várias tipologias AML não aparecem em uma transação isolada. Elas aparecem no comportamento acumulado: volume fora de perfil, cash-in seguido de cash-out, concentração em MCC de risco, cross-border, alto valor e velocidade.

## Features usadas

As features foram organizadas em três grupos:

1. Cadastrais: renda, profissão, idade, risco KYC, PEP, sanções e tempo de relacionamento.
2. Transacionais: volume, quantidade, valor médio, valor máximo, PIX, Card, Wire, cash-in, cash-out, cross-border, alto valor, e-commerce sem 3DS, MCC de risco, IP anomaly e device rooted.
3. Semelhança por grupo: comparação do cliente contra outros clientes da mesma profissão no mesmo mês.

## Modelo escolhido

Usei XGBoost porque ele funciona bem com dados tabulares, captura relações não lineares e não exige normalização.

Também mantive a lógica de não remover outliers, porque em AML o outlier pode ser exatamente o sinal relevante.

Para valores ausentes, a ideia foi não imputar cegamente. Missing pode ser informativo. Para variáveis categóricas, missing foi tratado como categoria explícita. Para numéricas, o boosting consegue lidar melhor com ausência do que modelos lineares tradicionais.

## Split temporal

Usei split temporal:

- Treino: 2025-07 e 2025-08.
- Validação: 2025-09 e 2025-10.

Isso evita usar informação do futuro para prever o passado e simula melhor um cenário real de produção.

## Métricas

Avaliei:

- AUC-PR.
- AUC-ROC.
- Precision.
- Recall.
- FPR.
- MCC.
- Tabela de threshold de 0.1 a 0.9.

Em AML, eu não olharia só acurácia, porque a base é desbalanceada. O mais importante é o trade-off entre recall, precision, FPR e capacidade operacional do time.

## Explicabilidade

Usei SHAP para explicar quais features mais influenciaram o score.

Isso é importante porque, em AML, um modelo caixa-preta é difícil de defender. O analista precisa entender por que o modelo priorizou determinado cliente.

## Limitação importante

O modelo separado PJ não foi treinado nesta versão porque a base KYC está estruturada principalmente como PF. Para PJ, eu precisaria de campos como CNPJ, CNAE, setor econômico, porte, faturamento e beneficiário final com mais consistência.

## Como explicar em entrevista

“Na T3 eu usei as regras da T2 para criar um label fraco. Se um cliente-mês disparou três ou mais regras AML, ele virou positivo para treino. Depois criei features cadastrais, transacionais e de comparação por profissão, treinei um XGBoost para PF e validei em meses mais recentes. Removi as colunas de regras do treino para evitar vazamento direto. O objetivo do ML não é substituir o analista, mas priorizar melhor a fila e explicar quais fatores pesaram no score.”

## Frase de fechamento

“O ML entra como camada de priorização em cima de uma base explicável de regras. Isso mantém o processo auditável e ajuda o time a focar primeiro nos casos com maior combinação de risco.”
