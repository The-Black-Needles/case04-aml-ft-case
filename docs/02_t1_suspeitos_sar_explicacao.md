# T1 — suspeitos e SAR: explicação para apresentação

## Objetivo da T1

A Tarefa 1 pede até 30 clientes e/ou 30 transações suspeitas, além de um SAR completo.

Minha abordagem foi criar primeiro regras explicáveis, depois usar essas regras para gerar ranking.

Isso é importante porque, em AML, o analista precisa justificar por que um caso foi priorizado. Não basta dizer que um modelo ou score apontou suspeita.

## Como as regras foram estruturadas

As regras foram divididas em dois níveis:

1. Regras transacionais
   - Avaliam uma transação individual.
   - Exemplos: sanções, país de alto risco, alto valor, e-commerce sem 3DS, MCC de risco, IP anomaly, device rooted e self-merchant.

2. Regras cliente-mês
   - Avaliam comportamento agregado.
   - Exemplos: fora de perfil, alto volume mensal, muitos cash-outs, muitos cash-ins, valores redondos, velocity e possível conta de passagem.

Essa separação ajuda porque algumas tipologias aparecem em uma transação isolada, enquanto outras só aparecem quando olhamos o comportamento acumulado.

## Como o ranking foi feito

Eu priorizei clientes e transações pela combinação de alertas.

A ideia foi simples: quanto mais sinais independentes aparecem juntos, maior a prioridade de investigação.

Exemplo de combinação forte:

- Cliente com risco alto.
- Transações cross-border.
- País de destino de alto risco.
- Hit de sanções.
- Alto valor.
- Volume mensal fora do perfil.
- Comportamento compatível com conta de passagem.

Esse tipo de combinação é mais relevante do que olhar para um único alerta isolado.

## Por que escolhi o caso do SAR

O SAR draft foi montado para o cliente `C101208` porque ele apareceu como um caso forte dentro do ranking.

A escolha não foi baseada em um único fator, mas em combinação de sinais, timeline e materialidade.

O objetivo do SAR não é “provar crime”. O objetivo é registrar uma suspeita fundamentada, com sinais objetivos, linha do tempo e recomendação de comunicação ou escalonamento.

## Como eu explicaria em entrevista

“Depois da EDA, eu transformei os sinais em regras auditáveis. Separei regras transacionais de regras comportamentais por cliente-mês. Em seguida, criei um ranking priorizado com base na quantidade e gravidade dos sinais. Para o SAR, escolhi um caso com materialidade e múltiplos indícios, organizei a timeline e conectei os fatos com tipologias AML e base regulatória em alto nível.”

## Base regulatória em alto nível

A documentação final deve usar:

- Circular BCB nº 3.978/2020: política, procedimentos e controles internos de PLD/FT.
- Carta Circular BCB nº 4.001/2020: relação de operações e situações que podem configurar indícios de LD/FT.
- Lei nº 9.613/1998: base legal brasileira de lavagem de dinheiro.
- Recomendações FATF/GAFI: referência internacional de abordagem baseada em risco.

Observação: sempre validar a versão vigente no site do BCB antes da entrega final.
