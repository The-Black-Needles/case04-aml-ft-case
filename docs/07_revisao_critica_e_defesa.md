# Revisão crítica e defesa do case

## Objetivo deste documento

Este arquivo existe para me ajudar a defender as decisões do case durante a apresentação.

A ideia não é decorar respostas. A ideia é saber explicar o racional de forma simples, objetiva e segura.

---

## 1. Por que comecei pela EDA?

Eu comecei pela EDA porque, em AML, uma regra ruim em cima de dado ruim gera falso positivo e perda de confiança.

Antes de procurar suspeitos, eu precisava validar:

- estrutura da base;
- volume por tabela;
- tipos de transação;
- nulos;
- duplicatas;
- datas;
- valores inconsistentes;
- relacionamento entre transações, clientes e merchants;
- coerência por rail.

A frase para explicar é:

“Antes de criar alerta, eu quis garantir que os dados faziam sentido. Em AML, qualidade de dado é parte do controle.”

---

## 2. Por que separar por rail?

Porque PIX, Card e Wire têm riscos diferentes.

PIX tem mais relação com velocidade, cash-in/cash-out, mule account e conta de passagem.

Card exige olhar para e-commerce, 3DS, MCC de risco, chargeback e card-present/card-not-present.

Wire exige atenção maior para cross-border, país de destino, sanções e alto valor.

A frase para explicar é:

“Eu separei por rail porque comparar PIX, cartão e wire como se fossem iguais aumentaria falso positivo.”

---

## 3. Por que usar regras antes de ML?

Porque AML precisa de explicabilidade.

Uma regra permite dizer:

- o que aconteceu;
- qual parâmetro foi usado;
- por que aquilo é suspeito;
- qual ação operacional faz sentido.

O ML entra depois para priorizar, mas a base explicável começa nas regras.

A frase para explicar é:

“O ML ajuda a priorizar, mas a explicação operacional vem primeiro das regras.”

---

## 4. Por que usar label fraco no ML?

A base não tinha uma coluna oficial dizendo “fraude” ou “lavagem”.

Então eu criei um label fraco usando a própria lógica AML:

- cliente-mês com 3 ou mais regras disparadas = suspeito;
- caso contrário = não suspeito.

Isso não significa que o label é perfeito. Significa que ele é uma aproximação operacional para treinar um modelo de priorização.

A frase para explicar é:

“Como eu não tinha label investigativo final, usei as regras como proxy. O modelo aprende a priorizar casos parecidos com os que o motor de regras já considerou relevantes.”

---

## 5. Por que o resultado do ML ficou alto?

Porque o label fraco foi criado a partir de regras, e as features também capturam parte desses comportamentos.

Então o modelo não deve ser vendido como “modelo perfeito”.

A leitura correta é:

- bom baseline;
- boa capacidade de priorização;
- útil para ranking;
- precisa ser validado com histórico real de investigações;
- precisa de calibragem antes de produção.

A frase para explicar é:

“O desempenho alto faz sentido porque é um baseline supervisionado por regras. Em produção, eu validaria com casos reais encerrados e calibraria threshold com o time de compliance.”

---

## 6. Por que escolher threshold alto?

Em AML, a fila de investigação é limitada.

Se eu usar threshold muito baixo, gero volume alto e falso positivo.

Se eu uso threshold mais alto, priorizo menos casos, mas com mais concentração de sinais.

A decisão depende da capacidade operacional do time.

A frase para explicar é:

“O threshold não é só decisão estatística. Ele precisa considerar capacidade operacional, apetite de risco e SLA de investigação.”

---

## 7. Por que o SAR não afirma crime?

Porque SAR ou comunicação de suspeita não é condenação.

O objetivo é registrar indícios objetivos, materialidade, timeline e motivo de suspeita.

A frase para explicar é:

“O SAR não conclui crime. Ele comunica uma suspeita fundamentada para avaliação pelas autoridades competentes.”

---

## 8. Como defender o multi-agente?

O multi-agente não substitui o analista.

Ele organiza o fluxo:

1. valida dados;
2. detecta alertas;
3. monta visão 360;
4. estrutura SAR;
5. revisa compliance e auditoria.

A frase para explicar é:

“O LLM entra como apoio de padronização e produtividade, mas com revisão humana e evidências rastreáveis.”

---

## 9. Principais limitações do case

As principais limitações são:

- base sintética ou de case, não produção real;
- ausência de label oficial de investigação;
- ausência de campo explícito de espécie/cash;
- device e IP quase únicos, limitando análise de ring por reutilização;
- modelo treinado com label fraco;
- necessidade de validação regulatória final antes de produção.

A frase para explicar é:

“Eu tratei essas limitações de forma conservadora. Quando o dado não sustentava uma conclusão, eu não forcei a tipologia.”

---

## 10. Principal mensagem do case

A mensagem central é:

“Eu construí uma esteira AML completa: começo com qualidade de dados, passo por regras explicáveis, gero ranking de suspeitos, estruturo SAR, uso ML para priorização e proponho multi-agente para padronizar a operação.”
