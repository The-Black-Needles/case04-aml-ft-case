# Outputs T4 - Arquitetura multiagente

## Estado atual

Esta pasta contém documentação e exemplos de uma simulação determinística do fluxo AML/FT.

A implementação atual não realiza chamadas reais a LLM.

## Arquivos

### `00_T4_agents_summary.md`

Resumo técnico, limites atuais e evolução planejada.

### `01_agent_prompts.md`

Prompts de referência para os papéis:

- Dados;
- Detecção;
- Investigação;
- Reporte;
- Compliance.

Os prompts ainda não são enviados a um provedor externo.

### `02_agent_workflow_run.md`

Exemplo versionado de execução sequencial.

O conteúdo ainda precisa ser regenerado para ficar integralmente alinhado ao schema atual de `src/agents.py`.

### `03_agent_workflow_run.json`

Exemplo de saída estruturada.

O arquivo atual não deve ser interpretado como log de uma inferência real por LLM.

### `04_agent_diagram.mmd`

Diagrama Mermaid do fluxo sequencial.

### `05_agent_roles.csv`

Resumo dos papéis e responsabilidades.

## Código relacionado

- `src/agents.py`
- `notebooks/04_agents.ipynb`
- `docs/05_t4_multi_agente_explicacao.md`
- `presentation/roteiro_t4_multi_agente.md`

## O que o protótipo demonstra

- decomposição do processo em cinco papéis;
- execução sequencial;
- prompts de referência;
- achados e decisões estruturados;
- arquivos de evidência;
- revisão humana como princípio.

## O que o protótipo não demonstra

- inferência ativa por LLM;
- autonomia investigativa;
- integração com API;
- eventos ou filas reais;
- decisão automática de compliance;
- deploy;
- operação produtiva.

## Como explicar

“Esta etapa demonstra uma arquitetura controlada para organizar dados, detecção, investigação, reporte e compliance. Na versão atual, o fluxo é determinístico e não chama um LLM. A evolução v2 adicionará contratos tipados, estado compartilhado, handoffs, checkpoints humanos, logs e integração opcional com um provedor.”

## Princípio de segurança

Nenhuma conclusão de risco, comunicação regulatória ou ação sobre cliente deve ser executada automaticamente.

A decisão deve permanecer sob responsabilidade humana.
