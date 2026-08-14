# T2 — Backtesting descritivo reproduzível

## Objetivo

Este conjunto de artefatos mede cobertura, concentração, carga operacional e sobreposição do motor principal de regras sobre a base sintética do case.

O backtesting é descritivo e experimental. Ele não constitui homologação produtiva e não usa um ground truth independente.

## Escopo

- 16 regras transacionais: R01–R16.
- 12 regras cliente-mês: M01–M12.
- 28 regras no motor principal.
- R17 permanece como enriquecimento suplementar de geo-salto e está fora deste backtesting principal.
- Base integralmente sintética.

## Carga operacional observada

- Transações alertadas: 28,204/52,000 (54,24%).
- Cliente-mês alertados: 5,832/9,107 (64,04%).
- Total de hits transacionais: 44,932.
- Total de hits cliente-mês: 9,521.

## Segmentação transacional por rail

- PIX: 16,842/31,547 (53,39%).
- Card: 10,007/17,930 (55,81%).
- Wire: 1,355/2,523 (53,71%).

Na unidade cliente-mês, a presença de rail é não exclusiva: um mesmo cliente-mês pode conter PIX, Card e Wire.

## Status transacional

A segmentação por `status` é apenas descritiva. `status` não é tratado como ground truth de fraude ou lavagem.

Em particular, Chargeback participa diretamente da lógica da R09. Por isso, a concentração de alertas nesse status é circular e não pode ser apresentada como evidência independente de precisão.

## Sobreposição e revisão humana

- Pares transacionais sinalizados para revisão: 8/120.
- Pares cliente-mês sinalizados para revisão: 8/66.
- R10/R11: Jaccard empírico 0.437979, com 8,979 acionamentos conjuntos.
- Containment observado na base é evidência empírica para revisão, não prova de equivalência lógica entre regras.

Nenhuma regra é desativada automaticamente. Redundância, conflito, ajuste de threshold e ação operacional exigem análise humana.

## O que este backtesting não mede

- Não calcula precision, recall, FPR, FNR, falsos positivos ou falsos negativos das regras, porque não existe label investigativo independente.
- Não transforma sanções, chargeback ou qualquer outro campo usado pela própria regra em validação externa.
- Não representa homologação em ambiente produtivo.
- Não afirma ocorrência de crime.

## Uso pretendido

Os artefatos servem para tornar o motor auditável, comparar carga por rail, localizar concentração de alertas, identificar pares de regras que merecem revisão e apoiar uma futura calibragem com feedback investigativo e capacidade operacional.

A decisão final permanece supervisionada por humanos.
