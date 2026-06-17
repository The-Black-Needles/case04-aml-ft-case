# Checklist final do case AML/FT

## Estrutura do repositório

- [x] `data/raw/` com base original versionada via Git LFS.
- [x] `outputs/eda_day1/` com EDA inicial.
- [x] `outputs/t1_suspects/` com suspeitos e SAR.
- [x] `outputs/t2_alert_system/` com catálogo de regras.
- [x] `outputs/t3_ml/` com métricas, features e explicabilidade.
- [x] `outputs/t4_agents/` com prompts, workflow e diagrama.
- [x] `src/` com scripts principais.
- [x] `notebooks/` com notebooks 01 a 04.
- [x] `docs/` com explicação por etapa.
- [x] `reports/` com relatório final.
- [x] `presentation/` com roteiro final.

## Validações principais

- [x] Base lida com sucesso.
- [x] Coerência por rail validada.
- [x] Regras AML implementadas e documentadas.
- [x] Top 30 transações suspeitas gerado.
- [x] Top 30 clientes suspeitos gerado.
- [x] SAR draft estruturado.
- [x] Label fraco definido por regra.
- [x] Modelo com split temporal.
- [x] Métricas e thresholds gerados.
- [x] Multi-agente implementado como script sequencial.
- [x] Roteiro de apresentação criado.

## Revisão antes de apresentar

- [ ] Rodar `git status` e garantir working tree clean.
- [ ] Confirmar push no GitHub.
- [ ] Abrir PDF final.
- [ ] Treinar apresentação usando `presentation/roteiro_final_30_40_min.md`.
- [ ] Ensaiar explicação do SAR C101208.
- [ ] Ensaiar ressalva sobre ML: baseline de priorização, não decisão automática.
