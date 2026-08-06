# AML/FT & Financial Crime Analytics

**Subtítulo:** Dados, Machine Learning e Arquitetura de Agentes de IA

**Timezone:** America/Sao_Paulo

**Última revisão pública:** 06/08/2026

**Repositório:** `case04-aml-ft-case`

## 1. Resumo executivo

Este case apresenta uma investigação AML/FT orientada a dados sobre uma base integralmente sintética.

O fluxo parte da validação da qualidade e da coerência por rail, avança para regras explicáveis, priorização de suspeitos, elaboração de SAR, modelagem por machine learning e desenho de uma arquitetura multiagente controlada.

A base contém:

- 52.000 transações;
- 2.500 perfis KYC;
- 1.000 merchants;
- 3.497 registros de comportamento geográfico.

O período transacional cobre 1º de julho a 4 de outubro de 2025.

O motor principal possui 28 regras:

- 16 regras transacionais;
- 12 regras cliente-mês.

Uma regra adicional de geo-salto, denominada `R17`, foi construída posteriormente como enriquecimento contextual e permanece separada do pipeline principal.

O cliente sintético `C101208` foi selecionado para SAR por combinar:

- forte incompatibilidade entre renda e movimentação;
- exposição cross-border;
- país de alto risco;
- hit transacional de sanções;
- recorrência de alertas.

O componente de machine learning deve ser interpretado como baseline experimental de priorização.

A arquitetura multiagente é um protótipo determinístico e sequencial que demonstra separação de etapas e referências de evidência, sem realizar chamadas a provedores externos de LLM.

## 2. Dados e metodologia

A metodologia foi organizada em cinco etapas:

1. Validação da estrutura e qualidade da base.
2. Coerência por rail: PIX, Card e Wire.
3. Regras AML/FT e priorização de suspeitos.
4. Baseline de ML com label fraco.
5. Protótipo de arquitetura multiagente com revisão humana como princípio de desenho.

O princípio central foi aplicar regras explicáveis antes do ML.

Em AML/FT, a priorização precisa ser defensável para:

- investigação;
- auditoria;
- compliance;
- revisão regulatória.

Valores ausentes e outliers não foram removidos ou imputados cegamente. Em dados financeiros, ambos podem representar sinais relevantes ou diferenças estruturais entre rails.

## 3. EDA e qualidade dos dados

A análise inicial não identificou:

- duplicatas relevantes;
- timestamps inválidos;
- valores negativos em `amount_brl`;
- valores zerados em `amount_brl`.

Distribuição por rail:

- PIX: 31.547 transações, correspondendo a 60,67% da base;
- Card: 17.930 transações, correspondendo a 34,48%;
- Wire: 2.523 transações, correspondendo a 4,85%.

Sinais iniciais relevantes:

- 2 transações com sanctions screening hit;
- 9 clientes com sanctions list hit cadastral;
- 80 clientes PEP;
- 196 clientes classificados como KYC high risk;
- 10.113 transações cross-border;
- 4.633 transações Card e-commerce sem 3DS.

A base não possui campo explícito para espécie ou cash físico.

Por isso, transações acima de R$ 50 mil foram tratadas apenas como operações de alto valor, e não como comunicação automática de operação em espécie.

A geolocalização também exige cautela. Diferenças entre país geográfico, IP e contexto transacional podem representar:

- risco real;
- VPN ou proxy;
- uso compartilhado;
- inconsistência operacional;
- ruído da base sintética.

## 4. Sistema de alertas

O motor principal contém 28 regras:

- 16 regras transacionais;
- 12 regras cliente-mês.

O catálogo registra, para cada regra:

- identificador;
- nome;
- lógica;
- parâmetros;
- severidade;
- tipologia;
- rail aplicável;
- exemplo na base;
- justificativa;
- ação operacional;

As regras transacionais cobrem sinais como:

- sanções;
- país de alto risco;
- alto valor;
- e-commerce sem 3DS;
- MCC de risco;
- device e IP risk;
- self-merchant.

As regras cliente-mês cobrem:

- comportamento fora de perfil;
- volume mensal elevado;
- velocity;
- concentração cross-border;
- cash-in e cash-out por proxy comportamental;
- repetição em MCC de risco.

A prioridade final considera:

- combinação de alertas;
- severidade;
- materialidade;
- perfil KYC;
- repetição temporal;
- concentração por país;
- concentração por rail;
- concentração por merchant ou contraparte.

### 4.1 Enriquecimento R17

A `R17` identifica transações consecutivas do mesmo cliente com:

- distância geográfica igual ou superior a 500 km;
- intervalo igual ou inferior a 12 horas.

A regra foi adicionada posteriormente como enriquecimento contextual.

Os candidatos e o catálogo estão versionados, mas sua geração ainda não está integrada ao motor principal de forma reproduzível.

Para `C101208`, foram registrados dois candidatos:

- deslocamento de aproximadamente 7.657 km em 2,696 horas;
- deslocamento de aproximadamente 11.615 km em 1,626 horas.

Nos dois eventos:

- o IP permaneceu no Brasil;
- não houve indicação de IP anômalo;
- não houve indicação de VPN;
- não houve indicação de proxy;
- não houve indicação de Tor;
- não houve indicação de device rooted.

Por isso, a R17 deve ser usada como sinal contextual sujeito à validação da qualidade da geolocalização, nunca como prova isolada ou bloqueio automático.

## 5. Suspeitos e SAR

A T1 gerou rankings das:

- 30 transações mais suspeitas;
- 30 clientes mais suspeitos.

O cliente `C101208` foi selecionado para SAR por apresentar:

- R$ 162.018,32 movimentados;
- 34 transações;
- renda anual declarada de R$ 13.047,00;
- 9 transações cross-border;
- 1 hit de sanctions screening em Wire;
- 1 transação para `receiver_country=SY`;
- alertas mensais recorrentes de comportamento fora de perfil;
- dois candidatos contextuais de geo-salto.

A diferença entre movimentação e renda declarada é material.

O volume transacionado representa mais de doze vezes a renda anual informada.

O SAR foi estruturado com:

- identificação;
- resumo executivo;
- sinais e alertas;
- timeline;
- análise;
- base legal em alto nível;
- conclusão;
- ações recomendadas.

Também foi construído um grafo de entidades em:

- CSV;
- Mermaid;
- JSON;
- PNG.

O grafo conecta:

- cliente;
- transações;
- rails;
- países;
- merchants;
- alertas.

O SAR não afirma a ocorrência de crime.

Ele registra uma suspeita fundamentada para revisão humana e eventual comunicação conforme os procedimentos da instituição.

## 6. Baseline de machine learning

A unidade de modelagem escolhida foi cliente-mês.

Essa granularidade permite capturar padrões acumulados que não aparecem em uma única transação.

O label fraco foi definido como:

`suspicious_label = 1` quando `rule_count >= 3`.

Foi estruturado um pipeline XGBoost para PF com `random_state=42`.

O split temporal foi:

- treino: julho e agosto de 2025;
- validação: setembro e outubro de 2025.

A base de treino possui:

- 4.998 linhas;
- 422 positivos;
- taxa positiva aproximada de 8,44%.

A base de validação possui:

- 4.109 linhas;
- 189 positivos;
- taxa positiva aproximada de 4,60%.

Os artefatos versionados registram:

- AUC-PR: 0,9416;
- AUC-ROC: 0,9970;
- threshold com maior MCC na validação: 0,9;
- precision: 0,9241;
- recall: 0,7725;
- FPR: 0,0031;
- MCC: 0,8382.

### 6.1 Interpretação correta

O desempenho elevado é esperado porque o label fraco deriva de regras construídas sobre variáveis próximas às features usadas pelo modelo.

As colunas de regras e `rule_count` foram excluídas do treino, evitando vazamento direto do rótulo.

Isso não elimina a circularidade conceitual entre as variáveis comportamentais e o label fraco.

Outras limitações relevantes:

- os mesmos clientes podem aparecer em treino e validação;
- a tabela geográfica pode agregar informações de todo o período;
- outubro contém apenas dados até o dia 4;
- a comparação por profissão utiliza o grupo do próprio mês;
- o threshold foi comparado na própria validação;
- não existe conjunto independente para calibragem;
- o label não representa caso confirmado;
- o label não representa SAR aceito;
- o label não representa decisão investigativa final.

O threshold de 0,9 deve ser tratado como referência estatística do experimento, e não como decisão operacional definitiva.

### 6.2 Explicabilidade

Existem artefatos versionados de:

- importância nativa do XGBoost;
- valores SHAP médios absolutos;
- ranking de casos da validação.

Entretanto, o código público atual ainda não contém a geração completa desses artefatos.

Portanto, a explicabilidade está documentada nos outputs, mas sua reprodução integral ainda precisa ser incorporada ao pipeline.

## 7. Protótipo de arquitetura multiagente

A T4 demonstra uma arquitetura sequencial com cinco etapas:

1. Dados.
2. Detecção.
3. Investigação.
4. Reporte.
5. Compliance.

Responsabilidades propostas:

- Dados: ingesta, qualidade, coerência por rail e enriquecimento;
- Detecção: regras, score de ML e fila priorizada;
- Investigação: entidade 360°, timeline e deduplicação;
- Reporte: estruturação de SAR ou ROS;
- Compliance: revisão regulatória, sanções e trilha de auditoria.

O arquivo `src/agents.py` implementa uma simulação determinística dessa sequência.

As etapas recebem contexto estruturado e produzem:

- achados;
- decisões;
- próximas ações;
- referências de evidência.

O protótipo não realiza chamadas a APIs ou provedores externos de LLM.

Os prompts são mantidos como modelos de instrução para uma integração futura.

O objetivo desta etapa é demonstrar:

- separação de responsabilidades;
- passagem controlada de contexto;
- referências de evidência;
- revisão humana como princípio;
- orientação à auditabilidade;
- desenho seguro para ambiente regulado.

Não se trata de:

- agente autônomo;
- automação produtiva;
- sistema capaz de emitir comunicação regulatória sem revisão;
- decisão automática de compliance.

## 8. Limitações e próximos passos

Principais limitações:

- base integralmente sintética;
- ausência de label investigativo final;
- ausência de campo explícito de espécie;
- geolocalização sujeita a ruído;
- R17 separada do motor principal;
- notebooks ainda sem execução versionada;
- caminhos antigos em parte do código;
- geração integral dos outputs de ML ainda não consolidada;
- ausência de calibragem com feedback operacional;
- ausência de modelo PJ separado;
- protótipo multiagente sem integração ativa com LLM.

Próximos passos técnicos:

1. Corrigir caminhos e contratos de execução.
2. Integrar a R17 ao motor principal.
3. Executar os notebooks ponta a ponta.
4. Versionar a geração de métricas, thresholds, SHAP e gráficos.
5. Avaliar leakage temporal e sobreposição de entidades.
6. Separar treino, calibragem e teste.
7. Calibrar thresholds por capacidade operacional e risco.
8. Evoluir modelos PF e PJ conforme disponibilidade cadastral.
9. Monitorar drift, estabilidade e falsos positivos.
10. Integrar listas externas apenas em ambiente controlado.
11. Conectar a arquitetura de agentes a um provedor de LLM somente com guardrails, logs e aprovação humana.

## 9. Base regulatória em alto nível

A Circular BCB nº 3.978/2020 estabelece política, procedimentos e controles internos de prevenção à lavagem de dinheiro e ao financiamento do terrorismo para instituições autorizadas pelo Banco Central.

A Carta Circular BCB nº 4.001/2020 divulga operações e situações que podem configurar indícios de lavagem de dinheiro ou financiamento do terrorismo.

A Lei nº 9.613/1998 constitui a principal base legal brasileira sobre lavagem ou ocultação de bens, direitos e valores e institui o COAF.

As Recomendações FATF/GAFI formam o padrão internacional de AML/CFT.

## 10. Conclusão

O case demonstra uma arquitetura analítica coerente para Financial Crime:

- qualidade e coerência dos dados;
- regras explicáveis;
- priorização de suspeitos;
- investigação estruturada;
- SAR;
- baseline de ML;
- desenho controlado de agentes de IA.

Seu principal valor está na integração entre:

- raciocínio investigativo;
- dados;
- regras;
- modelagem;
- governança.

Os resultados devem ser interpretados como evidência técnica de um case sintético e experimental.

Eles não devem ser interpretados como:

- solução pronta para produção;
- decisão automática;
- comunicação regulatória final;
- comprovação de atividade ilícita.

## Referências

- Banco Central do Brasil. Circular nº 3.978/2020: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=3978&tipo=Circular
- Banco Central do Brasil. Carta Circular nº 4.001/2020: https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50911/C_Circ_4001_v2_P.pdf
- Presidência da República. Lei nº 9.613/1998: https://www.planalto.gov.br/ccivil_03/leis/l9613.htm
- FATF/GAFI. FATF Recommendations: https://www.fatf-gafi.org/en/topics/fatf-recommendations.html
