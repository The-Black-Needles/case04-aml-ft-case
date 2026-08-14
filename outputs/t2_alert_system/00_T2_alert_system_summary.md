# T2 — Sistema de Alertas AML/FT

## Objetivo

Esta etapa transforma os achados da EDA e da T1 em um sistema de alertas explicável, auditável e operacional.

A premissa é: **regras primeiro, ML depois**. As regras dão rastreabilidade para o analista, servem de base para priorização e também serão usadas depois como label fraco para o modelo de ML.

## Estrutura do sistema

O sistema tem dois níveis de alerta:

1. **Regras transacionais**
   - Avaliam uma transação individual.
   - São úteis para eventos críticos ou pontuais, como sanções, país de alto risco, alto valor, e-commerce sem 3DS, device/IP risk e self-merchant.

2. **Regras cliente-mês**
   - Avaliam comportamento agregado por cliente em uma janela mensal.
   - São úteis para fora de perfil, velocity, structuring, cash-in para cash-out, concentração cross-border e repetição de sinais técnicos.

## Quantidade de regras

Foram formalizadas **28 regras**:

- **16 regras transacionais**
- **12 regras cliente-mês**

Isso atende ao requisito de no mínimo 15 regras e mantém cobertura sobre as principais tipologias do case.

A R17 de geo-salto é um enriquecimento suplementar e permanece fora das 28 regras do motor principal e do backtesting principal enquanto não estiver integrada ao pipeline de forma reproduzível.

## Tipologias cobertas

As regras cobrem:

- Sanções e FT
- PEP e diligência reforçada
- Cross-border e países de alto risco
- Fora de perfil por renda/risco
- Velocity e conta de passagem
- Structuring/smurfing proxy
- MCC e merchant risk
- E-commerce sem 3DS
- Device/IP risk e geo-salto
- Self-merchant/circularidade

## Lógica de priorização

Cada regra possui pontuação. Alertas críticos, como sanções e self-merchant, recebem peso maior. Alertas de contexto, como MCC de risco ou device rooted, recebem peso menor e ganham importância quando aparecem combinados com outros sinais.

A prioridade final não depende de um único gatilho. Ela considera:

- Quantidade de regras disparadas
- Severidade dos sinais
- Materialidade financeira
- Perfil cadastral/KYC
- Repetição no tempo
- Concentração por rail, país, merchant ou contraparte

## Limiares dinâmicos

Alguns limiares são fixos por simplicidade operacional, mas os principais alertas comportamentais usam ou admitem limiar dinâmico.

O principal exemplo é a regra de movimentação mensal fora de perfil:

- Risco baixo: movimentação mensal >= 2x renda mensal estimada
- Risco médio: movimentação mensal >= 1,5x renda mensal estimada
- Risco alto: movimentação mensal >= 1x renda mensal estimada
- Piso operacional usado no protótipo: R$20.000 para PF

Essa abordagem evita tratar todos os clientes iguais e segue o princípio de abordagem baseada em risco.

## Limitações

A base não possui campo explícito de espécie/cash físico. Por isso, a regra de alto valor >= R$50 mil foi tratada como alerta de materialidade, não como comunicação automática de operação em espécie.

A base também não favorece device/IP ring por reutilização exata, porque os fingerprints e IPs são majoritariamente únicos. Por isso, o sistema usa sinais de risco técnico como `device_rooted`, `ip_anomaly`, `Proxy`, `VPN` e `Tor`.

## Backtesting descritivo reproduzível

O motor principal agora possui um runner dedicado que regenera métricas de hits, cobertura por rail, carga operacional, distribuição do número de acionamentos e coocorrência entre regras.

Na base sintética atual:

- 28.204 de 52.000 transações acionam ao menos uma regra transacional;
- 5.832 de 9.107 registros cliente-mês acionam ao menos uma regra mensal;
- 120 pares de regras transacionais e 66 pares cliente-mês são avaliados por coocorrência;
- 8 pares em cada nível aparecem como candidatos empíricos para revisão humana pelos critérios atuais.

Esses números medem comportamento do motor sobre a base sintética. Não existe ground truth investigativo independente e, portanto, o backtesting não estima precision, recall, falsos positivos ou falsos negativos das regras. `status` é usado apenas para segmentação descritiva e não como validação externa.

O resumo completo está em `17_backtesting_summary.md` e o contrato reproduzível em `18_backtesting_manifest.json`.

## Resultado

O sistema gera uma fila AML priorizada e defensável, permitindo explicar por que uma transação ou cliente entrou na fila de investigação. A calibragem operacional continua dependente de revisão humana, capacidade de fila e feedback investigativo.
