# Roteiro curto — T2 Sistema de Alertas

## Entrada na T2

“Depois de validar a base e identificar os primeiros suspeitos, eu transformei os sinais em um sistema de alertas formal. Aqui o objetivo é deixar claro o que dispara alerta, por qual motivo e com qual prioridade.”

## Explicação rápida

“Eu dividi as regras em dois grupos. O primeiro grupo olha transações individuais. O segundo olha comportamento agregado por cliente no mês.”

## Exemplos de regras transacionais

- Sanções na transação.
- Cliente em lista de sanções no KYC.
- Wire para país de alto risco.
- E-commerce sem 3DS.
- Merchant ou MCC de risco.
- Device/IP suspeito.
- Self-merchant.

## Exemplos de regras cliente-mês

- Movimentação mensal fora de perfil.
- Velocity de alto volume.
- Repetição de valores próximos de R$10 mil.
- Cash-in para cash-out.
- Concentração cross-border.
- Repetição com país de alto risco.

## Mensagem principal

“O ponto mais importante é que eu não trato um alerta isolado como conclusão. O sistema prioriza a combinação de sinais. Isso reduz ruído e cria uma fila mais defensável para investigação.”

## Frase para fechar a T2

“Esse motor de regras cria a ponte entre a investigação manual e o modelo de ML: ele explica os alertas agora e depois vira base para label fraco no treinamento.”
