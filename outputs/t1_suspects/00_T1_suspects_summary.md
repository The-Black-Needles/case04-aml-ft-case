# Tarefa 1 — Suspeitos e SAR (DIA 1)

## Visão geral

- Transações avaliadas: 52,000
- Clientes-mês com pelo menos um alerta mensal: 5,832
- Transações com pelo menos uma regra disparada: 28,204
- Regras implementadas nesta etapa: 28 (16 transacionais + 12 cliente-mês)
- Candidato de SAR selecionado: C101208

## Top 10 clientes suspeitos

| customer_id   | priority   |   final_customer_score |   total_amount |   tx_count |   sanctions_tx_count | sanctions_list_hit   | pep   | risk_rating   |   cross_border_count |   high_risk_country_count |
|:--------------|:-----------|-----------------------:|---------------:|-----------:|---------------------:|:---------------------|:------|:--------------|---------------------:|--------------------------:|
| C101028       | Crítica    |                  515   |        98314   |         25 |                    0 | Yes                  | Yes   | Low           |                    5 |                         1 |
| C101208       | Crítica    |                  444.7 |       162018   |         34 |                    1 | No                   | No    | Low           |                    9 |                         1 |
| C100091       | Crítica    |                  411   |        97254.5 |         21 |                    1 | No                   | No    | Low           |                    3 |                         1 |
| C101582       | Crítica    |                  403   |       101276   |         27 |                    0 | Yes                  | No    | Low           |                    4 |                         0 |
| C101445       | Crítica    |                  399   |        83575.9 |         27 |                    0 | Yes                  | No    | Low           |                   10 |                         0 |
| C100099       | Crítica    |                  395   |        97696.2 |         23 |                    0 | Yes                  | No    | Low           |                    4 |                         1 |
| C100472       | Crítica    |                  383   |       147843   |         26 |                    0 | Yes                  | No    | Low           |                    4 |                         0 |
| C101517       | Crítica    |                  377   |       104259   |         34 |                    0 | Yes                  | No    | Medium        |                    7 |                         0 |
| C100840       | Crítica    |                  364   |        77696.8 |         23 |                    0 | Yes                  | No    | Low           |                    3 |                         0 |
| C100570       | Crítica    |                  325   |        72307.2 |         17 |                    0 | Yes                  | No    | Low           |                    2 |                         0 |

## Top 10 transações suspeitas

| transaction_id   | timestamp           | subject_customer_id   | transaction_type   |   amount_brl | receiver_country   | country_risk_receiver   | sanctions_screening_hit   |   tx_rule_score | tx_rules_triggered                                                                                                                                                                                 |
|:-----------------|:--------------------|:----------------------|:-------------------|-------------:|:-------------------|:------------------------|:--------------------------|----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TJRKHTP81JROK    | 2025-08-07 17:28:29 | C100091               | Wire               |     11672.9  | IR                 | High                    | Yes                       |             248 | R01_tx_sanctions_screening_hit; R04_wire_to_high_risk_country; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk; R11_high_risk_merchant_or_cb_ratio; R16_low_income_high_single_tx      |
| TFNO8A1FBZUMA    | 2025-07-01 08:48:15 | C101028               | Card               |      4390.02 | KP                 | High                    | No                        |             233 | R02_subject_on_sanctions_list; R03_pep_crossborder_or_high_value; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk; R08_card_ecommerce_without_3ds; R11_high_risk_merchant_or_cb_ratio  |
| TNHZDN7D6LYK6    | 2025-08-12 03:37:39 | C101208               | Wire               |      2166.18 | SY                 | High                    | Yes                       |             210 | R01_tx_sanctions_screening_hit; R04_wire_to_high_risk_country; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk                                                                         |
| THCF7RXE8PSWC    | 2025-09-12 14:03:19 | C101028               | Card               |      1135.2  | DE                 | Low                     | No                        |             185 | R02_subject_on_sanctions_list; R03_pep_crossborder_or_high_value; R09_chargeback_status; R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio                                                     |
| TMNRCJMAFGZ4V    | 2025-07-02 00:43:48 | C101028               | PIX                |      4128.85 | BR                 | Low                     | No                        |             165 | R02_subject_on_sanctions_list; R03_pep_crossborder_or_high_value; R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio                                                                            |
| TD75IGSBF7O1D    | 2025-09-30 19:55:12 | C100099               | PIX                |      1525.54 | SY                 | High                    | No                        |             160 | R02_subject_on_sanctions_list; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk                                                                                                         |
| T4EYDTWOQ1TU5    | 2025-08-31 17:51:13 | C102376               | Card               |      9097.8  | SY                 | High                    | No                        |             150 | R03_pep_crossborder_or_high_value; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk; R08_card_ecommerce_without_3ds; R11_high_risk_merchant_or_cb_ratio; R15_near_10k_structuring_proxy |
| TA2DEC7JAUV3L    | 2025-07-21 06:03:56 | C101028               | Card               |      2061.1  | US                 | Low                     | No                        |             150 | R02_subject_on_sanctions_list; R03_pep_crossborder_or_high_value; R11_high_risk_merchant_or_cb_ratio                                                                                               |
| TO4AF1HZUO0NJ    | 2025-10-04 06:50:31 | C100472               | Card               |     17092.6  | BR                 | Low                     | No                        |             148 | R02_subject_on_sanctions_list; R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio; R16_low_income_high_single_tx                                                                                |
| T0XTK7LGM8P9Y    | 2025-07-27 06:03:59 | C101028               | PIX                |     14373.9  | BR                 | Low                     | No                        |             148 | R02_subject_on_sanctions_list; R03_pep_crossborder_or_high_value; R16_low_income_high_single_tx                                                                                                    |

## Observações

- O ranking prioriza sanções, países de alto risco, self-merchant, PEP com exposição cross-border, fora de perfil e concentração de alertas.
- Valores ausentes e outliers foram preservados como informação de risco, sem remoção automática.
- O SAR é um draft analítico e deve passar por revisão humana, enriquecimento de KYC/listas e validação jurídica/compliance antes de comunicação.
