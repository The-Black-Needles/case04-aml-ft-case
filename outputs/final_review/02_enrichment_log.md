# Log de enriquecimento pós-delivery-ready

## Prioridade 2 — Geo-salto literal

Enriquecimento adicionado para cobrir explicitamente a tipologia de geo-salto citada no desafio.

Arquivos adicionados/atualizados:

- `outputs/t2_alert_system/04_geo_jump_candidates.csv`
- `outputs/t2_alert_system/04b_geo_jump_summary.json`
- `outputs/t2_alert_system/05_geo_jump_priority_top30.csv`
- `outputs/t2_alert_system/README_geo_salto.md`
- `docs/09_geo_salto_enrichment.md`
- `presentation/roteiro_geo_salto_addendum.md`
- `src/alerts.py`
- `outputs/t2_alert_system/01_alert_rules_catalog_t2.csv`
- `outputs/t2_alert_system/02_rule_coverage_by_typology.csv`
- `outputs/t2_alert_system/03_rule_examples_t2.md`

Racional:

A regra de geo-salto adiciona distância/tempo de forma explícita, mas é tratada de maneira conservadora por risco de falso positivo em dados geográficos sintéticos ou ruidosos.
