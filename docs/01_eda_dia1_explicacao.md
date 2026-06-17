# EDA DIA 1 — explicação para apresentação

## Objetivo da EDA

Nesta etapa, meu objetivo foi entender a base antes de sair criando regras.

Em AML, um erro comum é olhar direto para valores altos ou para clientes suspeitos sem validar se os dados estão coerentes. Então eu comecei pelo básico: abas, volume, tipos, nulos, duplicatas, datas e consistência entre tabelas.

## O que eu validei

A base tem cinco partes principais:

- `Transactions`: transações.
- `KYC_Profiles`: dados cadastrais e risco do cliente.
- `Merchants`: dados dos estabelecimentos.
- `GeoBehavior`: comportamento geográfico e velocidade.
- `Data_Dictionary`: dicionário de dados.

A aba principal é `Transactions`, com 52 mil transações. Também há 2.500 clientes em KYC, 1.000 merchants e dados complementares de comportamento geográfico.

## Por que validar por rail

Eu separei a análise por rail porque PIX, cartão e wire têm naturezas diferentes.

PIX costuma ter volume maior e pode indicar cash-in/cash-out, conta de passagem, mule account e velocidade.

Cartão exige olhar para e-commerce, 3DS, MCC de risco, card-present/card-not-present e chargeback.

Wire exige mais atenção para cross-border, país de destino, sanções e alto valor.

Se eu misturasse tudo sem separar por rail, poderia criar falso positivo por comparar comportamentos que não são equivalentes.

## Principais achados da EDA

Os principais pontos da EDA foram:

- A base está íntegra para análise.
- Não encontrei duplicatas relevantes.
- Os timestamps estão válidos.
- Os valores em reais estão coerentes com câmbio e moeda original.
- PIX concentra a maior parte do volume transacional.
- Existem sinais relevantes de AML: sanções, PEP, país de alto risco, MCC de risco, alto valor, e-commerce sem 3DS, IP anomaly e device rooted.

## Limitações encontradas

Um ponto importante é que a base não traz um campo explícito de transação em espécie.

Por isso, valores acima de R$50 mil foram tratados como alto valor, mas não como comunicação automática de espécie. Para comunicação automática de espécie, seria necessário ter evidência de que a operação foi em dinheiro físico.

Também percebi que `device_fingerprint` e `ip_address` são praticamente únicos por transação. Então, nesta base, não faz sentido forçar uma regra de “device ring” por reutilização exata. O melhor é usar sinais como `device_rooted`, `ip_anomaly` e risco geográfico.

## Como eu explicaria em entrevista

“Eu comecei pela EDA porque queria garantir que as regras AML fossem construídas sobre dados coerentes. Separei a análise por rail, porque PIX, cartão e wire têm riscos diferentes. Depois validei volume, datas, nulos, duplicatas, integridade entre tabelas e sinais iniciais de risco. Com isso, consegui sair de uma visão exploratória para uma fila priorizada de alertas.”
