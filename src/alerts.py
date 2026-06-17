from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AlertLevel = Literal["transaction", "customer_month"]


@dataclass(frozen=True)
class AlertRule:
    """Metadata de uma regra de alerta AML/FT.

    A implementação operacional das regras está em src/rules.py.
    Este arquivo concentra metadados para documentação, auditoria e apresentação.
    """

    rule_id: str
    name: str
    level: AlertLevel
    severity: str
    points: int
    typology: str
    logic: str
    parameters: str
    dynamic_threshold: bool


ALERT_RULES: list[AlertRule] = [
    AlertRule(rule_id='R01', name='Hit de sanções na transação', level='transaction', severity='Crítica', points=100, typology='sanções / FT / cross-border', logic='sanctions_screening_hit = Yes na transação.', parameters='sanctions_screening_hit=Yes.', dynamic_threshold=False),
    AlertRule(rule_id='R02', name='Cliente em lista de sanções no KYC', level='transaction', severity='Crítica', points=95, typology='sanções / KYC', logic='Cliente sujeito da transação possui sanctions_list_hit = Yes no KYC.', parameters='kyc.sanctions_list_hit=Yes.', dynamic_threshold=False),
    AlertRule(rule_id='R03', name='PEP com cross-border ou alto valor', level='transaction', severity='Alta', points=35, typology='PEP / corrupção / layering', logic='Cliente PEP com cross_border=Yes, amount_brl >= 10.000 ou receiver de país High.', parameters='pep=Yes + (cross_border=Yes OR amount>=10000 OR country_risk_receiver=High).', dynamic_threshold=False),
    AlertRule(rule_id='R04', name='Wire para país de alto risco', level='transaction', severity='Alta', points=45, typology='cross-border / país de risco / FT', logic='transaction_type = Wire e country_risk_receiver = High.', parameters='rail=Wire; country_risk_receiver=High.', dynamic_threshold=False),
    AlertRule(rule_id='R05', name='Cross-border com receiver em país de alto risco', level='transaction', severity='Alta', points=45, typology='cross-border / país de risco', logic='cross_border=Yes e country_risk_receiver=High.', parameters='cross_border=Yes; country_risk_receiver=High.', dynamic_threshold=False),
    AlertRule(rule_id='R06', name='Geografia/IP de alto risco', level='transaction', severity='Média', points=20, typology='geo-salto / geografia de risco', logic='country_risk_geo=High ou country_risk_ip=High ou country_risk_sender=High.', parameters='Qualquer dimensão geográfica classificada como High.', dynamic_threshold=False),
    AlertRule(rule_id='R07', name='Transação de alto valor >= R$50 mil', level='transaction', severity='Alta', points=30, typology='alto valor / possível comunicação objetiva se espécie', logic='amount_brl >= 50.000.', parameters='amount_brl>=50000.', dynamic_threshold=False),
    AlertRule(rule_id='R08', name='Card e-commerce sem 3DS', level='transaction', severity='Média', points=18, typology='fraude cartão / e-commerce sem autenticação forte', logic='Card + E-commerce + card_present=No + auth_3ds=No.', parameters='transaction_type=Card; capture_method=E-commerce; card_present=No; auth_3ds=No.', dynamic_threshold=False),
    AlertRule(rule_id='R09', name='Transação com chargeback', level='transaction', severity='Média', points=20, typology='fraude cartão / merchant risk', logic='status = Chargeback.', parameters='status=Chargeback.', dynamic_threshold=False),
    AlertRule(rule_id='R10', name='MCC de alto risco', level='transaction', severity='Média', points=15, typology='MCC risco / merchant risk', logic='merchant_mcc_risk = High.', parameters='merchant.mcc_risk=High.', dynamic_threshold=False),
    AlertRule(rule_id='R11', name='Merchant high risk ou chargeback ratio elevado', level='transaction', severity='Média-Alta', points=20, typology='merchant risk / fraude adquirência', logic='merchant_high_risk_flag=Yes ou merchant_chargeback_ratio_90d >= 8%.', parameters='merchant_high_risk_flag=Yes OR chargeback_ratio_90d>=0.08.', dynamic_threshold=True),
    AlertRule(rule_id='R12', name='Self-merchant', level='transaction', severity='Crítica', points=80, typology='self-merchant / vendas simuladas / circularidade', logic='subject_customer_id = owner_customer_id do merchant.', parameters='subject_customer_id == merchant.owner_customer_id.', dynamic_threshold=False),
    AlertRule(rule_id='R13', name='IP anomaly, proxy, VPN ou Tor', level='transaction', severity='Média', points=12, typology='device/IP risk / geo-salto', logic='ip_anomaly=Yes ou ip_proxy_vpn_tor em Proxy/VPN/Tor.', parameters='ip_anomaly=Yes OR ip_proxy_vpn_tor in [Proxy, VPN, Tor].', dynamic_threshold=False),
    AlertRule(rule_id='R14', name='Device rooted', level='transaction', severity='Média', points=10, typology='device risk / fraude digital', logic='device_rooted = Yes.', parameters='device_rooted=Yes.', dynamic_threshold=False),
    AlertRule(rule_id='R15', name='Valor próximo de R$10 mil', level='transaction', severity='Média', points=12, typology='structuring / smurfing proxy', logic='amount_brl entre R$9.000 e R$9.999,99.', parameters='9000 <= amount_brl < 10000.', dynamic_threshold=True),
    AlertRule(rule_id='R16', name='Transação alta versus renda mensal estimada', level='transaction', severity='Média-Alta', points=18, typology='fora de perfil / renda incompatível', logic='amount_brl >= max(2x renda mensal estimada, R$10.000).', parameters='monthly_income=annual_income/12; amount >= max(monthly_income*2,10000).', dynamic_threshold=True),
    AlertRule(rule_id='M01', name='Movimentação mensal fora de perfil', level='customer_month', severity='Alta', points=35, typology='fora de perfil / renda incompatível', logic='Total mensal >= limiar dinâmico por risco/renda.', parameters='Risco Low: >=2x renda mensal; Medium: >=1,5x; High: >=1x; piso PF R$20.000 usado no protótipo.', dynamic_threshold=True),
    AlertRule(rule_id='M02', name='Velocity de alto volume mensal', level='customer_month', severity='Alta', points=25, typology='velocity / conta de passagem', logic='tx_count >= 15 e total_amount >= R$50.000 no mês.', parameters='tx_count>=15; total_amount>=50000.', dynamic_threshold=True),
    AlertRule(rule_id='M03', name='Structuring por repetição perto de R$10 mil', level='customer_month', severity='Alta', points=30, typology='structuring / smurfing', logic='near_10k_count >= 3 no mês.', parameters='Mínimo 3 transações entre R$9.000 e R$9.999,99 no mês.', dynamic_threshold=True),
    AlertRule(rule_id='M04', name='Cash-in para cash-out / conta de passagem', level='customer_month', severity='Alta', points=30, typology='conta de passagem / mule account / layering', logic='cash_in_count>=2, cash_out_count>=5, cash_out_amount>=70% cash_in_amount e total>=R$20.000.', parameters='cash_in_count>=2; cash_out_count>=5; cash_out_amount/cash_in_amount>=0.70; total>=20000.', dynamic_threshold=True),
    AlertRule(rule_id='M05', name='Concentração cross-border', level='customer_month', severity='Média-Alta', points=22, typology='cross-border / layering', logic='cross_border_count>=3 e cross_border_count/tx_count >= 30% no mês.', parameters='cross_border_count>=3; proporção>=0.30.', dynamic_threshold=True),
    AlertRule(rule_id='M06', name='Repetição com país de alto risco', level='customer_month', severity='Alta', points=35, typology='país de risco / FT / sanctions proximity', logic='high_risk_country_count >= 2 no mês.', parameters='Mínimo 2 eventos com receiver_country High no mês.', dynamic_threshold=True),
    AlertRule(rule_id='M07', name='Sanções no período', level='customer_month', severity='Crítica', points=100, typology='sanções / FT', logic='sanctions_tx_count>=1 ou sanctions_list_hit=Yes.', parameters='Qualquer hit transacional ou cadastral no mês.', dynamic_threshold=False),
    AlertRule(rule_id='M08', name='PEP com alto volume mensal', level='customer_month', severity='Alta', points=35, typology='PEP / corrupção / EDD', logic='pep=Yes e total_amount>=R$50.000 no mês.', parameters='PEP=Yes; total mensal>=50000.', dynamic_threshold=True),
    AlertRule(rule_id='M09', name='Repetição em MCC de risco', level='customer_month', severity='Média', points=20, typology='MCC risco / merchant risk', logic='high_risk_mcc_count>=5 no mês.', parameters='Mínimo 5 transações com MCC High no mês.', dynamic_threshold=True),
    AlertRule(rule_id='M10', name='E-commerce sem 3DS repetido', level='customer_month', severity='Média', points=18, typology='fraude cartão / e-commerce sem autenticação', logic='ecommerce_no3ds_count>=2 no mês.', parameters='Mínimo 2 transações Card E-commerce CNP sem 3DS no mês.', dynamic_threshold=True),
    AlertRule(rule_id='M11', name='Risco técnico repetido de device/IP', level='customer_month', severity='Média', points=18, typology='device/IP ring / geo-salto', logic='ip_anomaly_proxy_count>=3 no mês.', parameters='Mínimo 3 eventos de IP anomaly, Proxy, VPN ou Tor no mês.', dynamic_threshold=True),
    AlertRule(rule_id='M12', name='Self-merchant no mês', level='customer_month', severity='Crítica', points=80, typology='self-merchant / circularidade', logic='self_merchant_count>=1 no mês.', parameters='Qualquer transação em que cliente coincide com owner_customer_id do merchant.', dynamic_threshold=False),
]
