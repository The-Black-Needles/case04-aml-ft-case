# Perguntas e respostas para apresentação

## 1. Por que você começou pela EDA?

Porque eu precisava garantir que a base estava coerente antes de criar alerta. Em AML, dado inconsistente gera falso positivo e prejudica a investigação.

Resposta curta:

“Comecei pela EDA porque qualidade de dado é parte do controle AML.”

---

## 2. Qual foi a principal decisão técnica do case?

A principal decisão foi começar por regras explicáveis antes de ML.

Resposta curta:

“Eu priorizei explicabilidade. Primeiro regras auditáveis, depois ML para priorização.”

---

## 3. Por que separar PIX, Card e Wire?

Porque cada rail tem riscos e campos diferentes.

Resposta curta:

“PIX, cartão e wire têm comportamentos diferentes. Separar por rail reduz comparação injusta e falso positivo.”

---

## 4. O que torna uma transação ou cliente suspeito no seu ranking?

A combinação de sinais.

Um alerta isolado pode ser apenas triagem. Vários sinais juntos aumentam prioridade.

Resposta curta:

“O ranking prioriza concentração de sinais independentes, não apenas um evento isolado.”

---

## 5. Como você escolheu o SAR?

Escolhi um caso com materialidade, múltiplos alertas, timeline investigável e sinais compatíveis com tipologias AML.

Resposta curta:

“Escolhi o caso com maior capacidade de sustentação: sinais, materialidade e linha do tempo.”

---

## 6. O SAR afirma que houve lavagem de dinheiro?

Não.

Resposta curta:

“O SAR não prova crime. Ele comunica suspeita fundamentada.”

---

## 7. Por que usar label fraco no ML?

Porque a base não tinha label oficial de caso confirmado.

Resposta curta:

“Usei as regras como proxy porque não havia label investigativo final.”

---

## 8. O modelo de ML está pronto para produção?

Não diretamente.

Ele é um baseline técnico para priorização. Antes de produção, eu validaria com histórico real, calibraria threshold e monitoraria drift.

Resposta curta:

“Está pronto como baseline de case, não como modelo produtivo sem validação adicional.”

---

## 9. Como interpretar as métricas do ML?

O desempenho deve ser lido como capacidade de aproximar um label fraco derivado das regras, não como prova independente de atividade ilícita.

No teste temporal, o modelo registrou AUC-PR de 0,3167 e AUC-ROC de 0,8269. O split é temporal, mas não independente por entidade, e permanece circularidade conceitual entre o label e parte das features.

Resposta curta:

“Eu interpreto as métricas como desempenho experimental na aproximação do label fraco. Elas não validam produção nem provam detecção independente de ilícito.”

---

## 10. Qual métrica você priorizaria em AML?

Depende do objetivo.

Para triagem AML, recall é importante para não perder casos relevantes, mas FPR e capacidade operacional também importam.

Resposta curta:

“Eu olharia recall, precision, FPR e MCC juntos, porque AML depende de risco e capacidade de investigação.”

---

## 11. Por que não remover outliers?

Porque em AML outlier pode ser o próprio sinal.

Resposta curta:

“Outliers são informativos. Eu não removeria sem análise.”

---

## 12. Como o multi-agente ajuda na operação?

Ele padroniza etapas repetitivas: validação, detecção, investigação, SAR e compliance.

Resposta curta:

“O multi-agente ajuda a organizar evidências e reduzir esforço manual, mantendo revisão humana.”

---

## 13. Qual foi o maior trade-off do case?

Balancear sensibilidade e falso positivo.

Resposta curta:

“Quanto mais sensível o alerta, maior a fila. Por isso eu priorizei combinação de sinais.”

---

## 14. O que você faria se tivesse mais tempo?

Eu faria:

- validação mais profunda do SAR;
- calibragem de threshold com capacidade operacional;
- separação PF/PJ mais robusta;
- mais testes de drift;
- dashboard de investigação;
- integração com listas externas de sanções/PEP.

Resposta curta:

“Eu evoluiria o baseline para uma esteira mais próxima de produção, com validação histórica e monitoramento contínuo.”

---

## 15. Qual é a mensagem final do case?

Resposta curta:

“Transformei dados brutos em uma fila AML explicável, priorizada e defensável.”
