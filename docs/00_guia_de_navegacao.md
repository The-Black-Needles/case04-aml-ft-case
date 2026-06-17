# Guia de navegação do case AML-FT

Este repositório foi organizado para que a apresentação siga a mesma ordem da investigação.

## Como navegar na apresentação

1. Começar pelo `README.md`
   - Explica o objetivo do case e a estrutura do projeto.

2. Entrar em `outputs/eda_day1/`
   - Mostra a primeira leitura da base.
   - Aqui eu explico qualidade dos dados, abas, volumes, tipos de transação e coerência por rail.

3. Entrar em `outputs/t1_suspects/`
   - Mostra como os sinais viraram regras.
   - Aqui eu explico o ranking de transações suspeitas, ranking de clientes e o caso escolhido para SAR.

4. Entrar em `src/rules.py`
   - Mostra que as regras não foram apenas descritas, mas implementadas em código.
   - A lógica é simples: regras explicáveis primeiro, priorização depois.

5. Entrar em `docs/`
   - Contém os textos curtos para eu explicar o raciocínio de cada etapa.

## Linha narrativa

A narrativa principal é:

“Antes de procurar suspeitos, validei se os dados faziam sentido. Depois transformei sinais AML em regras auditáveis. Com essas regras, gerei um ranking priorizado de clientes e transações. Por fim, escolhi o caso mais forte para estruturar um SAR com identificação, sinais, timeline, base legal, conclusão e ações recomendadas.”

## Tom da apresentação

O tom deve ser natural, objetivo e prático.

Evitar falar como se fosse aula teórica de AML. A ideia é demonstrar raciocínio de investigação, domínio de dados e capacidade de transformar alertas em ação operacional.
