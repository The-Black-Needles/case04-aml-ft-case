# Relatório AML/FT - Case (versão enriquecida)

**Estilo visual:** alinhado ao deck dark theme do case  
**Versão:** enriquecida após PPTX, geo-salto literal, grafo do SAR e reforço de notebooks.

## Resumo executivo

Este relatório consolida o case AML/FT ponta a ponta: EDA, validação por rail, regras explicáveis, ranking de suspeitos, SAR completo, modelo de ML com label fraco e arquitetura multi-agente. O estilo visual segue a mesma identidade da apresentação, com foco em clareza, concisão e defesa técnica.

## Principais números

- 52.000 transações analisadas
- 2.500 clientes KYC
- 1.000 merchants
- 29 regras formalizadas (28 originais + geo-salto literal)
- 30 transações suspeitas priorizadas
- 30 clientes suspeitos priorizados
- SAR escolhido: C101208

## Enriquecimentos adicionados

1. **PPTX executivo** com mesma identidade visual do case.
2. **Regra literal de geo-salto** (≥ 500 km em ≤ 12h entre transações consecutivas do mesmo cliente), tratada como alerta contextual.
3. **Grafo simples do SAR** para visão 360° do caso C101208.
4. **Notebooks 01/02 reforçados** para melhorar a reprodutibilidade do fluxo técnico.

## T1 — Suspeitos e SAR

O cliente **C101208** foi escolhido para SAR por reunir materialidade e combinação de sinais: movimentação de R$ 162 mil, renda declarada de R$ 13 mil/ano, 9 transações cross-border, 1 hit de sanções, país de alto risco no destino e recorrência de alertas mensais. O grafo do caso mostra cliente, rails, países, merchants e principais alertas, ajudando a sustentar a visão 360°.

## T2 — Sistema de alertas

O motor de alertas foi estruturado com lógica, parâmetros, exemplo na base, justificativa e ação operacional. O enriquecimento mais relevante foi a regra de geo-salto literal. Como a base é sintética, essa regra foi mantida como sinal contextual e não como bloqueio automático isolado.

## T3 — Modelo de ML

O modelo XGBoost PF cliente-mês usou label fraco baseado em regras (3+ regras = suspeito). O desempenho foi forte (AUC-PR 0,9416; AUC-ROC 0,9970; threshold sugerido 0,90), mas a leitura correta continua sendo: baseline explicável de priorização, e não decisão autônoma pronta para produção.

## T4 — Multi-agente LLM

O fluxo multi-agente foi mantido simples e prático: Dados → Detecção → Investigação → Reporte → Compliance. Cada etapa recebe a saída estruturada da etapa anterior. O LLM ajuda a organizar evidências, reduzir esforço manual e padronizar narrativa, sempre com revisão humana.

## Limitações e próximos passos

As limitações principais são: base sintética, ausência de label investigativo final, ausência de campo explícito de espécie/cash, geolocalização ruidosa para geo-salto e necessidade de validação histórica para o modelo. Os próximos passos naturais seriam calibragem com histórico real, separação PF/PJ mais robusta, monitoramento de drift e integração com listas externas de sanções/PEP.

## Conclusão

A entrega já está no nível esperado pelo desafio e os enriquecimentos elevaram a robustez de apresentação e defesa técnica sem criar complexidade desnecessária. O principal valor permanece o mesmo: transformar dados brutos em uma fila AML auditável, explicável e priorizada.
