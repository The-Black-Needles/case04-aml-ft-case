# Outputs T4 — Multi-Agente LLM

## O que tem nesta pasta

Esta pasta contém a documentação e a simulação do fluxo multi-agente AML/FT.

## Arquivos principais

### `00_T4_agents_summary.md`

Resumo executivo da T4.

### `01_agent_prompts.md`

Prompts dos cinco agentes:

- Dados
- Detecção
- Investigação
- Reporte
- Compliance

### `02_agent_workflow_run.md`

Exemplo de execução sequencial do fluxo.

Mostra o que cada agente recebe, decide e entrega para o próximo passo.

### `03_agent_workflow_run.json`

Saída estruturada em JSON. Útil para auditoria, integração e rastreabilidade.

### `04_agent_diagram.mmd`

Diagrama Mermaid do fluxo.

## Como explicar esta etapa em 1 minuto

“Esta etapa mostra como eu usaria LLMs de forma segura e operacional em AML. O fluxo é sequencial: primeiro valida dados, depois detecta alertas com regras e ML, depois investiga, depois gera SAR e por fim revisa compliance. O agente não toma decisão sozinho; ele organiza evidências e ajuda o analista a trabalhar mais rápido, com trilha auditável.”

## Ponto de atenção

O desenho é propositalmente sequencial e controlado. Para AML, isso é melhor do que um agente totalmente autônomo, porque facilita auditoria, revisão humana e explicação para compliance.
