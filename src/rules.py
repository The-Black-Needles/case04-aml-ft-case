from __future__ import annotations
import os, zipfile, xml.etree.ElementTree as ET, re, json, shutil, time
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
XLSX = PROJECT_ROOT / "data" / "raw" / "AML_FT_Case_Synthetic_Data.xlsx"
OUT_ROOT = PROJECT_ROOT / "outputs" / "t1_suspects"
TMP_ROOT = PROJECT_ROOT / "outputs" / "tmp"
PKG_ROOT = TMP_ROOT / "aml_ft_case_t1_package"
PACKAGE_ARCHIVE = TMP_ROOT / "aml_ft_case_t1_package"
NS_MAIN='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
COL_RE=re.compile(r'([A-Z]+)([0-9]+)')

def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def col_to_idx(col: str) -> int:
    n=0
    for ch in col: n=n*26+ord(ch)-64
    return n-1

def load_shared(z: zipfile.ZipFile) -> List[str]:
    sst=[]
    with z.open('xl/sharedStrings.xml') as fh:
        for event, elem in ET.iterparse(fh, events=('end',)):
            if elem.tag.endswith('}si'):
                texts=[t_el.text for t_el in elem.iter() if t_el.tag.endswith('}t') and t_el.text is not None]
                sst.append(''.join(texts)); elem.clear()
    return sst

def sheet_to_df(z: zipfile.ZipFile, sheet_path: str, sst: List[str]) -> pd.DataFrame:
    rows=[]
    with z.open(sheet_path) as fh:
        for event, row in ET.iterparse(fh, events=('end',)):
            if row.tag.endswith('}row'):
                vals=[]
                for c in row:
                    if not c.tag.endswith('}c'): continue
                    m=COL_RE.match(c.attrib.get('r',''))
                    if m:
                        idx=col_to_idx(m.group(1))
                        while len(vals)<=idx: vals.append(None)
                    else: idx=len(vals)
                    typ=c.attrib.get('t'); v=None
                    if typ=='s':
                        ve=c.find('{%s}v'%NS_MAIN)
                        v=sst[int(ve.text)] if ve is not None and ve.text is not None else None
                    elif typ=='inlineStr':
                        is_el=c.find('{%s}is'%NS_MAIN)
                        v=''.join([t_el.text for t_el in is_el.iter() if t_el.tag.endswith('}t') and t_el.text is not None]) if is_el is not None else None
                    else:
                        ve=c.find('{%s}v'%NS_MAIN)
                        v=ve.text if ve is not None else None
                    if idx>=len(vals): vals.append(v)
                    else: vals[idx]=v
                rows.append(vals); row.clear()
    header=rows[0]; width=len(header); data=[]
    for r in rows[1:]:
        data.append((r+[None]*(width-len(r)))[:width])
    return pd.DataFrame(data, columns=header)

def load_data() -> Dict[str,pd.DataFrame]:
    mapping={'transactions':'xl/worksheets/sheet1.xml','kyc':'xl/worksheets/sheet2.xml','merchants':'xl/worksheets/sheet3.xml','geobehavior':'xl/worksheets/sheet4.xml'}
    with zipfile.ZipFile(XLSX) as z:
        log('carregando sharedStrings')
        sst=load_shared(z)
        dfs={}
        for name,path in mapping.items():
            log(f'carregando {name}')
            dfs[name]=sheet_to_df(z,path,sst)
            log(f'{name} {dfs[name].shape}')
    return dfs

def prep(dfs):
    t=dfs['transactions'].copy(); k=dfs['kyc'].copy(); m=dfs['merchants'].copy(); g=dfs['geobehavior'].copy()
    for c in ['amount_brl','amount_orig','fx_to_brl','installments','mcc','geolocation_lat','geolocation_lon']:
        t[c]=pd.to_numeric(t[c], errors='coerce')
    for c in ['annual_income_brl','kyc_risk_score']: k[c]=pd.to_numeric(k[c], errors='coerce')
    for c in ['mcc','merchant_chargeback_ratio_90d']: m[c]=pd.to_numeric(m[c], errors='coerce')
    for c in ['tx_count','counterparties','avg_amount','tx_window_days','tx_per_day']: g[c]=pd.to_numeric(g[c], errors='coerce')
    t['timestamp']=pd.to_datetime(t['timestamp'], errors='coerce')
    t['date']=t['timestamp'].dt.date.astype(str); t['month']=t['timestamp'].dt.to_period('M').astype(str); t['hour']=t['timestamp'].dt.hour
    k['date_of_birth']=pd.to_datetime(k['date_of_birth'], errors='coerce'); k['registration_date']=pd.to_datetime(k['registration_date'], errors='coerce')
    t['is_confirmed']=t['status'].eq('Confirmed')
    t['is_round_100']=np.isclose(t['amount_brl'].round(2) % 100, 0)
    t['near_10k']=t['amount_brl'].between(9000, 9999.99)
    t['subject_customer_id']=np.where(t['sender_entity_type'].eq('customer'), t['sender_id'], np.where(t['receiver_entity_type'].eq('customer'), t['receiver_id'], None))
    t['subject_direction']=np.where(t['subject_customer_id'].eq(t['sender_id']), 'out', 'in')
    t['merchant_id']=np.where(t['receiver_entity_type'].eq('merchant'), t['receiver_id'], np.where(t['sender_entity_type'].eq('merchant'), t['sender_id'], None))
    k_pref=k.add_prefix('kyc_').rename(columns={'kyc_customer_id':'subject_customer_id'})
    t=t.merge(k_pref,on='subject_customer_id',how='left')
    m_pref=m.add_prefix('merchant_').rename(columns={'merchant_merchant_id':'merchant_id'})
    t=t.merge(m_pref,on='merchant_id',how='left')
    ref=t['timestamp'].max()
    t['subject_age']=((ref - t['kyc_date_of_birth']).dt.days/365.25).round(1)
    t['months_since_registration']=((ref - t['kyc_registration_date']).dt.days/30.44).round(1)
    t['monthly_income_est']=t['kyc_annual_income_brl']/12
    return t,k,m,g

def add_rules(t):
    df=t.copy(); rules=[]
    def rule(name, cond, points):
        df[name]=cond.fillna(False).astype(bool); rules.append((name, points))
    rule('R01_tx_sanctions_screening_hit', df['sanctions_screening_hit'].eq('Yes'), 100)
    rule('R02_subject_on_sanctions_list', df['kyc_sanctions_list_hit'].eq('Yes'), 95)
    rule('R03_pep_crossborder_or_high_value', df['kyc_pep'].eq('Yes') & (df['cross_border'].eq('Yes') | (df['amount_brl']>=10000) | df['country_risk_receiver'].eq('High')), 35)
    rule('R04_wire_to_high_risk_country', df['transaction_type'].eq('Wire') & df['country_risk_receiver'].eq('High'), 45)
    rule('R05_crossborder_high_risk_receiver', df['cross_border'].eq('Yes') & df['country_risk_receiver'].eq('High'), 45)
    rule('R06_geo_or_ip_high_risk', df['country_risk_geo'].eq('High') | df['country_risk_ip'].eq('High') | df['country_risk_sender'].eq('High'), 20)
    rule('R07_large_amount_50k_plus', df['amount_brl']>=50000, 30)
    rule('R08_card_ecommerce_without_3ds', df['transaction_type'].eq('Card') & df['capture_method'].eq('E-commerce') & df['card_present'].eq('No') & df['auth_3ds'].eq('No'), 18)
    rule('R09_chargeback_status', df['status'].eq('Chargeback'), 20)
    rule('R10_high_risk_mcc', df['merchant_mcc_risk'].eq('High'), 15)
    rule('R11_high_risk_merchant_or_cb_ratio', df['merchant_merchant_high_risk_flag'].eq('Yes') | (df['merchant_merchant_chargeback_ratio_90d']>=0.08), 20)
    rule('R12_self_merchant', df['subject_customer_id'].notna() & df['merchant_owner_customer_id'].notna() & df['subject_customer_id'].eq(df['merchant_owner_customer_id']), 80)
    rule('R13_ip_anomaly_or_proxy_tor_vpn', df['ip_anomaly'].eq('Yes') | df['ip_proxy_vpn_tor'].isin(['Proxy','VPN','Tor']), 12)
    rule('R14_rooted_device', df['device_rooted'].eq('Yes'), 10)
    rule('R15_near_10k_structuring_proxy', df['near_10k'], 12)
    rule('R16_low_income_high_single_tx', df['monthly_income_est'].notna() & (df['amount_brl']>=np.maximum(df['monthly_income_est']*2,10000)), 18)
    rule_cols=[r[0] for r in rules]
    df['tx_rule_count']=df[rule_cols].sum(axis=1).astype(int)
    score=np.zeros(len(df), dtype=float)
    for name,points in rules: score+=df[name].astype(int).values*points
    df['tx_rule_score']=score
    arr=df[rule_cols].values
    df['tx_rules_triggered']=['; '.join([rule_cols[i] for i,v in enumerate(row) if v]) for row in arr]
    catalog=pd.DataFrame([{'rule_id':n.split('_')[0],'rule_name':n,'level':'transaction','points':p} for n,p in rules])
    return df,catalog

def build_inv(tx):
    a=tx[tx['sender_entity_type'].eq('customer')].copy(); a['customer_id']=a['sender_id']; a['direction']='out'
    b=tx[tx['receiver_entity_type'].eq('customer')].copy(); b['customer_id']=b['receiver_id']; b['direction']='in'
    inv=pd.concat([a,b],ignore_index=True)
    inv['dir_in']=inv['direction'].eq('in').astype(int); inv['dir_out']=inv['direction'].eq('out').astype(int)
    inv['amt_in']=np.where(inv['direction'].eq('in'), inv['amount_brl'], 0.0); inv['amt_out']=np.where(inv['direction'].eq('out'), inv['amount_brl'], 0.0)
    for new,cond in {
        'is_pix':inv['transaction_type'].eq('PIX'), 'is_card':inv['transaction_type'].eq('Card'), 'is_wire':inv['transaction_type'].eq('Wire'),
        'is_crossborder':inv['cross_border'].eq('Yes'), 'is_high_receiver':inv['country_risk_receiver'].eq('High'),
        'is_sanctions_tx':inv['sanctions_screening_hit'].eq('Yes'), 'is_high_mcc':inv['merchant_mcc_risk'].eq('High'),
        'is_high_merchant':inv['merchant_merchant_high_risk_flag'].eq('Yes'), 'is_chargeback':inv['status'].eq('Chargeback'),
    }.items(): inv[new]=cond.astype(int)
    return inv

def month_alerts(inv,k):
    # unique counterparties approximate by receiver_id; for incoming it can still be sender merchants, okay for proxy
    agg=inv.groupby(['customer_id','month']).agg(
        tx_count=('transaction_id','count'), confirmed_count=('is_confirmed','sum'), total_amount=('amount_brl','sum'), avg_amount=('amount_brl','mean'), max_amount=('amount_brl','max'),
        cash_in_count=('dir_in','sum'), cash_out_count=('dir_out','sum'), cash_in_amount=('amt_in','sum'), cash_out_amount=('amt_out','sum'),
        pix_count=('is_pix','sum'), card_count=('is_card','sum'), wire_count=('is_wire','sum'), cross_border_count=('is_crossborder','sum'), high_risk_country_count=('is_high_receiver','sum'),
        sanctions_tx_count=('is_sanctions_tx','sum'), high_risk_mcc_count=('is_high_mcc','sum'), high_risk_merchant_count=('is_high_merchant','sum'), ecommerce_no3ds_count=('R08_card_ecommerce_without_3ds','sum'),
        chargeback_count=('is_chargeback','sum'), ip_anomaly_proxy_count=('R13_ip_anomaly_or_proxy_tor_vpn','sum'), rooted_count=('R14_rooted_device','sum'), near_10k_count=('near_10k','sum'),
        self_merchant_count=('R12_self_merchant','sum'), tx_rule_score_sum=('tx_rule_score','sum'), tx_rule_score_max=('tx_rule_score','max'), unique_counterparties=('receiver_id','nunique')
    ).reset_index()
    kk=k[['customer_id','full_name','cpf_cnpj','annual_income_brl','risk_rating','pep','kyc_tier','kyc_risk_score','sanctions_list_hit','declared_occupation','date_of_birth','registration_date','state','city','beneficial_owner']]
    agg=agg.merge(kk,on='customer_id',how='left')
    agg['monthly_income_est']=agg['annual_income_brl']/12
    factor=agg['risk_rating'].map({'Low':2.0,'Medium':1.5,'High':1.0}).fillna(2.0)
    agg['out_profile_threshold']=np.maximum(agg['monthly_income_est']*factor,20000)
    rules=[]
    def mr(name,cond,points): agg[name]=cond.fillna(False).astype(bool); rules.append((name,points))
    mr('M01_monthly_out_of_profile_dynamic', agg['total_amount']>=agg['out_profile_threshold'],35)
    mr('M02_velocity_high_volume', (agg['tx_count']>=15)&(agg['total_amount']>=50000),25)
    mr('M03_structuring_near_10k_repeated', agg['near_10k_count']>=3,30)
    mr('M04_cashin_to_cashout_pass_through_proxy', (agg['cash_in_count']>=2)&(agg['cash_out_count']>=5)&(agg['cash_out_amount']>=0.7*agg['cash_in_amount'])&(agg['total_amount']>=20000),30)
    mr('M05_crossborder_concentration', (agg['cross_border_count']>=3)&((agg['cross_border_count']/agg['tx_count'])>=0.3),22)
    mr('M06_high_risk_country_repeated', agg['high_risk_country_count']>=2,35)
    mr('M07_sanctions_any_period', (agg['sanctions_tx_count']>=1)|agg['sanctions_list_hit'].eq('Yes'),100)
    mr('M08_pep_high_volume', agg['pep'].eq('Yes')&(agg['total_amount']>=50000),35)
    mr('M09_high_risk_mcc_repeated', agg['high_risk_mcc_count']>=5,20)
    mr('M10_ecommerce_no3ds_repeated', agg['ecommerce_no3ds_count']>=2,18)
    mr('M11_device_ip_risk_repeated', agg['ip_anomaly_proxy_count']>=3,18)
    mr('M12_self_merchant_any', agg['self_merchant_count']>=1,80)
    rule_cols=[r[0] for r in rules]
    agg['month_rule_count']=agg[rule_cols].sum(axis=1).astype(int)
    score=np.zeros(len(agg), dtype=float)
    for n,p in rules: score+=agg[n].astype(int).values*p
    agg['month_rule_score']=score
    arr=agg[rule_cols].values
    agg['month_rules_triggered']=['; '.join([rule_cols[i] for i,v in enumerate(row) if v]) for row in arr]
    catalog=pd.DataFrame([{'rule_id':n.split('_')[0],'rule_name':n,'level':'customer_month','points':p} for n,p in rules])
    return agg,catalog

def daily_pass(inv):
    a=inv.copy(); a['day']=a['timestamp'].dt.date.astype(str)
    d=a.groupby(['customer_id','day']).agg(in_count=('dir_in','sum'),out_count=('dir_out','sum'),in_amount=('amt_in','sum'),out_amount=('amt_out','sum'),tx_count=('transaction_id','count'),cross_border_count=('is_crossborder','sum')).reset_index()
    d['daily_pass_through_flag']=(d['in_count']>=1)&(d['out_count']>=2)&(d['out_amount']>=0.7*d['in_amount'])&(d['in_amount']>=5000)
    return d[d['daily_pass_through_flag']].sort_values(['out_amount','tx_count'],ascending=False)

def rank_clients(ma, tx):
    cust=ma.groupby('customer_id').agg(months_alerted=('month_rule_count',lambda s:(s>0).sum()), max_month_rule_score=('month_rule_score','max'), total_month_rule_score=('month_rule_score','sum'), max_month_rule_count=('month_rule_count','max'), total_amount=('total_amount','sum'), tx_count=('tx_count','sum'), max_tx_amount=('max_amount','max'), sanctions_tx_count=('sanctions_tx_count','sum'), cross_border_count=('cross_border_count','sum'), high_risk_country_count=('high_risk_country_count','sum'), near_10k_count=('near_10k_count','sum'), ecommerce_no3ds_count=('ecommerce_no3ds_count','sum'), self_merchant_count=('self_merchant_count','sum'), first_month=('month','min'), last_month=('month','max')).reset_index()
    prof=ma.sort_values('customer_id').drop_duplicates('customer_id')
    pcols=['customer_id','full_name','cpf_cnpj','annual_income_brl','risk_rating','pep','kyc_tier','kyc_risk_score','sanctions_list_hit','declared_occupation','state','city','beneficial_owner','registration_date','date_of_birth']
    cust=cust.merge(prof[pcols],on='customer_id',how='left')
    top_tx=tx.groupby('subject_customer_id').agg(max_tx_rule_score=('tx_rule_score','max'),total_tx_rule_score=('tx_rule_score','sum'),suspicious_tx_count=('tx_rule_count',lambda s:(s>0).sum())).reset_index().rename(columns={'subject_customer_id':'customer_id'})
    cust=cust.merge(top_tx,on='customer_id',how='left').fillna({'max_tx_rule_score':0,'total_tx_rule_score':0,'suspicious_tx_count':0})
    cust['final_customer_score']=cust['max_month_rule_score']+cust['max_tx_rule_score']+np.minimum(cust['total_month_rule_score']/10,50)+np.minimum(cust['suspicious_tx_count'],20)
    cust['priority']=pd.cut(cust['final_customer_score'],[-1,60,120,999],labels=['Média','Alta','Crítica'])
    front=['customer_id','full_name','cpf_cnpj','priority','final_customer_score','max_tx_rule_score','max_month_rule_score','total_amount','tx_count','suspicious_tx_count','sanctions_tx_count','sanctions_list_hit','pep','risk_rating','kyc_risk_score','annual_income_brl','declared_occupation','cross_border_count','high_risk_country_count','near_10k_count','ecommerce_no3ds_count','self_merchant_count','first_month','last_month']
    cust=cust[[c for c in front if c in cust.columns]+[c for c in cust.columns if c not in front]]
    return cust.sort_values(['final_customer_score','max_tx_rule_score','total_amount'],ascending=False)

def money(x):
    return f"R$ {float(x):,.2f}".replace(',', 'X').replace('.', ',').replace('X','.')

def make_sar(cid, tx, ma, rank):
    c=rank[rank.customer_id.eq(cid)].iloc[0]
    txc=tx[(tx['subject_customer_id'].eq(cid)) | (tx['sender_id'].eq(cid)) | (tx['receiver_id'].eq(cid))].copy().sort_values('timestamp')
    top=txc.sort_values(['tx_rule_score','amount_brl'],ascending=False).head(10)
    months=ma[ma.customer_id.eq(cid)].sort_values('month')
    lines=[f"# SAR Draft — Cliente {cid}\n\n"]
    lines.append("## 1. Identificação\n\n")
    lines.append(f"- Cliente: {cid}\n- Nome cadastral: {c.get('full_name','n/d')}\n- CPF/CNPJ: {c.get('cpf_cnpj','n/d')}\n")
    lines.append(f"- Perfil KYC: risco {c.get('risk_rating','n/d')}, PEP={c.get('pep','n/d')}, sanções cadastrais={c.get('sanctions_list_hit','n/d')}, ocupação={c.get('declared_occupation','n/d')}\n")
    lines.append(f"- Renda anual declarada: {money(c.get('annual_income_brl',0) or 0)}\n- Período analisado: {txc.timestamp.min()} a {txc.timestamp.max()}\n\n")
    lines.append("## 2. Resumo executivo\n\n")
    lines.append(f"O cliente {cid} foi priorizado com score {c['final_customer_score']:.1f} e prioridade {c['priority']}. No período, movimentou {money(c['total_amount'])} em {int(c['tx_count'])} transações, com {int(c['cross_border_count'])} transações cross-border e {int(c['high_risk_country_count'])} eventos associados a país/contraparte de risco alto. ")
    st=txc[txc['sanctions_screening_hit'].eq('Yes')]
    if len(st):
        r=st.iloc[0]
        lines.append(f"Foi identificado hit de sanctions screening na transação {r['transaction_id']}, em {r['timestamp']}, no valor de {money(r['amount_brl'])}, com receiver_country={r['receiver_country']} e country_risk_receiver={r['country_risk_receiver']}. ")
    lines.append("A combinação de sanções, país de risco, cross-border e alertas de perfil/atividade justifica investigação formal e preparação de comunicação, sujeita à revisão humana.\n\n")
    lines.append("## 3. Sinais e alertas\n\n")
    for _,m in months.iterrows():
        if m['month_rule_count']>0:
            lines.append(f"- {m['month']}: {int(m['month_rule_count'])} regras mensais, score {int(m['month_rule_score'])}, total {money(m['total_amount'])}, regras: {m['month_rules_triggered']}\n")
    lines.append("\n## 4. Timeline analítica\n\n")
    for _,r in top.sort_values('timestamp').iterrows():
        lines.append(f"- {r['timestamp']} | {r['transaction_id']} | {r['transaction_type']} | {money(r['amount_brl'])} | status={r['status']} | receiver_country={r['receiver_country']} | regras={r['tx_rules_triggered']}\n")
    lines.append("\n## 5. Base legal e normativa — alto nível\n\n")
    lines.append("- Lei nº 9.613/1998: prevenção e repressão à lavagem ou ocultação de bens, direitos e valores.\n")
    lines.append("- Circular BCB nº 3.978/2020: política, procedimentos e controles internos de PLD/FT para instituições autorizadas pelo BCB.\n")
    lines.append("- Carta Circular BCB nº 4.001/2020: relação de operações e situações que podem configurar indícios de LD/FT passíveis de comunicação ao COAF.\n")
    lines.append("- Recomendações do FATF/GAFI: abordagem baseada em risco, diligência de clientes e comunicação de operações suspeitas.\n\n")
    lines.append("## 6. Conclusão e ações recomendadas\n\n")
    lines.append("Recomenda-se abertura de investigação formal, validação em listas oficiais, revisão de KYC/beneficiário final, análise de contrapartes e merchants associados, aplicação de fricção operacional quando permitido e preparação de comunicação de operação suspeita ao COAF caso a revisão humana confirme os indícios.\n")
    return ''.join(lines)

def main():
    OUT_ROOT.mkdir(parents=True,exist_ok=True)
    log('load data'); dfs=load_data()
    log('prep'); tx,k,m,g=prep(dfs)
    log('tx rules'); txr,cat_tx=add_rules(tx)
    log('involved'); inv=build_inv(txr)
    log('month alerts'); ma,cat_m=month_alerts(inv,k)
    log('rank clients'); rank=rank_clients(ma,txr)
    log('pass through'); dp=daily_pass(inv)
    catalog=pd.concat([cat_tx,cat_m],ignore_index=True)
    logic={
        'R01_tx_sanctions_screening_hit':'sanctions_screening_hit = Yes na transação.','R02_subject_on_sanctions_list':'Cliente sujeito da transação possui sanctions_list_hit = Yes no KYC.','R03_pep_crossborder_or_high_value':'Cliente PEP com cross-border, valor >= R$10k ou país receiver High.','R04_wire_to_high_risk_country':'Wire com receiver em país de risco alto.','R05_crossborder_high_risk_receiver':'Transação cross-border com receiver_country classificado como High.','R06_geo_or_ip_high_risk':'País de geolocalização/IP/sender classificado como High.','R07_large_amount_50k_plus':'amount_brl >= R$50.000.','R08_card_ecommerce_without_3ds':'Card + E-commerce + card_present=No + auth_3ds=No.','R09_chargeback_status':'status = Chargeback.','R10_high_risk_mcc':'mcc_risk = High.','R11_high_risk_merchant_or_cb_ratio':'merchant_high_risk_flag=Yes ou chargeback ratio 90d >= 8%.','R12_self_merchant':'subject_customer_id igual ao owner_customer_id do merchant.','R13_ip_anomaly_or_proxy_tor_vpn':'ip_anomaly=Yes ou IP via Proxy/VPN/Tor.','R14_rooted_device':'device_rooted=Yes.','R15_near_10k_structuring_proxy':'amount_brl entre R$9.000 e R$9.999,99.','R16_low_income_high_single_tx':'Transação >= max(2x renda mensal estimada, R$10.000).','M01_monthly_out_of_profile_dynamic':'Total mensal >= max(renda mensal estimada × fator por risco, R$20k). Fator: Low 2x, Medium 1,5x, High 1x.','M02_velocity_high_volume':'tx_count mensal >=15 e total_amount >= R$50.000.','M03_structuring_near_10k_repeated':'near_10k_count mensal >=3.','M04_cashin_to_cashout_pass_through_proxy':'cash-in >=2, cash-out >=5, cash-out >=70% do cash-in e total >= R$20k.','M05_crossborder_concentration':'cross_border_count >=3 e >=30% das transações do mês.','M06_high_risk_country_repeated':'high_risk_country_count mensal >=2.','M07_sanctions_any_period':'sanctions transaction >=1 ou KYC sanctions_list_hit=Yes.','M08_pep_high_volume':'PEP com total mensal >= R$50.000.','M09_high_risk_mcc_repeated':'high_risk_mcc_count mensal >=5.','M10_ecommerce_no3ds_repeated':'e-commerce sem 3DS >=2 no mês.','M11_device_ip_risk_repeated':'sinais de IP anômalo/proxy/vpn/tor >=3 no mês.','M12_self_merchant_any':'self_merchant_count >=1 no mês.'}
    catalog['logic']=catalog['rule_name'].map(logic)
    catalog['justification']='Regra explicável para priorização AML/FT; limiares conservadores para reduzir ruído e preservar rastreabilidade da investigação.'
    tx_cols=['transaction_id','timestamp','subject_customer_id','kyc_full_name','kyc_cpf_cnpj','transaction_type','status','amount_brl','currency','channel','capture_method','merchant_id','merchant_merchant_name','merchant_mcc','merchant_mcc_risk','merchant_merchant_high_risk_flag','sender_id','receiver_id','sender_entity_type','receiver_entity_type','sender_country','receiver_country','country_risk_receiver','geo_country','ip_country','ip_anomaly','ip_proxy_vpn_tor','device_rooted','cross_border','sanctions_screening_hit','kyc_risk_rating','kyc_pep','kyc_sanctions_list_hit','tx_rule_count','tx_rule_score','tx_rules_triggered']
    tx_top=txr[txr.tx_rule_count>0].sort_values(['tx_rule_score','amount_brl'],ascending=False)[[c for c in tx_cols if c in txr.columns]].head(30)
    top_clients=rank.head(30)
    log('save csv')
    catalog.to_csv(OUT_ROOT/'01_rule_catalog_t1.csv',index=False)
    tx_top.to_csv(OUT_ROOT/'02_suspicious_transactions_top30.csv',index=False)
    top_clients.to_csv(OUT_ROOT/'03_suspicious_clients_top30.csv',index=False)
    ma.sort_values(['month_rule_score','total_amount'],ascending=False).to_csv(OUT_ROOT/'04_client_month_alerts_all.csv',index=False)
    dp.head(100).to_csv(OUT_ROOT/'05_daily_pass_through_candidates.csv',index=False)
    sc=rank[rank.sanctions_tx_count>0].sort_values(['final_customer_score','max_tx_rule_score'],ascending=False)
    cid=sc.iloc[0].customer_id if len(sc) else top_clients.iloc[0].customer_id
    timeline=txr[(txr['subject_customer_id'].eq(cid))|txr['sender_id'].eq(cid)|txr['receiver_id'].eq(cid)].sort_values('timestamp')
    timeline_cols=['transaction_id','timestamp','transaction_type','status','amount_brl','sender_id','receiver_id','sender_entity_type','receiver_entity_type','merchant_id','receiver_country','country_risk_receiver','cross_border','sanctions_screening_hit','tx_rule_score','tx_rules_triggered']
    timeline[[c for c in timeline_cols if c in timeline.columns]].to_csv(OUT_ROOT/f'06_sar_candidate_timeline_{cid}.csv',index=False)
    (OUT_ROOT/f'07_SAR_draft_{cid}.md').write_text(make_sar(cid,txr,ma,rank),encoding='utf-8')
    summary=f'''# Tarefa 1 — Suspeitos e SAR (DIA 1)\n\n## Visão geral\n\n- Transações avaliadas: {len(txr):,}\n- Clientes-mês com pelo menos um alerta mensal: {(ma.month_rule_count>0).sum():,}\n- Transações com pelo menos uma regra disparada: {(txr.tx_rule_count>0).sum():,}\n- Regras implementadas nesta etapa: {len(catalog)} ({len(cat_tx)} transacionais + {len(cat_m)} cliente-mês)\n- Candidato de SAR selecionado: {cid}\n\n## Top 10 clientes suspeitos\n\n{top_clients[['customer_id','priority','final_customer_score','total_amount','tx_count','sanctions_tx_count','sanctions_list_hit','pep','risk_rating','cross_border_count','high_risk_country_count']].head(10).to_markdown(index=False)}\n\n## Top 10 transações suspeitas\n\n{tx_top[['transaction_id','timestamp','subject_customer_id','transaction_type','amount_brl','receiver_country','country_risk_receiver','sanctions_screening_hit','tx_rule_score','tx_rules_triggered']].head(10).to_markdown(index=False)}\n\n## Observações\n\n- O ranking prioriza sanções, países de alto risco, self-merchant, PEP com exposição cross-border, fora de perfil e concentração de alertas.\n- Valores ausentes e outliers foram preservados como informação de risco, sem remoção automática.\n- O SAR é um draft analítico e deve passar por revisão humana, enriquecimento de KYC/listas e validação jurídica/compliance antes de comunicação.\n'''
    (OUT_ROOT/'00_T1_suspects_summary.md').write_text(summary,encoding='utf-8')
    # package repo tree
    log('package')
    if PKG_ROOT.exists(): shutil.rmtree(PKG_ROOT)
    (PKG_ROOT/'outputs'/'t1_suspects').mkdir(parents=True,exist_ok=True); (PKG_ROOT/'src').mkdir(parents=True,exist_ok=True)
    for f in OUT_ROOT.iterdir():
        if f.is_file(): shutil.copy2(f,PKG_ROOT/'outputs'/'t1_suspects'/f.name)
    shutil.copy2(Path(__file__),PKG_ROOT/'src'/'rules.py')
    (PKG_ROOT/'src'/'utils.py').write_text('''"""Utilidades para o case AML/FT."""\n\nRANDOM_STATE = 42\nTIMEZONE = "America/Sao_Paulo"\n''',encoding='utf-8')
    shutil.make_archive(str(PACKAGE_ARCHIVE), 'zip', PKG_ROOT)
    print(json.dumps({'candidate_id':cid,'zip':str(PACKAGE_ARCHIVE.with_suffix('.zip')),'top_clients':top_clients.head(5)[['customer_id','priority','final_customer_score','total_amount','tx_count','sanctions_tx_count','sanctions_list_hit','pep','risk_rating']].to_dict('records'),'top_transactions':tx_top.head(5)[['transaction_id','subject_customer_id','transaction_type','amount_brl','receiver_country','sanctions_screening_hit','tx_rule_score']].to_dict('records')},ensure_ascii=False,default=str,indent=2))
if __name__=='__main__': main()
