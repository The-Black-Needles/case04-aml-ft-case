# SAR Draft — Cliente C101208

## 1. Identificação

- Cliente: C101208
- Nome cadastral: Customer 1209
- CPF/CNPJ: 75249447443
- Perfil KYC: risco Low, PEP=No, sanções cadastrais=No, ocupação=Chef
- Renda anual declarada: R$ 13.047,00
- Período analisado: 2025-07-03 17:46:13 a 2025-10-02 19:58:36

## 2. Resumo executivo

O cliente C101208 foi priorizado com score 444.7 e prioridade Crítica. No período, movimentou R$ 162.018,32 em 34 transações, com 9 transações cross-border e 1 eventos associados a país/contraparte de risco alto. Foi identificado hit de sanctions screening na transação TNHZDN7D6LYK6, em 2025-08-12 03:37:39, no valor de R$ 2.166,18, com receiver_country=SY e country_risk_receiver=High. A combinação de sanções, país de risco, cross-border e alertas de perfil/atividade justifica investigação formal e preparação de comunicação, sujeita à revisão humana.

## 3. Sinais e alertas

- 2025-07: 1 regras mensais, score 35, total R$ 48.733,96, regras: M01_monthly_out_of_profile_dynamic
- 2025-08: 4 regras mensais, score 187, total R$ 40.315,80, regras: M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration; M07_sanctions_any_period
- 2025-09: 2 regras mensais, score 55, total R$ 70.192,70, regras: M01_monthly_out_of_profile_dynamic; M09_high_risk_mcc_repeated

## 4. Timeline analítica

- 2025-07-03 19:35:37 | TRLSHBGRSQGA1 | PIX | R$ 2.828,01 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio
- 2025-07-22 03:28:49 | TJZRYWR88WZHJ | PIX | R$ 1.241,06 | status=Confirmed | receiver_country=PT | regras=R11_high_risk_merchant_or_cb_ratio; R13_ip_anomaly_or_proxy_tor_vpn
- 2025-08-05 20:27:45 | TGCSN3TSADMDW | PIX | R$ 3.351,21 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio
- 2025-08-09 22:07:21 | TR1K3PDMT9A1T | PIX | R$ 2.880,87 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio
- 2025-08-12 03:37:39 | TNHZDN7D6LYK6 | Wire | R$ 2.166,18 | status=Confirmed | receiver_country=SY | regras=R01_tx_sanctions_screening_hit; R04_wire_to_high_risk_country; R05_crossborder_high_risk_receiver; R06_geo_or_ip_high_risk
- 2025-08-21 18:33:38 | TVC0AUP1WJ7DN | Card | R$ 6.500,50 | status=Confirmed | receiver_country=BR | regras=R08_card_ecommerce_without_3ds; R10_high_risk_mcc
- 2025-09-03 16:25:49 | T2BJ7J1CQ8KRG | PIX | R$ 902,05 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio
- 2025-09-17 17:16:33 | TKQD7O5QATE4I | PIX | R$ 2.091,73 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio
- 2025-09-23 10:09:41 | TIQS2U9KT1J0U | Card | R$ 14.011,86 | status=Confirmed | receiver_country=BR | regras=R10_high_risk_mcc; R16_low_income_high_single_tx
- 2025-09-23 23:17:39 | TF9EJQVFQTQJM | PIX | R$ 7.718,63 | status=Confirmed | receiver_country=RU | regras=R10_high_risk_mcc; R11_high_risk_merchant_or_cb_ratio

## 5. Base legal e normativa — alto nível

- Lei nº 9.613/1998: prevenção e repressão à lavagem ou ocultação de bens, direitos e valores.
- Circular BCB nº 3.978/2020: política, procedimentos e controles internos de PLD/FT para instituições autorizadas pelo BCB.
- Carta Circular BCB nº 4.001/2020: relação de operações e situações que podem configurar indícios de LD/FT passíveis de comunicação ao COAF.
- Recomendações do FATF/GAFI: abordagem baseada em risco, diligência de clientes e comunicação de operações suspeitas.

## 6. Conclusão e ações recomendadas

Recomenda-se abertura de investigação formal, validação em listas oficiais, revisão de KYC/beneficiário final, análise de contrapartes e merchants associados, aplicação de fricção operacional quando permitido e preparação de comunicação de operação suspeita ao COAF caso a revisão humana confirme os indícios.
