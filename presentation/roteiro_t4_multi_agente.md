# Roteiro T4 — Multi-Agente LLM

Tempo sugerido: 5 a 7 minutos.

## Como introduzir

“Depois das regras e do modelo de ML, eu desenhei uma camada multi-agente para apoiar a operação AML de ponta a ponta.”

## O que mostrar no repo

Abrir:

`outputs/t4_agents/README.md`

Depois mostrar:

`outputs/t4_agents/04_agent_diagram.mmd`

Depois abrir:

`src/agents.py`

## Fala principal

“Esse fluxo tem cinco agentes. O primeiro valida dados e coerência por rail. O segundo combina regras e ML para priorizar alertas. O terceiro investiga a entidade com timeline e deduplicação. O quarto monta o SAR. O quinto revisa compliance, sanções, BACEN, COAF, FATF e trilha de auditoria.”

## Ponto que preciso reforçar

“O LLM não toma decisão sozinho. Ele atua como apoio operacional para organizar evidências, padronizar investigação e reduzir esforço manual. A decisão continua revisável por analista e compliance.”

## Frase curta de fechamento

“O multi-agente conecta tudo que foi construído antes: EDA, regras, suspeitos, SAR e ML em uma esteira AML auditável.”
