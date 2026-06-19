# Relatório AML/FT - Case

**Timezone:** America/Sao_Paulo  
**Data de geração:** 17/06/2026  
**Repositório:** aml-ft-case

## 1. Resumo executivo

Este case foi tratado como uma investigação AML/FT orientada a dados. A abordagem começou pela validação da base e coerência por rail, avançou para regras explicáveis, ranking de suspeitos, SAR estruturado, modelo de ML com label fraco e fluxo multi-agente para apoiar investigação e reporte.

A base analisada possui 52.000 transações, 2.500 clientes KYC, 1.000 merchants e 3.497 registros de comportamento geográfico. O período transacional cobre 2025-07-01 a 2025-10-04.

Foram formalizadas 28 regras de alerta: 16 transacionais e 12 cliente-mês. O cliente selecionado para SAR foi **C101208**, por combinação de sanções transacionais, país de alto risco, cross-border e comportamento fora de perfil.

## 2. Metodologia

A metodologia seguiu cinco etapas:

1. EDA e qualidade da base.
2. Validação por rail: PIX, Card e Wire.
3. Regras AML/FT e ranking de suspeitos.
4. ML com label fraco baseado nas regras.
5. Multi-agente LLM com revisão humana.

O princípio central foi **regras primeiro, ML depois**. Em AML, isso é importante porque alertas precisam ser auditáveis, defensáveis e compreensíveis para o analista.

## 3. EDA e qualidade dos dados

A EDA identificou base consistente: sem duplicatas relevantes, sem timestamps inválidos e sem valores negativos ou zerados em `amount_brl`. Os campos `n/a` foram tratados como informativos, principalmente por diferença entre rails.

Distribuição por rail:

- PIX: 31.547 transações (60,67%).
- Card: 17.930 transações (34,48%).
- Wire: 2.523 transações (4,85%).

Sinais iniciais relevantes:

- 2 transações com sanctions screening hit.
- 9 clientes com sanctions list hit cadastral.
- 80 clientes PEP.
- 196 clientes KYC high risk.
- 10.113 transações cross-border.
- 4.633 transações card e-commerce sem 3DS.

Limitação relevante: a base não possui campo explícito de espécie/cash físico. Por isso, transações acima de R$50 mil foram tratadas como alto valor, não como comunicação automática de espécie.

## 4. Sistema de alertas

A T2 transformou os sinais da EDA em um catálogo operacional com 28 regras. Cada regra tem nome, lógica, parâmetros, severidade, tipologia, rail aplicável, exemplo na base, justificativa, ação operacional e controle de falso positivo.

As regras foram separadas em:

- Regras transacionais: sanções, país de alto risco, alto valor, e-commerce sem 3DS, MCC de risco, device/IP risk e self-merchant.
- Regras cliente-mês: fora de perfil, alto volume mensal, velocity, concentração cross-border, cash-in/cash-out proxy e repetição de MCC de risco.

A prioridade final considera quantidade de alertas, severidade, materialidade, KYC, repetição temporal e concentração por país, rail, merchant ou contraparte.

## 5. Suspeitos e SAR

A T1 gerou rankings de transações e clientes suspeitos. O cliente **C101208** foi escolhido para SAR por apresentar:

- movimentação total de R$ 162.018,32 em 34 transações;
- renda anual declarada de R$ 13.047,00;
- 9 transações cross-border;
- 1 hit de sanctions screening em Wire;
- transação para `receiver_country=SY`, país de risco alto na base;
- alertas mensais recorrentes de fora de perfil e concentração de risco.

O SAR foi estruturado com identificação, resumo executivo, sinais, timeline, análise, base legal em alto nível, conclusão e ações recomendadas. O SAR não afirma crime; ele registra suspeita fundamentada para revisão e eventual comunicação.

## 6. Modelo de ML

A T3 criou um modelo de priorização AML na unidade cliente-mês. O label fraco foi definido como `suspicious_label = 1` quando o cliente-mês disparou três ou mais regras AML.

O modelo implementado foi XGBoost para PF, com `random_state=42` e split temporal:

- treino: 2025-07 a 2025-08;
- validação: 2025-09 a 2025-10.

Métricas principais:

- AUC-PR: 0,9416.
- AUC-ROC: 0,9970.
- Threshold sugerido: 0,9.
- Precision: 0,9241.
- Recall: 0,7725.
- FPR: 0,0031.
- MCC: 0,8382.

Leitura correta: o resultado alto é esperado porque o label fraco deriva das regras. O modelo deve ser apresentado como baseline de priorização, não como decisão automática.

## 7. Multi-agente LLM

A T4 propôs um fluxo sequencial com cinco agentes:

1. Dados - ingesta, qualidade, coerência por rail e enriquecimento.
2. Detecção - regras + ML e fila priorizada.
3. Investigação - entidade 360°, timeline e deduplicação.
4. Reporte - SAR/ROS estruturado.
5. Compliance - revisão BACEN/COAF/FATF, sanções e trilha de auditoria.

O LLM não substitui o analista. Ele organiza evidências, padroniza narrativa, reduz esforço manual e mantém revisão humana.

## 8. Base regulatória em alto nível

A Circular BCB nº 3.978/2020 dispõe sobre política, procedimentos e controles internos de prevenção à lavagem de dinheiro e financiamento do terrorismo para instituições autorizadas pelo Banco Central. A Carta Circular BCB nº 4.001/2020 divulga operações e situações que podem configurar indícios de lavagem de dinheiro ou financiamento do terrorismo passíveis de comunicação ao COAF. A Lei nº 9.613/1998 é a base legal brasileira sobre lavagem ou ocultação de bens, direitos e valores e cria o COAF. As Recomendações FATF/GAFI formam o padrão internacional de AML/CFT.

## 9. Conclusão

O case demonstra uma cadeia completa de AML/FT: qualidade de dados, coerência por rail, regras explicáveis, ranking de suspeitos, SAR, ML explicável e arquitetura multi-agente. O principal valor está em transformar dados brutos em uma fila AML auditável, priorizada e defensável para investigação.

## Referências

- Banco Central do Brasil. Circular nº 3.978/2020: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=3978&tipo=Circular
- Banco Central do Brasil. Carta Circular nº 4.001/2020: https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50911/C_Circ_4001_v2_P.pdf
- Planalto. Lei nº 9.613/1998: https://www.planalto.gov.br/ccivil_03/leis/l9613.htm
- FATF/GAFI. FATF Recommendations: https://www.fatf-gafi.org/en/topics/fatf-recommendations.html
