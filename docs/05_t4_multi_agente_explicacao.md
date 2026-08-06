# T4 - Protótipo de arquitetura multiagente

## Objetivo

A T4 apresenta um desenho sequencial para organizar uma investigação AML/FT em cinco etapas controladas.

O objetivo é demonstrar:

- separação de responsabilidades;
- passagem estruturada de contexto;
- rastreabilidade;
- evidências versionadas;
- revisão humana;
- auditabilidade.

## Arquitetura

O fluxo possui cinco etapas.

### 1. Dados

Responsável por:

- ingesta;
- validação de qualidade;
- coerência por rail;
- enriquecimento;
- registro de limitações.

### 2. Detecção

Responsável por:

- regras AML;
- score de ML;
- priorização;
- consolidação da fila de alertas.

### 3. Investigação

Responsável por:

- visão de entidade 360°;
- timeline;
- deduplicação;
- organização de evidências;
- hipóteses investigativas.

### 4. Reporte

Responsável por estruturar uma minuta de SAR ou ROS para revisão humana.

### 5. Compliance

Responsável por:

- revisão regulatória em alto nível;
- sanções;
- consistência da narrativa;
- trilha de auditoria;
- encaminhamento para aprovação humana final.

## O que está implementado

O arquivo `src/agents.py` contém uma simulação determinística e sequencial.

O script demonstra:

- prompts de referência;
- saídas estruturadas e contexto compartilhado em dicionário;
- achados;
- decisões;
- próximas ações;
- arquivos de evidência;
- passagem de contexto entre etapas.

A execução não depende de rede ou credenciais externas.

## O que não está implementado

O protótipo não realiza:

- chamadas a OpenAI, Anthropic ou outro provedor;
- inferência real por LLM;
- seleção autônoma de ferramentas;
- investigação autônoma;
- decisão regulatória;
- envio de comunicação;
- operação em produção.

Os prompts funcionam como contratos de referência para uma integração futura.

## Por que usar fluxo sequencial

AML/FT exige controle e capacidade de reconstruir o processo.

Uma arquitetura sequencial facilita identificar:

- qual contexto cada etapa recebeu;
- quais evidências foram consideradas;
- qual saída foi produzida;
- qual decisão ficou pendente;
- onde inserir revisão humana.

## Trade-offs

O desenho privilegia controle sobre autonomia.

Vantagens:

- maior auditabilidade;
- menor risco de decisões opacas;
- contexto mais delimitado;
- facilidade para inserir checkpoints humanos;
- melhor separação de responsabilidades.

Limitações:

- menor autonomia;
- maior latência;
- dependência da qualidade dos dados;
- necessidade de validação dos prompts;
- ausência atual de integração com LLM;
- ausência de avaliações formais de qualidade.

## Como apresentar

“Na T4, construí um protótipo determinístico e sequencial com cinco etapas: Dados, Detecção, Investigação, Reporte e Compliance. O código demonstra estrutura de contexto, saídas estruturadas e referências de evidência. Ele não faz chamadas reais a LLM e não toma decisões autônomas. A proposta é mostrar como uma integração futura poderia ser construída com controle e revisão humana.”

## Evolução futura

Uma implementação com LLM exigiria:

- guardrails;
- controle de acesso;
- minimização de dados;
- logs;
- versionamento de prompts;
- avaliações de qualidade;
- proteção contra prompt injection;
- validação de citações e evidências;
- monitoramento de custo e latência;
- aprovação humana antes de qualquer ação regulatória.
