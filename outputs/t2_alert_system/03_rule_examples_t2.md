# Exemplos de regras acionadas na base — T2

Abaixo estão exemplos reais da base para explicar o funcionamento das regras. A ideia é mostrar que cada alerta tem rastreabilidade: regra, parâmetro e evidência.

## R01 — Hit de sanções na transação

- **Nível:** transacao
- **Tipologia:** sanções / FT / cross-border
- **Lógica:** sanctions_screening_hit = Yes na transação.
- **Parâmetros:** sanctions_screening_hit=Yes.
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Sanções têm baixa tolerância a falso negativo e exigem revisão imediata, bloqueio/segregação conforme política interna e validação em listas oficiais.

## R02 — Cliente em lista de sanções no KYC

- **Nível:** transacao
- **Tipologia:** sanções / KYC
- **Lógica:** Cliente sujeito da transação possui sanctions_list_hit = Yes no KYC.
- **Parâmetros:** kyc.sanctions_list_hit=Yes.
- **Exemplo:** TFNO8A1FBZUMA | cliente C101028 | Card | R$ 4.390,02 | receiver_country=KP | country_risk_receiver=High | cross_border=Yes | capture_method=E-commerce | auth_3ds=No | card_present=No | merchant_mcc_risk=Normal
- **Por que importa:** Um hit cadastral altera a análise de todo comportamento transacional do cliente e deve prevalecer sobre limiares de valor.

## R03 — PEP com cross-border ou alto valor

- **Nível:** transacao
- **Tipologia:** PEP / corrupção / layering
- **Lógica:** Cliente PEP com cross_border=Yes, amount_brl >= 10.000 ou receiver de país High.
- **Parâmetros:** pep=Yes + (cross_border=Yes OR amount>=10000 OR country_risk_receiver=High).
- **Exemplo:** TFNO8A1FBZUMA | cliente C101028 | Card | R$ 4.390,02 | receiver_country=KP | country_risk_receiver=High | cross_border=Yes | capture_method=E-commerce | auth_3ds=No | card_present=No | merchant_mcc_risk=Normal
- **Por que importa:** PEP não é suspeito por si só, mas PEP combinado com alto valor, país de risco ou cross-border aumenta a necessidade de diligência reforçada.

## R04 — Wire para país de alto risco

- **Nível:** transacao
- **Tipologia:** cross-border / país de risco / FT
- **Lógica:** transaction_type = Wire e country_risk_receiver = High.
- **Parâmetros:** rail=Wire; country_risk_receiver=High.
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Wire internacional para país de alto risco é red flag clássica de layering, evasão e FT, especialmente quando combinado com sanções.

## R05 — Cross-border com receiver em país de alto risco

- **Nível:** transacao
- **Tipologia:** cross-border / país de risco
- **Lógica:** cross_border=Yes e country_risk_receiver=High.
- **Parâmetros:** cross_border=Yes; country_risk_receiver=High.
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** A combinação de internacionalização com jurisdição de alto risco aumenta risco de layering e evasão de controles.

## R06 — Geografia/IP de alto risco

- **Nível:** transacao
- **Tipologia:** geo-salto / geografia de risco
- **Lógica:** country_risk_geo=High ou country_risk_ip=High ou country_risk_sender=High.
- **Parâmetros:** Qualquer dimensão geográfica classificada como High.
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Risco geográfico isolado gera ruído, mas em combinação com cross-border, sanções ou alto valor melhora a priorização.

## R07 — Transação de alto valor >= R$50 mil

- **Nível:** transacao
- **Tipologia:** alto valor / possível comunicação objetiva se espécie
- **Lógica:** amount_brl >= 50.000.
- **Parâmetros:** amount_brl>=50000.
- **Exemplo:** T7ILZTP10SBFN | cliente C100208 | Card | R$ 51.589,26 | receiver_country=MM | country_risk_receiver=High | cross_border=Yes | capture_method=Magstripe | auth_3ds=n/a | card_present=Yes | merchant_mcc_risk=Normal
- **Por que importa:** Valor alto aumenta materialidade AML, mas nesta base não há campo de espécie; por isso é tratado como alerta de alto valor, não comunicação automática.

## R08 — Card e-commerce sem 3DS

- **Nível:** transacao
- **Tipologia:** fraude cartão / e-commerce sem autenticação forte
- **Lógica:** Card + E-commerce + card_present=No + auth_3ds=No.
- **Parâmetros:** transaction_type=Card; capture_method=E-commerce; card_present=No; auth_3ds=No.
- **Exemplo:** TFNO8A1FBZUMA | cliente C101028 | Card | R$ 4.390,02 | receiver_country=KP | country_risk_receiver=High | cross_border=Yes | capture_method=E-commerce | auth_3ds=No | card_present=No | merchant_mcc_risk=Normal
- **Por que importa:** Ausência de 3DS em e-commerce aumenta risco de fraude e pode compor alerta AML quando há MCC/merchant de risco e volume incompatível.

## R09 — Transação com chargeback

- **Nível:** transacao
- **Tipologia:** fraude cartão / merchant risk
- **Lógica:** status = Chargeback.
- **Parâmetros:** status=Chargeback.
- **Exemplo:** THCF7RXE8PSWC | cliente C101028 | Card | R$ 1.135,20 | receiver_country=DE | country_risk_receiver=Low | cross_border=Yes | capture_method=E-commerce | auth_3ds=Yes | card_present=No | merchant_mcc_risk=High
- **Por que importa:** Chargeback pode indicar fraude, teste de cartão, merchant abusivo ou disputa; isolado é operacional, combinado com MCC/alto risco vira AML/fraude.

## R10 — MCC de alto risco

- **Nível:** transacao
- **Tipologia:** MCC risco / merchant risk
- **Lógica:** merchant_mcc_risk = High.
- **Parâmetros:** merchant.mcc_risk=High.
- **Exemplo:** THCF7RXE8PSWC | cliente C101028 | Card | R$ 1.135,20 | receiver_country=DE | country_risk_receiver=Low | cross_border=Yes | capture_method=E-commerce | auth_3ds=Yes | card_present=No | merchant_mcc_risk=High
- **Por que importa:** MCC de risco não é suspeito sozinho, mas ajuda a priorizar quando combinado com alto volume, e-commerce sem 3DS ou chargeback.

## R11 — Merchant high risk ou chargeback ratio elevado

- **Nível:** transacao
- **Tipologia:** merchant risk / fraude adquirência
- **Lógica:** merchant_high_risk_flag=Yes ou merchant_chargeback_ratio_90d >= 8%.
- **Parâmetros:** merchant_high_risk_flag=Yes OR chargeback_ratio_90d>=0.08.
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Merchant com risco elevado ou alto chargeback ratio pode ser vetor de fraude, collusion, self-merchant ou laundering via vendas simuladas.

## R12 — Self-merchant

- **Nível:** transacao
- **Tipologia:** self-merchant / vendas simuladas / circularidade
- **Lógica:** subject_customer_id = owner_customer_id do merchant.
- **Parâmetros:** subject_customer_id == merchant.owner_customer_id.
- **Exemplo:** T89LY8D0GYY1H | cliente C102253 | PIX | R$ 13.698,06 | receiver_country=BR | country_risk_receiver=Low | cross_border=No | capture_method=Pix Key | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=High
- **Por que importa:** Cliente transacionando com merchant próprio pode indicar circularidade, simulação de vendas, auto-liquidação ou abuso de arranjo.

## R13 — IP anomaly, proxy, VPN ou Tor

- **Nível:** transacao
- **Tipologia:** device/IP risk / geo-salto
- **Lógica:** ip_anomaly=Yes ou ip_proxy_vpn_tor em Proxy/VPN/Tor.
- **Parâmetros:** ip_anomaly=Yes OR ip_proxy_vpn_tor in [Proxy, VPN, Tor].
- **Exemplo:** TQXICCVPO421G | cliente C101028 | Card | R$ 6.975,17 | receiver_country=BR | country_risk_receiver=Low | cross_border=No | capture_method=E-commerce | auth_3ds=Yes | card_present=No | merchant_mcc_risk=High
- **Por que importa:** Sinal técnico isolado pode ser ruído, mas combinado com alto valor, cross-border ou conta nova reforça risco de fraude/AML.

## R14 — Device rooted

- **Nível:** transacao
- **Tipologia:** device risk / fraude digital
- **Lógica:** device_rooted = Yes.
- **Parâmetros:** device_rooted=Yes.
- **Exemplo:** T3VP1HWRBF614 | cliente C101973 | Wire | R$ 2.149,85 | receiver_country=MM | country_risk_receiver=High | cross_border=Yes | capture_method=SWIFT | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Device rooted aumenta risco de comprometimento, automação ou manipulação de sessão, especialmente com transação financeira de risco.

## R15 — Valor próximo de R$10 mil

- **Nível:** transacao
- **Tipologia:** structuring / smurfing proxy
- **Lógica:** amount_brl entre R$9.000 e R$9.999,99.
- **Parâmetros:** 9000 <= amount_brl < 10000.
- **Exemplo:** T4EYDTWOQ1TU5 | cliente C102376 | Card | R$ 9.097,80 | receiver_country=SY | country_risk_receiver=High | cross_border=Yes | capture_method=E-commerce | auth_3ds=No | card_present=No | merchant_mcc_risk=Normal
- **Por que importa:** Valores próximos a limites são proxies de fracionamento; o sinal fica mais forte com repetição e múltiplas contrapartes.

## R16 — Transação alta versus renda mensal estimada

- **Nível:** transacao
- **Tipologia:** fora de perfil / renda incompatível
- **Lógica:** amount_brl >= max(2x renda mensal estimada, R$10.000).
- **Parâmetros:** monthly_income=annual_income/12; amount >= max(monthly_income*2,10000).
- **Exemplo:** TJRKHTP81JROK | cliente C100091 | Wire | R$ 11.672,88 | receiver_country=IR | country_risk_receiver=High | cross_border=Yes | capture_method=Domestic | auth_3ds=n/a | card_present=n/a | merchant_mcc_risk=Normal
- **Por que importa:** Transação incompatível com renda declarada é red flag clássica, mas precisa ser calibrada por segmento e histórico.

## M01 — Movimentação mensal fora de perfil

- **Nível:** cliente_mes
- **Tipologia:** fora de perfil / renda incompatível
- **Lógica:** Total mensal >= limiar dinâmico por risco/renda.
- **Parâmetros:** Risco Low: >=2x renda mensal; Medium: >=1,5x; High: >=1x; piso PF R$20.000 usado no protótipo.
- **Exemplo:** cliente C101028 / mês 2025-07 | total=R$ 62.577,35 | tx_count=14 | cash_in=3 (R$ 9.910,53) | cash_out=11 (R$ 52.666,82) | cross_border=3 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M07_sanctions_any_period; M08_pep_high_volume; M09_high_risk_mcc_repeated
- **Por que importa:** Avalia comportamento acumulado e reduz falso positivo de uma transação isolada; muito útil para priorização AML.

## M02 — Velocity de alto volume mensal

- **Nível:** cliente_mes
- **Tipologia:** velocity / conta de passagem
- **Lógica:** tx_count >= 15 e total_amount >= R$50.000 no mês.
- **Parâmetros:** tx_count>=15; total_amount>=50000.
- **Exemplo:** cliente C100057 / mês 2025-07 | total=R$ 69.504,60 | tx_count=18 | cash_in=2 (R$ 3.726,80) | cash_out=16 (R$ 65.777,80) | cross_border=7 | high_risk_country=2 | regras=M01_monthly_out_of_profile_dynamic; M02_velocity_high_volume; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration; M06_high_risk_country_repeated; M09_high_risk_mcc_repeated
- **Por que importa:** Volume + frequência aumentam risco de conta operacionalizada por terceiros, laundering ou fraude em escala.

## M03 — Structuring por repetição perto de R$10 mil

- **Nível:** cliente_mes
- **Tipologia:** structuring / smurfing
- **Lógica:** near_10k_count >= 3 no mês.
- **Parâmetros:** Mínimo 3 transações entre R$9.000 e R$9.999,99 no mês.
- **Exemplo:** cliente C100119 / mês 2025-08 | total=R$ 43.028,80 | tx_count=8 | cash_in=2 (R$ 13.677,38) | cash_out=6 (R$ 29.351,42) | cross_border=3 | high_risk_country=0 | regras=M01_monthly_out_of_profile_dynamic; M03_structuring_near_10k_repeated; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration
- **Por que importa:** Repetição perto de limite é mais forte que evento isolado e pode indicar tentativa de fracionamento.

## M04 — Cash-in para cash-out / conta de passagem

- **Nível:** cliente_mes
- **Tipologia:** conta de passagem / mule account / layering
- **Lógica:** cash_in_count>=2, cash_out_count>=5, cash_out_amount>=70% cash_in_amount e total>=R$20.000.
- **Parâmetros:** cash_in_count>=2; cash_out_count>=5; cash_out_amount/cash_in_amount>=0.70; total>=20000.
- **Exemplo:** cliente C101028 / mês 2025-07 | total=R$ 62.577,35 | tx_count=14 | cash_in=3 (R$ 9.910,53) | cash_out=11 (R$ 52.666,82) | cross_border=3 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M07_sanctions_any_period; M08_pep_high_volume; M09_high_risk_mcc_repeated
- **Por que importa:** Entrada seguida de saída, com pouca retenção, é padrão compatível com conta de passagem ou mule account.

## M05 — Concentração cross-border

- **Nível:** cliente_mes
- **Tipologia:** cross-border / layering
- **Lógica:** cross_border_count>=3 e cross_border_count/tx_count >= 30% no mês.
- **Parâmetros:** cross_border_count>=3; proporção>=0.30.
- **Exemplo:** cliente C101208 / mês 2025-08 | total=R$ 40.315,80 | tx_count=12 | cash_in=2 (R$ 6.672,41) | cash_out=10 (R$ 33.643,39) | cross_border=5 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration; M07_sanctions_any_period
- **Por que importa:** Alta concentração internacional fora do padrão pode indicar layering, evasão ou uso de jurisdição de risco.

## M06 — Repetição com país de alto risco

- **Nível:** cliente_mes
- **Tipologia:** país de risco / FT / sanctions proximity
- **Lógica:** high_risk_country_count >= 2 no mês.
- **Parâmetros:** Mínimo 2 eventos com receiver_country High no mês.
- **Exemplo:** cliente C100057 / mês 2025-07 | total=R$ 69.504,60 | tx_count=18 | cash_in=2 (R$ 3.726,80) | cash_out=16 (R$ 65.777,80) | cross_border=7 | high_risk_country=2 | regras=M01_monthly_out_of_profile_dynamic; M02_velocity_high_volume; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration; M06_high_risk_country_repeated; M09_high_risk_mcc_repeated
- **Por que importa:** Repetição com jurisdição de alto risco aumenta materialidade e reduz chance de evento acidental.

## M07 — Sanções no período

- **Nível:** cliente_mes
- **Tipologia:** sanções / FT
- **Lógica:** sanctions_tx_count>=1 ou sanctions_list_hit=Yes.
- **Parâmetros:** Qualquer hit transacional ou cadastral no mês.
- **Exemplo:** cliente C101028 / mês 2025-07 | total=R$ 62.577,35 | tx_count=14 | cash_in=3 (R$ 9.910,53) | cash_out=11 (R$ 52.666,82) | cross_border=3 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M07_sanctions_any_period; M08_pep_high_volume; M09_high_risk_mcc_repeated
- **Por que importa:** Sanções exigem tratamento de alta prioridade independentemente de valor.

## M08 — PEP com alto volume mensal

- **Nível:** cliente_mes
- **Tipologia:** PEP / corrupção / EDD
- **Lógica:** pep=Yes e total_amount>=R$50.000 no mês.
- **Parâmetros:** PEP=Yes; total mensal>=50000.
- **Exemplo:** cliente C101028 / mês 2025-07 | total=R$ 62.577,35 | tx_count=14 | cash_in=3 (R$ 9.910,53) | cash_out=11 (R$ 52.666,82) | cross_border=3 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M07_sanctions_any_period; M08_pep_high_volume; M09_high_risk_mcc_repeated
- **Por que importa:** PEP exige diligência reforçada quando combinado com materialidade financeira.

## M09 — Repetição em MCC de risco

- **Nível:** cliente_mes
- **Tipologia:** MCC risco / merchant risk
- **Lógica:** high_risk_mcc_count>=5 no mês.
- **Parâmetros:** Mínimo 5 transações com MCC High no mês.
- **Exemplo:** cliente C101028 / mês 2025-07 | total=R$ 62.577,35 | tx_count=14 | cash_in=3 (R$ 9.910,53) | cash_out=11 (R$ 52.666,82) | cross_border=3 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M07_sanctions_any_period; M08_pep_high_volume; M09_high_risk_mcc_repeated
- **Por que importa:** Repetição em MCC de risco é mais relevante que uma compra isolada; pode indicar uso de merchants para layering/fraude.

## M10 — E-commerce sem 3DS repetido

- **Nível:** cliente_mes
- **Tipologia:** fraude cartão / e-commerce sem autenticação
- **Lógica:** ecommerce_no3ds_count>=2 no mês.
- **Parâmetros:** Mínimo 2 transações Card E-commerce CNP sem 3DS no mês.
- **Exemplo:** cliente C101770 / mês 2025-08 | total=R$ 57.477,85 | tx_count=16 | cash_in=4 (R$ 29.480,51) | cash_out=12 (R$ 27.997,34) | cross_border=4 | high_risk_country=1 | regras=M01_monthly_out_of_profile_dynamic; M02_velocity_high_volume; M04_cashin_to_cashout_pass_through_proxy; M10_ecommerce_no3ds_repeated; M11_device_ip_risk_repeated
- **Por que importa:** Repetição de e-commerce sem 3DS aumenta risco de fraude e pode compor priorização junto a MCC/merchant de risco.

## M11 — Risco técnico repetido de device/IP

- **Nível:** cliente_mes
- **Tipologia:** device/IP ring / geo-salto
- **Lógica:** ip_anomaly_proxy_count>=3 no mês.
- **Parâmetros:** Mínimo 3 eventos de IP anomaly, Proxy, VPN ou Tor no mês.
- **Exemplo:** cliente C100251 / mês 2025-09 | total=R$ 38.095,20 | tx_count=11 | cash_in=2 (R$ 2.460,73) | cash_out=9 (R$ 35.634,47) | cross_border=4 | high_risk_country=2 | regras=M01_monthly_out_of_profile_dynamic; M04_cashin_to_cashout_pass_through_proxy; M05_crossborder_concentration; M06_high_risk_country_repeated; M11_device_ip_risk_repeated
- **Por que importa:** Repetição de sinal técnico é mais relevante que evento isolado e pode indicar automação, ocultação de origem ou takeover.

## M12 — Self-merchant no mês

- **Nível:** cliente_mes
- **Tipologia:** self-merchant / circularidade
- **Lógica:** self_merchant_count>=1 no mês.
- **Parâmetros:** Qualquer transação em que cliente coincide com owner_customer_id do merchant.
- **Exemplo:** cliente C100300 / mês 2025-07 | total=R$ 86.567,52 | tx_count=16 | cash_in=1 (R$ 2.000,19) | cash_out=15 (R$ 84.567,33) | cross_border=1 | high_risk_country=0 | regras=M01_monthly_out_of_profile_dynamic; M02_velocity_high_volume; M09_high_risk_mcc_repeated; M12_self_merchant_any
- **Por que importa:** Indício forte de possível circularidade ou venda simulada, especialmente quando combinado com alto valor ou chargeback.



## R17 — Geo-salto físico improvável

**Lógica:** transações consecutivas do mesmo cliente com distância geográfica >= 500 km em intervalo <= 12h.

**Parâmetros:** distância >= 500 km; intervalo <= 12h; priorização quando houver país de risco, IP anomaly, proxy/VPN/Tor, device rooted, cross-border ou distância extrema.

**Exemplo na base:** `T8DGGXAWXFEVX -> THL18899DG0S9` para o cliente `C100392`. Intervalo de 1.177h, distância de 19172.7 km e velocidade implícita de 16290.2 km/h. Flags contextuais: `proxy_vpn_tor;cross_border;geo_country_change`.

**Justificativa:** geo-saltos fisicamente improváveis podem indicar uso indevido de credenciais, device/IP mascarado, atuação de terceiros ou conta operada por múltiplas localidades. Na base sintética, a regra deve ser usada como alerta contextual, não como bloqueio automático isolado.
