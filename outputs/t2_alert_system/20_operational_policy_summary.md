# T2 — Política operacional das regras

## Objetivo

Este artefato normaliza como o protótipo distingue threshold implementado, potencial de calibragem e ação operacional recomendada para as 28 regras do motor principal.

A matriz não altera a lógica das regras, pontuação ou thresholds existentes.

## Thresholds implementados

- `DYNAMIC_ACTIVE`: 2 regras — R16 e M01.
- `FIXED_NUMERIC`: 13 regras.
- `EVENT_OR_CATEGORY`: 13 regras.

`DYNAMIC_ACTIVE` significa que o valor efetivamente usado pelo motor varia de acordo com atributos do cliente. R16 depende da renda estimada e M01 combina renda e risco.

Uma regra marcada como `CALIBRATABLE_CANDIDATE` continua usando o parâmetro fixo/categórico atual. A classificação apenas registra que uma calibragem futura pode ser testada.

## Ação operacional normalizada

- `MONITOR`: 4 regras.
- `REVIEW`: 19 regras.
- `ESCALATE`: 5 regras.

`MONITOR` é reservado a sinais contextuais que, isoladamente, têm maior risco de ruído. Repetição, materialidade ou combinação com outros sinais pode elevar o caso para revisão.

`REVIEW` direciona o caso para investigação humana antes de qualquer decisão material.

`ESCALATE` é usado para sinais críticos, incluindo sanções e self-merchant, que exigem tratamento prioritário.

## Bloqueio

Nenhuma das 28 regras autoriza bloqueio automático.

R01, R02 e M07 são `conditional_block_eligible` somente após validação da evidência crítica em fonte oficial e aplicação da política interna, jurídico e/ou Compliance.

R12 e M12 são críticos e devem ser escalados, mas a relação self-merchant isolada não autoriza bloqueio automático.

## Limites

- Base sintética.
- Política operacional experimental.
- Sem homologação produtiva.
- Sem decisão autônoma.
- Revisão humana obrigatória.
