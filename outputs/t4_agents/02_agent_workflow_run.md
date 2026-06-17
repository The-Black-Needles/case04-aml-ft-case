# Execução sequencial multi-agente AML/FT

## Agente 1 — Dados

**Objetivo:** validar qualidade, ingesta e coerência por rail.

**Achados:**
- Base principal validada com transações, KYC, merchants e comportamento geográfico.
- PIX, Card e Wire foram tratados separadamente para evitar comparação indevida.
- Ausentes e outliers foram preservados como possíveis sinais informativos.

**Saída para o próximo agente:** contexto de dados confiável para detecção.

## Agente 2 — Detecção

**Objetivo:** combinar regras e ML para priorizar alertas.

**Achados:**
- Regras explicáveis da T2 funcionam como primeira camada.
- Score ML da T3 entra como camada de priorização.
- Casos com múltiplos sinais independentes têm maior prioridade.

**Saída para o próximo agente:** fila priorizada de clientes/transações.

## Agente 3 — Investigação

**Objetivo:** montar entidade 360°, timeline e hipótese AML.

**Achados:**
- Caso `C101208` foi mantido como candidato de SAR.
- A timeline consolida fatos relevantes e evita duplicidade.
- A análise diferencia indícios de conclusão definitiva.

**Saída para o próximo agente:** narrativa investigativa estruturada.

## Agente 4 — Reporte

**Objetivo:** gerar SAR estruturado.

**Achados:**
- SAR deve conter identificação, resumo, sinais, timeline, análise, base legal, conclusão e ações.
- Linguagem deve ser objetiva, rastreável e não acusatória.

**Saída para o próximo agente:** SAR draft pronto para revisão.

## Agente 5 — Compliance

**Objetivo:** revisar aderência regulatória e trilha de auditoria.

**Achados:**
- Base legal deve ser citada em alto nível: Lei 9.613/1998, Circular BCB 3.978/2020, Carta Circular BCB 4.001/2020 e FATF/GAFI.
- Ausência de campo explícito de espécie precisa ser registrada.
- Sanções, PEP e país de alto risco devem ter tratamento prioritário.

**Saída final:** SAR e fila AML com evidências, versionamento e trilha auditável.
