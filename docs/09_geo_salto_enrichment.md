# Enriquecimento — Regra literal de geo-salto

## Objetivo

Este enriquecimento foi criado porque o desafio cita explicitamente geo-salto como uma tipologia possível. A versão anterior do case já considerava risco geográfico e IP de risco, mas este ajuste adiciona uma regra literal de distância e tempo entre transações consecutivas do mesmo cliente.

## Regra adicionada

**R17 — Geo-salto físico improvável**

Lógica:

- ordenar transações por cliente e timestamp;
- comparar cada transação com a imediatamente anterior do mesmo cliente;
- calcular distância pela fórmula de Haversine usando latitude/longitude;
- disparar alerta quando distância >= 500 km e intervalo <= 12h;
- priorizar quando houver sinais contextuais: país de risco, IP anomaly, proxy/VPN/Tor, device rooted, cross-border, mudança de país ou distância extrema.

## Resultados na base

- Transações lidas: 52000
- Transações de clientes com geolocalização válida: 46760
- Clientes com geolocalização: 2500
- Candidatos literais: 4247
- Clientes únicos com candidatos literais: 1997
- Candidatos priorizados: 1942
- Clientes únicos em candidatos priorizados: 1304

## Como explicar na apresentação

“Na primeira versão eu já olhava risco geográfico, país de IP e cross-border. Como o desafio cita geo-salto explicitamente, adicionei uma regra literal de distância e tempo. Eu comparo transações consecutivas do mesmo cliente e calculo se o deslocamento seria fisicamente plausível. Como geolocalização pode ser ruidosa, especialmente em base sintética, eu não uso essa regra sozinha para bloquear. Ela serve para aumentar prioridade quando aparece junto com outros sinais, como IP anomaly, país de risco, device rooted ou cross-border.”

## Trade-off

Geo-salto é uma regra útil, mas sensível a falso positivo.

Possíveis causas legítimas ou ruído:

- geolocalização aproximada;
- IP corporativo ou VPN legítima;
- transação card-not-present;
- viagem real;
- dados sintéticos com coordenadas distribuídas artificialmente.

Por isso, o uso correto é como sinal contextual dentro de uma fila AML, não como decisão automática isolada.
