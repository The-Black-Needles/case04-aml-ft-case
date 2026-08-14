# T2 — Sistema de Alertas: explicação para apresentação

## Objetivo

Nesta etapa, eu transformei os achados da EDA e da T1 em um sistema formal de alertas.

A ideia foi sair de uma lista de sinais soltos e criar regras com nome, lógica, parâmetros, exemplo real na base, justificativa e ação operacional.

## Por que regras primeiro

Em AML, explicabilidade é essencial. O analista precisa conseguir responder: “por que esse cliente entrou na fila?”.

Por isso, eu usei regras antes de ML. As regras dão rastreabilidade, ajudam a montar o SAR e depois podem servir como label fraco para treinar o modelo.

## Como organizei as regras

Eu separei em dois blocos:

1. Regras transacionais
   - Olham uma transação individual.
   - Exemplo: sanções, país de risco, alto valor, e-commerce sem 3DS, MCC de risco, self-merchant.

2. Regras cliente-mês
   - Olham o comportamento agregado do cliente no mês.
   - Exemplo: fora de perfil, velocity, structuring, cash-in para cash-out, concentração cross-border e repetição de sinais técnicos.

Essa separação é importante porque algumas suspeitas aparecem em um evento único, mas outras só aparecem quando a gente olha o padrão acumulado.

## Como eu explicaria os pesos

Eu dei mais peso para sinais críticos, como sanções e self-merchant.

Sinais de contexto, como MCC de risco ou device rooted, têm peso menor porque sozinhos podem gerar falso positivo. Mas eles ficam fortes quando aparecem junto com alto valor, cross-border, chargeback, país de risco ou fora de perfil.

## Limiares dinâmicos

O principal limiar dinâmico é o fora de perfil por renda e risco.

Em vez de usar o mesmo valor para todo mundo, o sistema considera o risco cadastral:

- Cliente de risco baixo: alerta quando movimenta muito acima da renda.
- Cliente de risco médio: limiar mais sensível.
- Cliente de risco alto: limiar ainda mais sensível.

Isso faz sentido porque AML deve seguir uma abordagem baseada em risco.

## Pontos de cuidado

Eu não tratei transação acima de R$50 mil como comunicação automática de espécie, porque a base não tem campo dizendo que a operação foi em dinheiro físico.

Também não forcei uma regra de device/IP ring por fingerprint repetido, porque os IPs e devices da base são majoritariamente únicos. Preferi usar sinais técnicos mais confiáveis dentro da base: IP anomaly, Proxy/VPN/Tor e device rooted.

## Backtesting descritivo e homologação

Depois da formalização do motor, eu adicionei um backtesting reproduzível para responder quatro perguntas operacionais:

- quais regras mais acionam;
- como a carga muda entre PIX, Card e Wire;
- quantas regras tendem a disparar na mesma observação;
- quais pares apresentam sobreposição empírica suficiente para merecer revisão.

A análise também segmenta transações por `status`, mas esse campo não é tratado como ground truth. Isso é especialmente importante para Chargeback, porque o próprio status participa da lógica da R09 e criaria circularidade se fosse usado para afirmar precisão.

Sem decisões investigativas independentes, eu não calculo falso positivo, falso negativo, precision ou recall das regras. O resultado é um backtesting descritivo sobre dados sintéticos, não uma homologação produtiva.

Os indicadores de coocorrência também não desativam regras automaticamente. Eles geram evidência para revisão humana de redundância, conflito, cobertura e impacto operacional.

A entrada recomendada é `outputs/t2_alert_system/17_backtesting_summary.md`.

## Como eu explicaria em entrevista

“Na T2 eu formalizei o motor de alertas e depois criei um backtesting reproduzível. Além de saber qual regra dispara, eu consigo medir carga da fila, cobertura por rail e sobreposição entre regras. Como a base é sintética e não tem ground truth investigativo independente, eu não apresento falso positivo ou falso negativo como se fossem métricas validadas. Esses resultados servem para revisão e calibragem supervisionadas, não para desativação automática de regras.”
