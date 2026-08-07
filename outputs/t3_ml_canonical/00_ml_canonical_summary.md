# T3 — Machine Learning canônico

Baseline experimental cliente-mês com XGBoost explicável.

## Contrato

- Base: sintética.
- Label: fraco e derivado das regras determinísticas M01–M12.
- R17: fora do label canônico.
- Treino: julho/2025.
- Calibragem: agosto/2025.
- Teste temporal: setembro/2025.
- Outubro/2025: excluído por mês incompleto.
- `random_state=42`.
- Revisão humana: obrigatória.
- Validação produtiva: não alegada.

## Entrada

- Arquivo: `outputs/t1_suspects/04_client_month_alerts_all.csv`.
- SHA-256: `aadcac57102fff0052ac41ecd0372fad9e64d7009fc85e38e8a069ec79d6e3b8`.
- Registros canônicos: 7496.
- Features primárias: 5 categóricas + 16 numéricas.

## Splits

- train: 2025-07; 2499 registros; 236 positivos; prevalência 0.0944.
- calibration: 2025-08; 2499 registros; 254 positivos; prevalência 0.1016.
- test: 2025-09; 2498 registros; 220 positivos; prevalência 0.0881.

## Threshold

- Threshold estatístico selecionado na calibragem: 0.3.
- Regra de seleção: `max_mcc_statistical_baseline`.
- Restrições operacionais explícitas: não aplicadas.
- Homologação operacional: não.
- O threshold é baseline estatístico e não deve ser interpretado como threshold de produção.

## Teste temporal

- AUC-PR: 0.3167.
- AUC-ROC: 0.8269.
- Precision: 0.2096.
- Recall: 0.7773.
- FPR: 0.2831.
- MCC: 0.2986.
- Alertas no threshold estatístico: 816 de 2498.

## Limitações de interpretação

- As métricas medem a capacidade de aproximar um label fraco, não de provar ilícito ou validar produção.
- Há circularidade conceitual porque o label deriva de regras determinísticas e algumas features representam conceitos correlatos.
- O split é temporal, mas as mesmas entidades aparecem em meses sucessivos; a independência entre clientes não é garantida.
- SHAP e feature importance são explicabilidade pós-hoc e não participam da seleção do threshold.
- Capacidade da fila, custo de falsos positivos e negativos, calibragem e drift ainda precisam de homologação antes de qualquer uso operacional.
