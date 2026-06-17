# Reforço dos notebooks 01 e 02

## Objetivo

Este enriquecimento reforça a reprodutibilidade do case nos notebooks iniciais.

Os notebooks anteriores já existiam, mas eram mais enxutos. A melhoria adiciona uma sequência mais clara de execução para sustentar a apresentação técnica:

- leitura da base Excel;
- validação de abas, shapes, nulos e duplicatas;
- coerência por rail;
- sinais AML iniciais;
- regras transacionais demonstrativas;
- agregação cliente-mês;
- validação dos outputs finais de suspeitos, SAR e catálogo de regras.

## Arquivos alterados

- `notebooks/01_eda.ipynb`
- `notebooks/02_rules.ipynb`

## Como explicar

“Eu reforcei os notebooks 01 e 02 para que a análise não fique só nos arquivos finais. Eles mostram o caminho técnico: primeiro leio e valido a base, depois aplico regras demonstrativas e comparo com os outputs finais. Isso ajuda a provar reprodutibilidade e raciocínio investigativo.”

## Observação

O notebook 02 não substitui todo o motor de regras em `src/rules.py` e `src/alerts.py`. Ele serve como caderno técnico de validação e explicação, enquanto os scripts concentram a lógica operacional mais completa.
