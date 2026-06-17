# Roteiro de apresentação — 30 a 40 minutos

## 1. Abertura — 2 minutos

“Eu organizei o case como uma investigação AML orientada a dados. A ideia foi começar pela qualidade da base, depois validar comportamento por rail, transformar sinais em regras explicáveis, ranquear suspeitos e estruturar um SAR.”

## 2. Estrutura da base — 4 minutos

“Primeiro eu olhei as abas disponíveis: transações, KYC, merchants, comportamento geográfico e dicionário de dados. A base principal tem 52 mil transações e se conecta com os perfis de clientes e merchants.”

Ponto principal:
- Mostrar que a análise não começou por regra, mas por entendimento da base.

## 3. Qualidade e coerência — 5 minutos

“Antes de criar alerta, eu validei se os dados faziam sentido: duplicatas, datas, valores negativos, nulos e relacionamento entre tabelas.”

Ponto principal:
- Explicar que campos nulos podem ser informativos.
- Explicar que alguns nulos são apenas “não aplicável” por rail.

## 4. Análise por rail — 5 minutos

“Eu separei PIX, Card e Wire porque cada rail tem risco diferente.”

PIX:
- Foco em cash-in/cash-out, velocidade, conta de passagem e mule account.

Card:
- Foco em e-commerce, 3DS, MCC de risco e chargeback.

Wire:
- Foco em cross-border, país de destino, sanções e alto valor.

## 5. Sinais iniciais AML — 5 minutos

“Na EDA já apareceram sinais relevantes: sanções, PEP, cliente high risk, MCC high risk, IP anomaly, device rooted, cross-border e país de alto risco.”

Ponto principal:
- Não tratar todo sinal como caso suspeito automaticamente.
- Sinal isolado vira triagem; combinação de sinais vira prioridade.

## 6. Regras e ranking — 8 minutos

“Depois da EDA, transformei os sinais em regras. Separei regras transacionais e regras cliente-mês.”

Regras transacionais:
- Sanções.
- País de alto risco.
- Alto valor.
- E-commerce sem 3DS.
- MCC de risco.
- Device/IP anomaly.
- Self-merchant.

Regras cliente-mês:
- Fora de perfil.
- Alto volume mensal.
- Muitos cash-ins/cash-outs.
- Valores redondos.
- Velocity.
- Possível conta de passagem.

Ponto principal:
- Explicar que o ranking prioriza combinação de sinais.

## 7. SAR — 6 minutos

“Para o SAR, eu escolhi um caso com materialidade, combinação de alertas e timeline investigável.”

Estrutura do SAR:
- Identificação.
- Resumo executivo.
- Sinais de alerta.
- Timeline.
- Análise.
- Base legal em alto nível.
- Conclusão.
- Ações recomendadas.

Ponto principal:
- SAR não afirma crime.
- SAR comunica suspeita fundamentada.

## 8. Fechamento — 3 minutos

“Minha lógica foi manter clareza e explicabilidade. Primeiro regras, depois priorização. O próximo passo é evoluir isso para modelo de ML explicável, usando label fraco baseado nas regras e métricas adequadas para dados desbalanceados.”

## Frase final

“O valor do case está em transformar dados brutos em uma fila AML auditável, priorizada e defensável para investigação.”

---

## Bloco adicional — T2 Sistema de Alertas

Tempo sugerido: 5 a 7 minutos.

### Como introduzir

“Depois de fazer a EDA e identificar os primeiros sinais AML, eu transformei esses sinais em um sistema de alertas. A ideia foi criar regras explicáveis, com parâmetros claros e exemplos reais na base.”

### O que mostrar no repo

Abrir a pasta:

`outputs/t2_alert_system/`

Mostrar primeiro:

`00_T2_alert_system_summary.md`

Depois abrir:

`01_alert_rules_catalog_t2.csv`

### Fala principal

“Na T2 eu formalizei o motor de alertas. Primeiro eu peguei os sinais que apareceram na EDA e transformei em regras objetivas. Depois separei as regras em transacionais e comportamentais por cliente-mês. Cada regra tem lógica, parâmetro, severidade, tipologia AML, exemplo na base e ação operacional sugerida. A prioridade não vem de um alerta isolado, mas da combinação de sinais.”

### Ponto que preciso reforçar

“Eu escolhi começar por regras antes do ML porque AML precisa de explicabilidade. Um alerta precisa ser auditável. O analista precisa conseguir explicar por que aquele cliente ou transação entrou na fila.”

### Frase curta de fechamento da T2

“O motor de alertas é a ponte entre a EDA e o ML: ele transforma sinais em decisões auditáveis e também gera o label fraco que será usado na modelagem.”

