# T2 — Sistema de Alertas AML

## O que tem nesta pasta

Esta pasta documenta o motor de alertas AML criado para o case.

A ideia desta etapa foi sair da análise exploratória e transformar os sinais encontrados em regras formais, auditáveis e explicáveis.

## Arquivos principais

### `00_T2_alert_system_summary.md`

Resumo executivo da T2.

É o primeiro arquivo que eu abriria na apresentação para explicar rapidamente a lógica do sistema de alertas.

### `01_alert_rules_catalog_t2.csv`

Catálogo completo das regras.

Cada linha representa uma regra com nome, lógica, parâmetros, severidade, pontuação, tipologia, rail aplicável, exemplo na base, justificativa, ação operacional e controle de falso positivo.

Este é o arquivo mais importante da T2.

### `02_rule_coverage_by_typology.csv`

Mostra quais tipologias AML estão cobertas pelas regras.

Serve para demonstrar que o sistema não olha apenas para um tipo de suspeita, mas cobre diferentes cenários: sanções, cross-border, PEP, alto valor, fora de perfil, velocity, conta de passagem, e-commerce sem 3DS, MCC de risco e outros.

### `03_rule_examples_t2.md`

Traz exemplos de regras com casos encontrados na base.

É útil para explicar que as regras não ficaram apenas no conceitual: elas foram aplicadas em cima dos dados do case.

## Como explicar esta etapa em 1 minuto

“Na T2 eu formalizei o motor de alertas. Primeiro eu peguei os sinais que apareceram na EDA e transformei em regras objetivas. Depois separei as regras em transacionais e comportamentais por cliente-mês. Cada regra tem lógica, parâmetro, severidade, tipologia AML, exemplo na base e ação operacional sugerida. A prioridade não vem de um alerta isolado, mas da combinação de sinais. Isso deixa a fila AML mais auditável e defensável.”

## Raciocínio principal

O ponto principal desta etapa é explicabilidade.

Em AML, não basta dizer que um cliente é suspeito. É preciso explicar:

- qual regra disparou;
- qual comportamento foi observado;
- qual parâmetro foi usado;
- por que isso importa;
- qual ação operacional deve ser tomada.

Por isso, o sistema foi estruturado como um motor de regras antes do ML.

## Por que regras antes de ML

A decisão foi começar por regras porque regras são mais fáceis de auditar, explicar e revisar.

O modelo de ML entra depois, na T3, para priorizar casos e capturar padrões combinados. Mas a base explicável do sistema vem primeiro das regras.

## Trade-offs

Algumas regras são mais sensíveis e podem gerar falso positivo, como alto valor e cross-border.

Outras são mais críticas, como sanções, país de alto risco e PEP combinado com comportamento fora de perfil.

Por isso, a análise não deve depender de uma regra isolada. O melhor caminho é combinar sinais e priorizar os casos com maior concentração de alertas independentes.

## Frase para apresentação

“O sistema de alertas foi desenhado para ser simples, auditável e operacional. Cada regra tem uma justificativa clara, um parâmetro definido e um exemplo na base. Isso permite que o time de AML entenda por que um caso entrou na fila e qual deve ser a próxima ação.”
