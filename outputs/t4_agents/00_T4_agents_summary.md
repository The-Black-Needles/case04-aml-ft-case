# T4 - Protótipo determinístico de arquitetura multiagente

## Objetivo

A T4 demonstra como organizar uma investigação AML/FT em cinco componentes especializados, sequenciais e orientados à auditabilidade.

O protótipo prioriza:

- separação de responsabilidades;
- contexto estruturado;
- evidências rastreáveis;
- explicabilidade;
- revisão humana.

## Papéis

### Dados

- qualidade;
- coerência por rail;
- enriquecimento;
- registro de limitações.

### Detecção

- regras AML;
- score de ML;
- priorização;
- consolidação de alertas.

### Investigação

- entidade 360°;
- timeline;
- deduplicação;
- organização de evidências;
- separação entre fatos e hipóteses.

### Reporte

- estrutura de SAR;
- narrativa não acusatória;
- associação entre fatos e evidências.

### Compliance

- revisão regulatória em alto nível;
- sanções e PEP;
- consistência;
- trilha de auditoria;
- encaminhamento para revisão humana.

## Princípio central

O desenho proposto é híbrido:

- regras primeiro, pela explicabilidade;
- ML depois, como camada de priorização;
- agentes por último, para organizar contexto e fluxo.

Regras e modelos permanecem como núcleo determinístico.

## Natureza da implementação atual

O arquivo `src/agents.py` executa uma simulação determinística e sequencial.

Ele demonstra:

- cinco papéis;
- prompts de referência;
- saídas estruturadas em dicionários;
- achados;
- decisões;
- próximas ações;
- arquivos de evidência;
- passagem de contexto.

O script não realiza chamadas a provedores externos de LLM.

## O que ainda não está implementado

- inferência real por LLM;
- orquestrador com roteamento condicional;
- estado compartilhado tipado;
- eventos e filas executáveis;
- checkpoints humanos no código;
- retorno entre etapas;
- decisão `approve`, `revise` ou `escalate`;
- versionamento de prompts por execução;
- hashes dos artefatos;
- retry e timeout;
- integração por API;
- operação produtiva.

## Limitação dos outputs

Os arquivos Markdown e JSON desta pasta foram produzidos em uma etapa anterior.

Eles ainda precisam ser regenerados pelo script atual para garantir alinhamento entre:

- código;
- schema;
- conteúdo;
- evidências;
- documentação.

## Formulação para apresentação

“Na T4, construí um protótipo determinístico com cinco papéis: Dados, Detecção, Investigação, Reporte e Compliance. O código demonstra separação de responsabilidades, passagem de contexto e referências de evidência. Ele ainda não realiza inferência real por LLM nem toma decisões autônomas.”

## Evolução v2

A evolução planejada deverá incluir:

- orquestrador explícito;
- `CaseState` compartilhado;
- contratos tipados;
- handoffs;
- eventos;
- filas;
- status;
- evidências associadas;
- retorno entre etapas;
- checkpoints humanos;
- decisão `approve`, `revise` ou `escalate`;
- `run_id`;
- timestamps em `America/Sao_Paulo`;
- versões e hashes;
- falha segura;
- testes automatizados.

Serão preservados dois modos:

- offline determinístico e reproduzível;
- integração LLM opcional e desacoplada.
