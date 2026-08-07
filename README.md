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

Foi estruturado um baseline canônico XGBoost na unidade cliente-mês:

- base integralmente sintética;
- `weak_label` derivado exclusivamente das regras determinísticas M01–M12;
- `R17` fora do label canônico;
- treino em julho/2025;
- calibragem e seleção estatística de threshold em agosto/2025;
- teste temporal em setembro/2025;
- outubro/2025 excluído por mês incompleto;
- 5 features categóricas e 16 numéricas;
- `random_state=42`;
- métricas de AUC-PR, AUC-ROC, precision, recall, FPR e MCC;
- grid de thresholds entre 0,1 e 0,9;
- feature importance por gain e SHAP reproduzíveis por código.

Na calibragem, a regra `max_mcc_statistical_baseline` selecionou o threshold 0,3. Esse valor não foi homologado operacionalmente.

No teste temporal, os resultados foram:

- AUC-PR: 0,3167;
- AUC-ROC: 0,8269;
- precision: 0,2096;
- recall: 0,7773;
- FPR: 0,2831;
- MCC: 0,2986;
- 816 alertas em 2.498 registros, ou aproximadamente 32,67% da fila.

Essas métricas medem a capacidade de aproximar um label fraco derivado de regras. Elas não provam atividade ilícita, não constituem validação produtiva e não eliminam a circularidade conceitual entre label e features. O split é temporal, mas não é independente por entidade, pois os mesmos clientes podem aparecer em meses sucessivos.

A geração dos outputs tabulares, feature importance, SHAP e gráficos canônicos está versionada e reproduzível por código.

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
4. `outputs/t3_ml_canonical/` - dataset canônico cliente-mês, splits, métricas, thresholds, explicabilidade, ranking de teste e gráficos reproduzíveis.
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
- O Notebook 03 está alinhado ao pipeline canônico de ML; os demais notebooks continuam com escopos próprios de demonstração e validação.
- Os outputs canônicos da T3, incluindo SHAP e gráficos, são regeneráveis pelo código versionado.
- O modelo utiliza label fraco derivado de M01–M12 e não equivale a uma decisão investigativa confirmada.
- O threshold 0,3 é apenas o baseline estatístico `max_mcc_statistical_baseline` selecionado na calibragem e não representa calibragem operacional definitiva.
- O split é temporal, mas não independente por entidade.
- A R17 permanece separada do motor principal e fora do label canônico.
- A T4 é uma simulação determinística, sem integração ativa com LLM.
- Nenhum componente deve ser interpretado como solução pronta para produção ou decisão automática de compliance.

## Princípio central

Regras primeiro, ML para priorização e agentes para organização controlada do fluxo, sempre com evidências rastreáveis e decisão humana.
