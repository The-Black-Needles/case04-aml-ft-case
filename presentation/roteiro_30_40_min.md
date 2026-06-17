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
