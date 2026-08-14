from __future__ import annotations

import json
from pathlib import Path
from typing import Final

import pandas as pd

from src import rule_backtesting
from src import rules


DEFAULT_OUTPUT_DIR: Final = Path(
    "outputs/t2_alert_system"
)

TABLE_OUTPUTS: Final = (
    (
        "rule_hits_transaction",
        "06_backtesting_rule_hits_transaction.csv",
    ),
    (
        "rule_hits_customer_month",
        "07_backtesting_rule_hits_customer_month.csv",
    ),
    (
        "rule_rail_transaction",
        "08_backtesting_rule_rail_transaction.csv",
    ),
    (
        "rule_rail_presence_customer_month",
        "09_backtesting_rule_rail_presence_customer_month.csv",
    ),
    (
        "alert_load",
        "10_backtesting_alert_load.csv",
    ),
    (
        "rule_count_distribution_transaction",
        "11_backtesting_rule_count_distribution_transaction.csv",
    ),
    (
        "rule_count_distribution_customer_month",
        "12_backtesting_rule_count_distribution_customer_month.csv",
    ),
    (
        "transaction_load_by_status",
        "13_backtesting_transaction_load_by_status.csv",
    ),
    (
        "transaction_load_by_rail",
        "14_backtesting_transaction_load_by_rail.csv",
    ),
    (
        "pairwise_review_transaction",
        "15_backtesting_pairwise_review_transaction.csv",
    ),
    (
        "pairwise_review_customer_month",
        "16_backtesting_pairwise_review_customer_month.csv",
    ),
)

SUMMARY_FILENAME: Final = (
    "17_backtesting_summary.md"
)

MANIFEST_FILENAME: Final = (
    "18_backtesting_manifest.json"
)


def load_principal_rule_frames(
) -> tuple[
    pd.DataFrame,
    tuple[str, ...],
    pd.DataFrame,
    tuple[str, ...],
]:
    """Carrega somente o motor principal reproduzível R01-R16/M01-M12."""

    dfs = rules.load_data()

    tx, kyc, merchants, geobehavior = rules.prep(
        dfs
    )

    tx_rules, tx_catalog = rules.add_rules(
        tx
    )

    involvement = rules.build_inv(
        tx_rules
    )

    month_rules, month_catalog = rules.month_alerts(
        involvement,
        kyc,
    )

    tx_rule_columns = tuple(
        tx_catalog[
            "rule_name"
        ]
    )

    month_rule_columns = tuple(
        month_catalog[
            "rule_name"
        ]
    )

    if len(tx_rule_columns) != 16:
        raise RuntimeError(
            "Motor transacional principal deve conter 16 regras."
        )

    if len(month_rule_columns) != 12:
        raise RuntimeError(
            "Motor cliente-mês principal deve conter 12 regras."
        )

    identifiers = {
        rule_name.split(
            "_",
            1,
        )[0]
        for rule_name in (
            tx_rule_columns
            + month_rule_columns
        )
    }

    if "R17" in identifiers:
        raise RuntimeError(
            "R17 não pode entrar no backtesting principal."
        )

    return (
        tx_rules,
        tx_rule_columns,
        month_rules,
        month_rule_columns,
    )


def build_backtesting_tables(
    tx_rules: pd.DataFrame,
    tx_rule_columns: tuple[str, ...],
    month_rules: pd.DataFrame,
    month_rule_columns: tuple[str, ...],
) -> dict[str, pd.DataFrame]:
    """Constrói tabelas descritivas sem inferir ground truth."""

    return {
        "rule_hits_transaction": (
            rule_backtesting.rule_hit_summary(
                tx_rules,
                tx_rule_columns,
                level="transaction",
            )
        ),
        "rule_hits_customer_month": (
            rule_backtesting.rule_hit_summary(
                month_rules,
                month_rule_columns,
                level="customer_month",
            )
        ),
        "rule_rail_transaction": (
            rule_backtesting.transaction_rule_rail_summary(
                tx_rules,
                tx_rule_columns,
            )
        ),
        "rule_rail_presence_customer_month": (
            rule_backtesting
            .customer_month_rule_rail_presence_summary(
                month_rules,
                month_rule_columns,
            )
        ),
        "alert_load": pd.concat(
            [
                rule_backtesting.alert_load_summary(
                    tx_rules,
                    tx_rule_columns,
                    level="transaction",
                ),
                rule_backtesting.alert_load_summary(
                    month_rules,
                    month_rule_columns,
                    level="customer_month",
                ),
            ],
            ignore_index=True,
        ),
        "rule_count_distribution_transaction": (
            rule_backtesting.rule_count_distribution(
                tx_rules,
                tx_rule_columns,
                level="transaction",
            )
        ),
        "rule_count_distribution_customer_month": (
            rule_backtesting.rule_count_distribution(
                month_rules,
                month_rule_columns,
                level="customer_month",
            )
        ),
        "transaction_load_by_status": (
            rule_backtesting.transaction_alert_load_by_status(
                tx_rules,
                tx_rule_columns,
            )
        ),
        "transaction_load_by_rail": (
            rule_backtesting.transaction_alert_load_by_rail(
                tx_rules,
                tx_rule_columns,
            )
        ),
        "pairwise_review_transaction": (
            rule_backtesting.pairwise_rule_review_evidence(
                tx_rules,
                tx_rule_columns,
                level="transaction",
            )
        ),
        "pairwise_review_customer_month": (
            rule_backtesting.pairwise_rule_review_evidence(
                month_rules,
                month_rule_columns,
                level="customer_month",
            )
        ),
    }


def _level_row(
    table: pd.DataFrame,
    level: str,
) -> pd.Series:
    selected = table[
        table[
            "level"
        ].eq(
            level
        )
    ]

    if len(selected) != 1:
        raise RuntimeError(
            f"Carga inesperada para level={level}."
        )

    return selected.iloc[0]


def _pair_row(
    table: pd.DataFrame,
    rule_a: str,
    rule_b: str,
) -> pd.Series:
    selected = table[
        table[
            "rule_a_id"
        ].eq(
            rule_a
        )
        & table[
            "rule_b_id"
        ].eq(
            rule_b
        )
    ]

    if len(selected) != 1:
        raise RuntimeError(
            f"Par inesperado: {rule_a}/{rule_b}."
        )

    return selected.iloc[0]


def _percent(
    value: float,
) -> str:
    return (
        f"{value:.2%}"
        .replace(
            ".",
            ",",
        )
    )


def build_summary_markdown(
    tables: dict[str, pd.DataFrame],
) -> str:
    """Gera resumo público preservando os limites experimentais."""

    alert_load = tables[
        "alert_load"
    ]

    tx_load = _level_row(
        alert_load,
        "transaction",
    )

    month_load = _level_row(
        alert_load,
        "customer_month",
    )

    rail_load = (
        tables[
            "transaction_load_by_rail"
        ]
        .set_index(
            "segment_value"
        )
    )

    tx_review = tables[
        "pairwise_review_transaction"
    ]

    month_review = tables[
        "pairwise_review_customer_month"
    ]

    r10_r11 = _pair_row(
        tx_review,
        "R10",
        "R11",
    )

    tx_candidates = int(
        tx_review[
            "review_required"
        ].sum()
    )

    month_candidates = int(
        month_review[
            "review_required"
        ].sum()
    )

    lines = [
        "# T2 — Backtesting descritivo reproduzível",
        "",
        "## Objetivo",
        "",
        (
            "Este conjunto de artefatos mede cobertura, concentração, "
            "carga operacional e sobreposição do motor principal de regras "
            "sobre a base sintética do case."
        ),
        "",
        (
            "O backtesting é descritivo e experimental. Ele não constitui "
            "homologação produtiva e não usa um ground truth independente."
        ),
        "",
        "## Escopo",
        "",
        "- 16 regras transacionais: R01–R16.",
        "- 12 regras cliente-mês: M01–M12.",
        "- 28 regras no motor principal.",
        (
            "- R17 permanece como enriquecimento suplementar de geo-salto "
            "e está fora deste backtesting principal."
        ),
        "- Base integralmente sintética.",
        "",
        "## Carga operacional observada",
        "",
        (
            f"- Transações alertadas: "
            f"{int(tx_load['alerted_observations']):,}/"
            f"{int(tx_load['observations']):,} "
            f"({_percent(float(tx_load['alert_rate']))})."
        ),
        (
            f"- Cliente-mês alertados: "
            f"{int(month_load['alerted_observations']):,}/"
            f"{int(month_load['observations']):,} "
            f"({_percent(float(month_load['alert_rate']))})."
        ),
        (
            f"- Total de hits transacionais: "
            f"{int(tx_load['total_rule_hits']):,}."
        ),
        (
            f"- Total de hits cliente-mês: "
            f"{int(month_load['total_rule_hits']):,}."
        ),
        "",
        "## Segmentação transacional por rail",
        "",
        (
            f"- PIX: {int(rail_load.loc['PIX', 'alerted_observations']):,}/"
            f"{int(rail_load.loc['PIX', 'observations']):,} "
            f"({_percent(float(rail_load.loc['PIX', 'alert_rate']))})."
        ),
        (
            f"- Card: {int(rail_load.loc['Card', 'alerted_observations']):,}/"
            f"{int(rail_load.loc['Card', 'observations']):,} "
            f"({_percent(float(rail_load.loc['Card', 'alert_rate']))})."
        ),
        (
            f"- Wire: {int(rail_load.loc['Wire', 'alerted_observations']):,}/"
            f"{int(rail_load.loc['Wire', 'observations']):,} "
            f"({_percent(float(rail_load.loc['Wire', 'alert_rate']))})."
        ),
        "",
        (
            "Na unidade cliente-mês, a presença de rail é não exclusiva: "
            "um mesmo cliente-mês pode conter PIX, Card e Wire."
        ),
        "",
        "## Status transacional",
        "",
        (
            "A segmentação por `status` é apenas descritiva. `status` não é "
            "tratado como ground truth de fraude ou lavagem."
        ),
        "",
        (
            "Em particular, Chargeback participa diretamente da lógica da R09. "
            "Por isso, a concentração de alertas nesse status é circular e não "
            "pode ser apresentada como evidência independente de precisão."
        ),
        "",
        "## Sobreposição e revisão humana",
        "",
        (
            f"- Pares transacionais sinalizados para revisão: "
            f"{tx_candidates}/{len(tx_review)}."
        ),
        (
            f"- Pares cliente-mês sinalizados para revisão: "
            f"{month_candidates}/{len(month_review)}."
        ),
        (
            f"- R10/R11: Jaccard empírico "
            f"{float(r10_r11['jaccard']):.6f}, com "
            f"{int(r10_r11['both_hits']):,} acionamentos conjuntos."
        ),
        (
            "- Containment observado na base é evidência empírica para revisão, "
            "não prova de equivalência lógica entre regras."
        ),
        "",
        (
            "Nenhuma regra é desativada automaticamente. Redundância, conflito, "
            "ajuste de threshold e ação operacional exigem análise humana."
        ),
        "",
        "## O que este backtesting não mede",
        "",
        (
            "- Não calcula precision, recall, FPR, FNR, falsos positivos ou "
            "falsos negativos das regras, porque não existe label investigativo "
            "independente."
        ),
        (
            "- Não transforma sanções, chargeback ou qualquer outro campo usado "
            "pela própria regra em validação externa."
        ),
        "- Não representa homologação em ambiente produtivo.",
        "- Não afirma ocorrência de crime.",
        "",
        "## Uso pretendido",
        "",
        (
            "Os artefatos servem para tornar o motor auditável, comparar carga "
            "por rail, localizar concentração de alertas, identificar pares de "
            "regras que merecem revisão e apoiar uma futura calibragem com "
            "feedback investigativo e capacidade operacional."
        ),
        "",
        (
            "A decisão final permanece supervisionada por humanos."
        ),
        "",
    ]

    return "\n".join(
        lines
    )


def build_manifest(
    tables: dict[str, pd.DataFrame],
) -> dict[str, object]:
    alert_load = tables[
        "alert_load"
    ]

    tx_load = _level_row(
        alert_load,
        "transaction",
    )

    month_load = _level_row(
        alert_load,
        "customer_month",
    )

    tx_review = tables[
        "pairwise_review_transaction"
    ]

    month_review = tables[
        "pairwise_review_customer_month"
    ]

    return {
        "artifact": "t2_rule_backtesting",
        "artifact_version": "1.0",
        "dataset": "synthetic",
        "analysis_type": "descriptive_experimental",
        "principal_rule_engine": {
            "transaction_rules": 16,
            "customer_month_rules": 12,
            "total_rules": 28,
            "r17_in_principal_backtest": False,
        },
        "operational_load": {
            "transaction_observations": int(
                tx_load[
                    "observations"
                ]
            ),
            "transaction_alerted": int(
                tx_load[
                    "alerted_observations"
                ]
            ),
            "customer_month_observations": int(
                month_load[
                    "observations"
                ]
            ),
            "customer_month_alerted": int(
                month_load[
                    "alerted_observations"
                ]
            ),
        },
        "review_evidence": {
            "transaction_pairs": len(
                tx_review
            ),
            "transaction_candidates": int(
                tx_review[
                    "review_required"
                ].sum()
            ),
            "customer_month_pairs": len(
                month_review
            ),
            "customer_month_candidates": int(
                month_review[
                    "review_required"
                ].sum()
            ),
            "automatic_redundancy_verdict": False,
            "automatic_rule_disable": False,
        },
        "limitations": {
            "independent_ground_truth": False,
            "status_is_ground_truth": False,
            "rule_fp_fn_metrics_available": False,
            "production_homologation": False,
            "human_review_required": True,
        },
        "tables": {
            filename: {
                "key": key,
                "rows": len(
                    tables[
                        key
                    ]
                ),
            }
            for (
                key,
                filename,
            ) in TABLE_OUTPUTS
        },
    }


def write_backtesting_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    tables: dict[str, pd.DataFrame] | None = None,
) -> tuple[Path, ...]:
    if tables is None:
        (
            tx_rules,
            tx_rule_columns,
            month_rules,
            month_rule_columns,
        ) = load_principal_rule_frames()

        tables = build_backtesting_tables(
            tx_rules,
            tx_rule_columns,
            month_rules,
            month_rule_columns,
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    written: list[Path] = []

    for (
        key,
        filename,
    ) in TABLE_OUTPUTS:
        path = output_dir / filename

        tables[
            key
        ].to_csv(
            path,
            index=False,
            encoding="utf-8",
            lineterminator="\n",
            float_format="%.12g",
        )

        written.append(
            path
        )

    summary_path = (
        output_dir
        / SUMMARY_FILENAME
    )

    summary_path.write_text(
        build_summary_markdown(
            tables
        ),
        encoding="utf-8",
    )

    written.append(
        summary_path
    )

    manifest_path = (
        output_dir
        / MANIFEST_FILENAME
    )

    manifest_path.write_text(
        json.dumps(
            build_manifest(
                tables
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    written.append(
        manifest_path
    )

    return tuple(
        written
    )


def main() -> None:
    written = write_backtesting_outputs()

    print(
        f"T2_BACKTESTING_OUTPUTS={len(written)}"
    )

    for path in written:
        print(
            f"OUTPUT={path}"
        )


if __name__ == "__main__":
    main()
