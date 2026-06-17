# T4 — Multi-Agente LLM para AML/FT

## Objetivo

A T4 propõe um fluxo multi-agente sequencial para automatizar e padronizar uma investigação AML/FT.

A ideia não é criar um agente autônomo que toma decisão sozinho. A proposta é usar agentes como camadas de apoio ao analista, mantendo explicabilidade, rastreabilidade e revisão humana.

## Arquitetura

O fluxo tem cinco agentes:

1. **Dados** — ingesta, validação por rail, qualidade e enriquecimento.
2. **Detecção** — regras + ML, geração de fila priorizada.
3. **Investigação** — entidade 360°, timeline e deduplicação de fatos.
4. **Reporte** — estruturação de SAR/ROS.
5. **Compliance** — revisão BACEN/COAF/FATF, sanções e auditoria.

## Princípio central

O fluxo é híbrido:

- regras primeiro, porque são auditáveis e explicáveis;
- ML depois, para priorizar e capturar combinações de sinais;
- LLM por último, para organizar contexto, apoiar análise e gerar narrativa revisável.

## Entregáveis desta etapa

- `src/agents.py`: script Python sequencial com os 5 agentes.
- `notebooks/04_agents.ipynb`: notebook para demonstrar o workflow.
- `outputs/t4_agents/01_agent_prompts.md`: prompts dos agentes.
- `outputs/t4_agents/02_agent_workflow_run.md`: exemplo de execução do workflow.
- `outputs/t4_agents/03_agent_workflow_run.json`: saída estruturada dos agentes.
- `outputs/t4_agents/04_agent_diagram.mmd`: diagrama Mermaid.
- `docs/05_t4_multi_agente_explicacao.md`: explicação para apresentação.
- `presentation/roteiro_t4_multi_agente.md`: roteiro curto da T4.

## Como explicar em 1 minuto

“Na T4 eu desenhei um fluxo multi-agente para apoiar a operação AML. O primeiro agente valida os dados, o segundo combina regras e ML para priorizar alertas, o terceiro monta a investigação 360° com timeline, o quarto estrutura o SAR e o quinto faz uma revisão de compliance. O ponto principal é que o LLM não substitui o analista nem decide sozinho. Ele organiza evidências, reduz trabalho manual e mantém uma trilha auditável.”
