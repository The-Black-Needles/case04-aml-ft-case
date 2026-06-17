# Addendum de apresentação — Geo-salto

## Onde encaixar

Usar este bloco durante a T2, logo depois de apresentar o catálogo de regras.

## Fala curta

“Eu também adicionei uma regra literal de geo-salto, porque o desafio cita essa tipologia diretamente. A lógica é comparar transações consecutivas do mesmo cliente, calcular a distância entre as coordenadas e verificar se o deslocamento seria possível no intervalo observado. O ponto importante é que eu não trato geo-salto isolado como prova de fraude. Em produção, essa regra precisa ser combinada com IP anomaly, device, país de risco, cross-border e histórico do cliente para reduzir falso positivo.”

## Arquivos para mostrar

- `outputs/t2_alert_system/04_geo_jump_candidates.csv`
- `outputs/t2_alert_system/05_geo_jump_priority_top30.csv`
- `docs/09_geo_salto_enrichment.md`

## Frase de fechamento

“Esse enriquecimento melhora a cobertura do motor de alertas sem mudar a lógica central do case: sinais isolados entram como triagem, combinação de sinais vira prioridade.”
