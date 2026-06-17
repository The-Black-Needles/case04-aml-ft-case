# README — Geo-salto literal

Esta pasta agora inclui uma regra complementar de geo-salto literal.

## Arquivos

- `04_geo_jump_candidates.csv`: até 500 candidatos literais de geo-salto.
- `04b_geo_jump_summary.json`: resumo quantitativo da regra.
- `05_geo_jump_priority_top30.csv`: top 30 candidatos priorizados.

## Critério

Transações consecutivas do mesmo cliente com distância >= 500 km e intervalo <= 12h.

## Interpretação

Na base, foram encontrados 4247 candidatos literais e 1942 candidatos priorizados.

Como a geolocalização pode ter ruído, especialmente em base sintética, a regra deve ser usada como sinal contextual. O valor operacional está em combinar geo-salto com outros sinais, como país de risco, IP anomaly, device rooted, cross-border ou fora de perfil.
