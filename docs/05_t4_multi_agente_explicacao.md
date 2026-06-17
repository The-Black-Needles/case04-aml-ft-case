# T4 — Multi-Agente LLM: explicação para apresentação

## Objetivo da etapa

Nesta etapa, eu desenhei um fluxo multi-agente para apoiar a operação AML/FT de ponta a ponta.

A ideia não é substituir o analista nem deixar um LLM decidir sozinho. A proposta é usar agentes como camadas de apoio para organizar dados, priorizar alertas, montar investigação, estruturar SAR e revisar compliance.

## O que foi feito

Criei um script Python sequencial em `src/agents.py` com cinco agentes:

1. **Dados** — valida ingesta, qualidade, coerência por rail e enriquecimento.
2. **Detecção** — combina regras AML e score de ML para fila priorizada.
3. **Investigação** — monta entidade 360°, timeline e deduplicação de fatos.
4. **Reporte** — estrutura SAR/ROS em linguagem objetiva.
5. **Compliance** — revisa BACEN, COAF, FATF/GAFI, sanções e auditoria.

Também criei prompts, diagrama, exemplo de execução, notebook e roteiro de apresentação.

## Por que foi feito assim

Escolhi um fluxo sequencial porque AML exige controle, rastreabilidade e revisão humana.

Um agente totalmente autônomo seria mais difícil de auditar. Já um fluxo em etapas deixa claro:

- quem recebeu qual contexto;
- qual decisão foi tomada;
- qual evidência foi usada;
- qual saída foi enviada para a próxima etapa.

## Raciocínio principal

O desenho segue a mesma lógica do case:

1. Primeiro dados confiáveis.
2. Depois regras explicáveis.
3. Depois ML para priorização.
4. Depois investigação com timeline.
5. Depois SAR.
6. Por fim revisão de compliance.

## Como explicar em entrevista

“Na T4 eu desenhei um fluxo multi-agente para apoiar AML de forma controlada. O primeiro agente valida os dados; o segundo usa regras e ML para priorizar; o terceiro monta a investigação 360°; o quarto estrutura o SAR; e o quinto revisa compliance e auditoria. O LLM não substitui o analista. Ele organiza evidências, reduz esforço manual e melhora padronização, mantendo revisão humana em cada etapa.”

## Limitações e trade-offs

O principal trade-off é segurança versus autonomia.

Para AML, eu prefiro menos autonomia e mais controle. Por isso o fluxo é sequencial, com saídas estruturadas e checkpoints de revisão humana.

Outra limitação é que o LLM depende da qualidade do contexto fornecido. Por isso o agente de Dados vem primeiro e o motor de regras continua sendo a base explicável da detecção.

## Frase de fechamento

“O multi-agente funciona como uma esteira assistida de investigação AML: ele não decide sozinho, mas ajuda o analista a transformar dados, regras, ML e evidências em uma narrativa auditável e pronta para compliance.”
