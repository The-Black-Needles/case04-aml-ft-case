# T2 — Sistema de Alertas AML

## O que tem nesta pasta

Esta pasta documenta o motor de alertas AML criado para o case.

A ideia desta etapa foi sair da análise exploratória e transformar os sinais encontrados em regras formais, auditáveis e explicáveis.

## Arquivos principais

### `00_T2_alert_system_summary.md`

Resumo executivo da T2.

É o primeiro arquivo que eu abriria na apresentação para explicar rapidamente a lógica do sistema de alertas.

### `01_alert_rules_catalog_t2.csv`

Catálogo documental com 29 entradas: as 28 regras do motor principal e a R17 como enriquecimento suplementar de geo-salto.

Cada linha representa uma regra com nome, lógica, parâmetros, severidade, pontuação, tipologia, rail aplicável, exemplo na base, justificativa, ação operacional e controle de falso positivo. A R17 não participa do backtesting principal enquanto não estiver integrada ao pipeline de forma reproduzível.

Este é o arquivo mais importante da T2.

### `02_rule_coverage_by_typology.csv`

Mostra a cobertura documental por tipologia e inclui a R17 suplementar.

Serve para demonstrar que o sistema não olha apenas para um tipo de suspeita, mas cobre diferentes cenários: sanções, cross-border, PEP, alto valor, fora de perfil, velocity, conta de passagem, e-commerce sem 3DS, MCC de risco e outros. Para métricas reproduzíveis do motor principal, use os artefatos de backtesting abaixo.

### `03_rule_examples_t2.md`

Traz exemplos de regras com casos encontrados na base.

É útil para explicar que as regras não ficaram apenas no conceitual: elas foram aplicadas em cima dos dados do case.

### `17_backtesting_summary.md`

É a porta de entrada para o backtesting reproduzível do motor principal R01–R16 e M01–M12.

Resume carga operacional, cobertura por rail, distribuição de acionamentos, segmentação descritiva por status e evidências empíricas de sobreposição entre regras.

### `18_backtesting_manifest.json`

Contrato legível por máquina com escopo, volumes, número de regras, número de pares analisados e limitações metodológicas.

### Tabelas `06` a `16`

Materializam os resultados usados no resumo:

- hits por regra;
- regra × rail;
- presença não exclusiva de rail no cliente-mês;
- carga operacional;
- distribuição do número de regras acionadas;
- carga por status e rail;
- coocorrência e candidatos empíricos para revisão humana.

Esses artefatos não calculam falsos positivos ou falsos negativos das regras porque a base não possui ground truth investigativo independente.

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
