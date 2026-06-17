# EDA DIA 1 — AML Case CloudWalk

## Confirmação dos arquivos
- Fonte analisada: AML Case Cloudwalk INC (2).xlsx
- Abas: Transactions, KYC_Profiles, Merchants, GeoBehavior, Data_Dictionary

## Shape por aba
| aba             |   linhas |   colunas |   duplicatas_linha |
|:----------------|---------:|----------:|-------------------:|
| Transactions    |    52000 |        41 |                  0 |
| KYC_Profiles    |     2500 |        16 |                  0 |
| Merchants       |     1000 |        10 |                  0 |
| GeoBehavior     |     3497 |         6 |                  0 |
| Data_Dictionary |       19 |         2 |                  0 |

## Janela temporal e volume
- Transactions: 52,000 linhas e 41 colunas.
- Período: 2025-07-01 00:09:59 até 2025-10-04 23:58:57.
- IDs de transação únicos: True.
- Sem valores zerados/negativos em amount_brl: True.

## Distribuição por rail
| transaction_type   |   count |   pct |
|:-------------------|--------:|------:|
| PIX                |   31547 | 60.67 |
| Card               |   17930 | 34.48 |
| Wire               |    2523 |  4.85 |

## Estatísticas de valor por rail
| transaction_type   |   count |         sum |    mean |   median |   min |      max |     p90 |     p95 |     p99 |
|:-------------------|--------:|------------:|--------:|---------:|------:|---------:|--------:|--------:|--------:|
| Card               |   17930 | 7.9398e+07  | 4428.22 |  2691.12 | 44.86 | 140910   | 9572.11 | 13754   | 27949.4 |
| PIX                |   31547 | 1.40148e+08 | 4442.51 |  2689.04 | 26.07 | 125782   | 9782.91 | 13885.4 | 27904.7 |
| Wire               |    2523 | 1.05119e+07 | 4166.41 |  2603.1  | 75.99 |  76466.3 | 8940.97 | 12938.4 | 23427.5 |

## Qualidade e coerência
- Sem linhas duplicadas nas 5 abas.
- Sem timestamps inválidos.
- Sem quebras de integridade referencial cliente/merchant nos IDs transacionais.
- Campos n/a são majoritariamente coerentes com rail: PIX/Wire sem campos de cartão; Card sem pix_flow.
- Observação: em Card, auth_3ds e eci aparecem como n/a quando card_present = Yes, coerente como campo não aplicável ao e-commerce.

## Sinais AML iniciais
| sinal                         |   qtd |   pct_base |
|:------------------------------|------:|-----------:|
| sanctions_tx_hits             |     2 |       0    |
| sanctions_kyc_hits            |     9 |       0.36 |
| pep_customers                 |    80 |       3.2  |
| high_risk_kyc_customers       |   196 |       7.84 |
| medium_risk_kyc_customers     |   658 |      26.32 |
| high_risk_mcc_merchants       |   349 |      34.9  |
| merchant_high_risk_flag_yes   |   186 |      18.6  |
| ip_anomaly_yes                |   190 |       0.37 |
| ip_proxy_vpn_tor_yes          |     0 |       0    |
| device_rooted_yes             |  1562 |       3    |
| cross_border_yes              | 10113 |      19.45 |
| country_risk_geo_high         |   590 |       1.13 |
| country_risk_ip_high          |   268 |       0.52 |
| country_risk_sender_high      |    75 |       0.14 |
| country_risk_receiver_high    |   515 |       0.99 |
| card_no_3ds                   |  4633 |       8.91 |
| card_ecommerce_no_3ds         |  4633 |       8.91 |
| round_amounts_100             |     6 |       0.01 |
| round_amounts_1000            |     0 |       0    |
| cash_large_50k_proxy_possible |    90 |       0.17 |

## Pré-candidatos para investigação
Top 30 pré-candidatos por agregação cliente-mês salvos no CSV `05_preliminary_suspects_customer_month.csv`.
