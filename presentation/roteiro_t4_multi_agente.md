# Roteiro T4 - Arquitetura multiagente

## Tempo sugerido

5 a 7 minutos.

## Introdução

“Depois de regras, investigação e ML, organizei esses componentes em uma arquitetura com cinco papéis especializados.”

## Arquivos para mostrar

- `outputs/t4_agents/04_agent_diagram.mmd`
- `outputs/t4_agents/01_agent_prompts.md`
- `src/agents.py`
- `docs/05_t4_multi_agente_explicacao.md`

## Cinco papéis

### Dados

Valida qualidade, coerência por rail e limitações.

### Detecção

Combina resultados das regras e score de ML para priorização.

### Investigação

Organiza entidade 360°, timeline, fatos, hipóteses e evidências.

### Reporte

Estrutura uma minuta de SAR com linguagem não acusatória.

### Compliance

Revisa coerência, sanções, PEP, base regulatória em alto nível e trilha de auditoria.

## Natureza da implementação

Fala:

“A versão atual é uma simulação determinística. O código executa cinco funções em sequência e registra achados, decisões, próximas ações e referências de evidência. Ele não chama um provedor de LLM.”

## Por que manter o núcleo determinístico?

- regras devem permanecer explicáveis e auditáveis;
- o score deve permanecer reproduzível;
- evidências devem ser verificáveis;
- decisão regulatória exige revisão humana;
- LLM não deve inventar fatos ou executar ação autônoma.

Fala:

“Os agentes organizam o fluxo, mas regras e modelos permanecem como núcleo determinístico.”

## Limitações atuais

- não há inferência ativa por LLM;
- não há estado compartilhado tipado;
- não há roteamento condicional;
- não há eventos e filas executáveis;
- não há checkpoint humano no código;
- não há decisão formal de Compliance;
- os outputs precisam ser regenerados pelo script atual.

## Evolução v2

A próxima versão deverá demonstrar:

- orquestrador;
- `CaseState`;
- contratos tipados;
- handoffs;
- eventos e filas;
- retorno entre etapas;
- checkpoints humanos;
- `approve`, `revise` ou `escalate`;
- `run_id`, timestamps e hashes;
- testes;
- modo offline determinístico;
- integração LLM opcional.

## Fechamento

“A T4 atual demonstra a decomposição funcional e os limites de segurança. A evolução v2 transformará essa sequência em uma orquestração auditável e testada.”
