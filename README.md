# AML/FT & Financial Crime Analytics: Data, Machine Learning and AI Agents

Case técnico público construído sobre dados integralmente sintéticos, com foco em análise transacional, detecção explicável, priorização de alertas, investigação AML/FT, SAR, machine learning e arquitetura de agentes de IA.

O objetivo central é transformar dados brutos em uma fila de investigação auditável, priorizada e defensável.

## Principais números

- 52.000 transações entre julho e outubro de 2025.
- 2.500 perfis KYC.
- 1.000 merchants.
- 3.497 registros de comportamento geográfico.
- 30 transações e 30 clientes priorizados.
- SAR estruturado para o cliente sintético `C101208`.
- 28 regras no motor principal.
- 1 enriquecimento contextual adicional de geo-salto, identificado como `R17`.

## Escopo

### T1 - Suspeitos e SAR

- Ranking das 30 transações mais suspeitas.
- Ranking dos 30 clientes mais suspeitos.
- Timeline e visão de entidade 360°.
- SAR estruturado para `C101208`.
- Grafo de entidades em CSV, Mermaid, JSON e PNG.

### T2 - Sistema de alertas

O motor principal contém 28 regras:

- 16 regras transacionais;
- 12 regras cliente-mês.

Cada regra documenta lógica, parâmetros, severidade, tipologia, rail aplicável, justificativa, exemplo na base e ação operacional.

A regra `R17`, de geo-salto físico improvável, foi adicionada posteriormente como enriquecimento contextual. Seus candidatos estão versionados, mas ela ainda não está integrada ao pipeline principal de forma reproduzível.

### T3 - Machine learning

Foi estruturado um baseline XGBoost para PF na unidade cliente-mês:

- label fraco baseado em três ou mais regras disparadas;
- split temporal;
- `random_state=42`;
- métricas de AUC-PR, AUC-ROC, precision, recall, FPR e MCC;
- tabela de thresholds;
- artefatos de importância de features e SHAP.

Os artefatos versionados registram AUC-PR de 0,9416 e AUC-ROC de 0,9970. Esses valores devem ser interpretados com cautela, pois o label fraco foi derivado das próprias regras e o conjunto de validação também foi usado para comparar thresholds.

A geração completa dos artefatos de SHAP e dos demais outputs de ML ainda precisa ser incorporada ao pipeline público.

### T4 - Arquitetura multiagente

A T4 apresenta um protótipo determinístico e sequencial com cinco etapas:

1. Dados.
2. Detecção.
3. Investigação.
4. Reporte.
5. Compliance.

O script preserva prompts de referência, passagem estruturada de contexto, referências de evidência e revisão humana como princípio de desenho. Ele não realiza chamadas a provedores externos de LLM e não deve ser interpretado como sistema autônomo em produção.

## Como navegar

1. `outputs/eda_day1/` - EDA, qualidade e coerência por rail.
2. `outputs/t1_suspects/` - rankings, timeline, SAR e grafo de entidades.
3. `outputs/t2_alert_system/` - catálogo de regras e candidatos de geo-salto.
4. `outputs/t3_ml/` - dataset modelado, métricas, thresholds e explicabilidade.
5. `outputs/t4_agents/` - prompts, diagrama e simulação determinística.
6. `reports/AML_FT_Case_Report.md` - relatório técnico consolidado.
7. `presentation/roteiro_final_30_40_min.md` - roteiro de apresentação.

## Estrutura do repositório

- `data/raw/`: base sintética.
- `notebooks/`: EDA, regras, ML e agentes.
- `src/`: regras, catálogo de alertas, features, modelo e fluxo sequencial de agentes.
- `outputs/`: artefatos analíticos das quatro tarefas.
- `docs/`: documentação técnica e de defesa.
- `reports/`: relatório consolidado.
- `presentation/`: roteiros e materiais de apresentação.

## Reprodutibilidade e limites

- A base é sintética e não contém dados reais de clientes.
- Os principais artefatos analíticos estão versionados.
- Os notebooks funcionam atualmente como cadernos técnicos de demonstração.
- A reprodução integral de todos os outputs ainda está em consolidação.
- O modelo utiliza label fraco e não equivale a uma decisão investigativa confirmada.
- O threshold de 0,9 não representa calibragem operacional definitiva.
- A R17 permanece separada do motor principal.
- A T4 é uma simulação determinística, sem integração ativa com LLM.
- Nenhum componente deve ser interpretado como solução pronta para produção ou decisão automática de compliance.

## Princípio central

Regras primeiro, ML para priorização e agentes para organização controlada do fluxo, sempre com evidências rastreáveis e decisão humana.
