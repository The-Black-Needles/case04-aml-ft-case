# Estado dos notebooks 01 e 02

## Objetivo

Os notebooks 01 e 02 foram criados para tornar o raciocínio de EDA e regras mais fácil de inspecionar.

## Benefícios atuais

- Organizam a leitura técnica.
- Mostram parte do raciocínio passo a passo.
- Facilitam a navegação durante a apresentação.
- Relacionam análise exploratória, regras e outputs.

## Limites atuais

Os notebooks estão versionados:

- sem contadores de execução;
- sem outputs;
- com referência ao nome antigo da planilha;
- sem evidência de execução ponta a ponta.

O notebook 02 não substitui todo o motor de regras.

Além disso:

- `src/alerts.py` possui erro de sintaxe;
- `src/rules.py` ainda utiliza caminhos antigos;
- a R17 ainda não está integrada ao motor principal;
- nem todos os outputs são regenerados pelos notebooks.

## Formulação correta

Os notebooks melhoram a documentação e a demonstração do raciocínio.

Eles ainda não comprovam reprodução integral nem representam lógica produtiva.

## Próximos passos

- corrigir caminhos;
- alinhar notebooks e scripts;
- executar em Python 3.11;
- registrar outputs;
- adicionar smoke tests;
- validar os artefatos gerados;
- documentar um comando de execução.
