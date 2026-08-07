"""Gráficos reproduzíveis do experimento canônico de Machine Learning.

Este módulo consome exclusivamente artefatos tabulares já gerados pelo
pipeline canônico. Ele não treina modelos, não escolhe thresholds e não
altera outputs legados.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Final

import matplotlib

matplotlib.use(
    "Agg",
    force=True,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_INPUT_DIR: Final = Path(
    "outputs/t3_ml_canonical"
)

DEFAULT_OUTPUT_DIR: Final = Path(
    "outputs/t3_ml_canonical"
)

CANONICAL_BASE_FILENAMES: Final = (
    "00_ml_canonical_summary.md",
    "01_canonical_model_dataset.csv",
    "02_split_distribution.csv",
    "03_metrics_summary.csv",
    "04_threshold_metrics_calibration.csv",
    "05_feature_importance_gain.csv",
    "06_shap_summary_test.csv",
    "07_test_scored_top30.csv",
    "08_run_manifest.json",
)

INPUT_FILENAMES: Final = (
    "02_split_distribution.csv",
    "03_metrics_summary.csv",
    "04_threshold_metrics_calibration.csv",
    "05_feature_importance_gain.csv",
    "06_shap_summary_test.csv",
)

CHART_FILENAMES: Final = (
    "09_chart_01_prevalencia_splits.png",
    "10_chart_02_tradeoff_thresholds_calibracao.png",
    "11_chart_03_metricas_calibracao_teste.png",
    "12_chart_04_importancia_features_gain.png",
    "13_chart_05_shap_top_features.png",
)

MANIFEST_FILENAME: Final = (
    "14_charts_manifest.json"
)

ALL_OUTPUT_FILENAMES: Final = (
    *CHART_FILENAMES,
    MANIFEST_FILENAME,
)

PNG_DPI: Final = 160
TOP_FEATURES: Final = 12

SPLIT_LABELS: Final = {
    "train": "Treino",
    "calibration": "Calibragem",
    "test": "Teste",
}

FEATURE_LABELS: Final = {
    "numeric__confirmed_count":
        "Transações confirmadas",
    "numeric__zscore_vs_peer_total":
        "Z-score do total vs. pares",
    "numeric__ratio_to_peer_median_total":
        "Razão do total vs. mediana dos pares",
    "numeric__avg_amount":
        "Valor médio",
    "numeric__max_amount":
        "Valor máximo",
    "numeric__card_count":
        "Quantidade de Card",
    "numeric__pix_count":
        "Quantidade de PIX",
    "numeric__wire_count":
        "Quantidade de Wire",
    "numeric__annual_income_brl":
        "Renda anual declarada",
    "numeric__kyc_risk_score":
        "Score de risco KYC",
    "numeric__months_since_registration":
        "Meses desde o cadastro",
    "numeric__peer_group_size":
        "Tamanho do grupo de pares",
    "numeric__peer_total_amount_median":
        "Mediana do total dos pares",
    "numeric__peer_total_amount_mean":
        "Média do total dos pares",
    "numeric__peer_total_amount_std":
        "Desvio-padrão do total dos pares",
    "numeric__age":
        "Idade",
    "categorical__state_RS":
        "Estado: RS",
    "categorical__declared_occupation_Dentist":
        "Profissão: Dentista",
    "categorical__declared_occupation_Lawyer":
        "Profissão: Advogado",
    "categorical__declared_occupation_Software Engineer":
        "Profissão: Engenheiro de software",
    "categorical__declared_occupation_Driver":
        "Profissão: Motorista",
    "categorical__kyc_tier_L2":
        "Nível KYC: L2",
    "categorical__kyc_tier_L3":
        "Nível KYC: L3",
}

METRIC_LABELS: Final = {
    "auc_pr": "AUC-PR",
    "auc_roc": "AUC-ROC",
    "precision": "Precisão",
    "recall": "Sensibilidade",
    "fpr": "FPR",
    "mcc": "MCC",
}


def sha256_file(
    path: Path,
) -> str:
    """Return the SHA-256 digest of one file."""
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as stream:
        for chunk in iter(
            lambda: stream.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def feature_label(
    feature: str,
) -> str:
    """Return a public Portuguese label for a transformed feature."""
    if feature in FEATURE_LABELS:
        return FEATURE_LABELS[
            feature
        ]

    label = feature

    for prefix in (
        "numeric__",
        "categorical__",
    ):
        if label.startswith(
            prefix
        ):
            label = label[
                len(
                    prefix
                ):
            ]
            break

    return label.replace(
        "_",
        " ",
    )


def _validate_inputs(
    input_dir: Path,
) -> dict[str, Path]:
    paths = {
        filename:
            input_dir
            / filename
        for filename in INPUT_FILENAMES
    }

    missing = [
        str(path)
        for path in paths.values()
        if not path.is_file()
    ]

    if missing:
        raise FileNotFoundError(
            "Artefatos canônicos ausentes: "
            + ", ".join(
                missing
            )
        )

    return paths


def _prepare_outputs(
    output_dir: Path,
    *,
    overwrite: bool,
    allow_canonical_base: bool,
) -> dict[str, Path]:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = {
        filename:
            output_dir
            / filename
        for filename in ALL_OUTPUT_FILENAMES
    }

    allowed_existing_names = set(
        ALL_OUTPUT_FILENAMES
    )

    if allow_canonical_base:
        allowed_existing_names.update(
            CANONICAL_BASE_FILENAMES
        )

    entries = list(
        output_dir.iterdir()
    )

    unknown_entries = [
        entry
        for entry in entries
        if entry.name
        not in allowed_existing_names
    ]

    if unknown_entries:
        raise RuntimeError(
            "Diretório de saída contém entradas "
            "desconhecidas; nenhuma escrita realizada: "
            + ", ".join(
                str(
                    entry
                )
                for entry in sorted(
                    unknown_entries,
                    key=lambda value: value.name,
                )
            )
        )

    for entry in entries:
        if (
            entry.is_symlink()
            or not entry.is_file()
        ):
            raise RuntimeError(
                "Entrada permitida não é arquivo regular: "
                f"{entry}"
            )

    existing_outputs = [
        str(
            path
        )
        for path in paths.values()
        if path.exists()
    ]

    if (
        existing_outputs
        and not overwrite
    ):
        raise FileExistsError(
            "Artefatos gráficos já existem; "
            "use --overwrite somente após revisão: "
            + ", ".join(
                existing_outputs
            )
        )

    return paths


def _save_figure(
    figure: plt.Figure,
    path: Path,
) -> None:
    figure.savefig(
        path,
        dpi=PNG_DPI,
        format="png",
        metadata={
            "Software":
                "case04-canonical-ml-charts",
        },
    )

    plt.close(
        figure
    )


def _validate_split_table(
    frame: pd.DataFrame,
) -> None:
    required = {
        "split",
        "month",
        "rows",
        "positives",
        "negatives",
        "prevalence",
    }

    missing = sorted(
        required
        - set(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes na distribuição por split: "
            + ", ".join(
                missing
            )
        )

    if set(
        frame[
            "split"
        ]
    ) != {
        "train",
        "calibration",
        "test",
    }:
        raise ValueError(
            "Splits canônicos inesperados"
        )


def _validate_threshold_table(
    frame: pd.DataFrame,
) -> float:
    required = {
        "threshold",
        "precision",
        "recall",
        "fpr",
        "mcc",
        "alert_rate",
        "selected_statistical_baseline",
        "operationally_homologated",
    }

    missing = sorted(
        required
        - set(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes na tabela de thresholds: "
            + ", ".join(
                missing
            )
        )

    selected = frame.loc[
        frame[
            "selected_statistical_baseline"
        ].astype(
            bool
        )
    ]

    if len(
        selected
    ) != 1:
        raise ValueError(
            "Threshold estatístico deve ser único"
        )

    if not frame[
        "operationally_homologated"
    ].eq(
        False
    ).all():
        raise ValueError(
            "Threshold não pode estar homologado operacionalmente"
        )

    return float(
        selected[
            "threshold"
        ].iloc[
            0
        ]
    )


def _validate_metrics(
    frame: pd.DataFrame,
) -> None:
    required = {
        "split",
        *METRIC_LABELS.keys(),
        "operationally_homologated",
    }

    missing = sorted(
        required
        - set(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes na tabela de métricas: "
            + ", ".join(
                missing
            )
        )

    if set(
        frame[
            "split"
        ]
    ) != {
        "calibration",
        "test",
    }:
        raise ValueError(
            "Métricas devem conter calibragem e teste"
        )

    if not frame[
        "operationally_homologated"
    ].eq(
        False
    ).all():
        raise ValueError(
            "Métricas não podem alegar homologação operacional"
        )


def _validate_importance(
    frame: pd.DataFrame,
) -> None:
    required = {
        "feature",
        "importance_type",
        "importance",
    }

    missing = sorted(
        required
        - set(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes em feature importance: "
            + ", ".join(
                missing
            )
        )

    if not frame[
        "importance_type"
    ].eq(
        "gain"
    ).all():
        raise ValueError(
            "Feature importance deve usar gain"
        )


def _validate_shap(
    frame: pd.DataFrame,
) -> None:
    required = {
        "feature",
        "mean_abs_shap",
        "mean_shap",
        "split",
        "rows_explained",
    }

    missing = sorted(
        required
        - set(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes no resumo SHAP: "
            + ", ".join(
                missing
            )
        )

    if not frame[
        "split"
    ].eq(
        "test"
    ).all():
        raise ValueError(
            "SHAP deve usar exclusivamente o teste temporal"
        )

    if not frame[
        "rows_explained"
    ].eq(
        2498
    ).all():
        raise ValueError(
            "SHAP deve explicar 2.498 registros de teste"
        )


def _plot_split_prevalence(
    frame: pd.DataFrame,
    output_path: Path,
) -> None:
    order = [
        "train",
        "calibration",
        "test",
    ]

    indexed = frame.set_index(
        "split"
    ).loc[
        order
    ]

    labels = [
        SPLIT_LABELS[
            split
        ]
        for split in order
    ]

    values = (
        indexed[
            "prevalence"
        ].to_numpy(
            dtype=float
        )
        * 100.0
    )

    figure, axis = plt.subplots(
        figsize=(
            8,
            5,
        )
    )

    bars = axis.bar(
        labels,
        values,
    )

    axis.set_title(
        "Prevalência do label fraco por partição temporal"
    )
    axis.set_xlabel(
        "Partição"
    )
    axis.set_ylabel(
        "Prevalência (%)"
    )
    axis.set_ylim(
        0,
        max(
            values
        )
        * 1.25,
    )

    for bar, value in zip(
        bars,
        values,
        strict=True,
    ):
        axis.text(
            bar.get_x()
            + bar.get_width()
            / 2,
            bar.get_height(),
            f"{value:.1f}%",
            ha="center",
            va="bottom",
        )

    figure.tight_layout()

    _save_figure(
        figure,
        output_path,
    )


def _plot_threshold_tradeoff(
    frame: pd.DataFrame,
    selected_threshold: float,
    output_path: Path,
) -> None:
    figure, axis = plt.subplots(
        figsize=(
            8,
            5,
        )
    )

    series = (
        (
            "precision",
            "Precisão",
        ),
        (
            "recall",
            "Sensibilidade",
        ),
        (
            "fpr",
            "FPR",
        ),
        (
            "mcc",
            "MCC",
        ),
        (
            "alert_rate",
            "Taxa de alertas",
        ),
    )

    for column, label in series:
        axis.plot(
            frame[
                "threshold"
            ],
            frame[
                column
            ],
            marker="o",
            label=label,
        )

    axis.axvline(
        selected_threshold,
        linestyle="--",
        linewidth=1.4,
        label=(
            "Threshold estatístico "
            f"= {selected_threshold:.1f}"
        ),
    )

    axis.set_title(
        "Trade-off de thresholds na calibragem"
    )
    axis.set_xlabel(
        "Threshold"
    )
    axis.set_ylabel(
        "Métrica"
    )
    axis.set_xticks(
        frame[
            "threshold"
        ]
    )
    axis.set_ylim(
        0,
        1,
    )
    axis.legend(
        loc="best"
    )

    figure.tight_layout()

    _save_figure(
        figure,
        output_path,
    )


def _plot_metrics(
    frame: pd.DataFrame,
    output_path: Path,
) -> None:
    ordered_metrics = list(
        METRIC_LABELS
    )

    calibration = (
        frame.loc[
            frame[
                "split"
            ].eq(
                "calibration"
            )
        ]
        .iloc[
            0
        ]
    )

    test = (
        frame.loc[
            frame[
                "split"
            ].eq(
                "test"
            )
        ]
        .iloc[
            0
        ]
    )

    x = np.arange(
        len(
            ordered_metrics
        )
    )

    width = 0.36

    figure, axis = plt.subplots(
        figsize=(
            8,
            5,
        )
    )

    axis.bar(
        x
        - width
        / 2,
        [
            float(
                calibration[
                    metric
                ]
            )
            for metric in ordered_metrics
        ],
        width,
        label="Calibragem",
    )

    axis.bar(
        x
        + width
        / 2,
        [
            float(
                test[
                    metric
                ]
            )
            for metric in ordered_metrics
        ],
        width,
        label="Teste",
    )

    axis.set_title(
        "Métricas do modelo: calibragem × teste temporal"
    )
    axis.set_xlabel(
        "Métrica"
    )
    axis.set_ylabel(
        "Valor"
    )
    axis.set_xticks(
        x,
        [
            METRIC_LABELS[
                metric
            ]
            for metric in ordered_metrics
        ],
    )
    axis.set_ylim(
        0,
        1,
    )
    axis.legend(
        loc="best"
    )

    figure.tight_layout()

    _save_figure(
        figure,
        output_path,
    )


def _plot_importance(
    frame: pd.DataFrame,
    output_path: Path,
) -> None:
    top = (
        frame.head(
            TOP_FEATURES
        )
        .iloc[
            ::-1
        ]
        .copy()
    )

    labels = [
        feature_label(
            value
        )
        for value in top[
            "feature"
        ]
    ]

    figure, axis = plt.subplots(
        figsize=(
            10,
            6,
        )
    )

    axis.barh(
        labels,
        top[
            "importance"
        ],
    )

    axis.set_title(
        "Top features por importância gain do XGBoost"
    )
    axis.set_xlabel(
        "Importância gain"
    )
    axis.set_ylabel(
        "Feature"
    )

    figure.text(
        0.5,
        0.01,
        "Explicabilidade pós-hoc; importância não implica causalidade.",
        ha="center",
    )

    figure.tight_layout(
        rect=(
            0,
            0.04,
            1,
            1,
        )
    )

    _save_figure(
        figure,
        output_path,
    )


def _plot_shap(
    frame: pd.DataFrame,
    output_path: Path,
) -> None:
    top = (
        frame.head(
            TOP_FEATURES
        )
        .iloc[
            ::-1
        ]
        .copy()
    )

    labels = [
        feature_label(
            value
        )
        for value in top[
            "feature"
        ]
    ]

    figure, axis = plt.subplots(
        figsize=(
            10,
            6,
        )
    )

    axis.barh(
        labels,
        top[
            "mean_abs_shap"
        ],
    )

    axis.set_title(
        "Top features por média do valor absoluto de SHAP"
    )
    axis.set_xlabel(
        "Média de |SHAP| no teste temporal"
    )
    axis.set_ylabel(
        "Feature"
    )

    figure.text(
        0.5,
        0.01,
        "SHAP calculado somente no teste; explicação não implica causalidade.",
        ha="center",
    )

    figure.tight_layout(
        rect=(
            0,
            0.04,
            1,
            1,
        )
    )

    _save_figure(
        figure,
        output_path,
    )


def generate_charts(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    overwrite: bool = False,
) -> dict[str, object]:
    """Generate deterministic charts from canonical tabular outputs."""
    input_dir = Path(
        input_dir
    )

    output_dir = Path(
        output_dir
    )

    input_paths = _validate_inputs(
        input_dir
    )

    same_directory = (
        input_dir.resolve()
        == output_dir.resolve()
    )

    output_paths = _prepare_outputs(
        output_dir,
        overwrite=overwrite,
        allow_canonical_base=same_directory,
    )

    splits = pd.read_csv(
        input_paths[
            "02_split_distribution.csv"
        ]
    )

    metrics = pd.read_csv(
        input_paths[
            "03_metrics_summary.csv"
        ]
    )

    thresholds = pd.read_csv(
        input_paths[
            "04_threshold_metrics_calibration.csv"
        ]
    )

    importance = pd.read_csv(
        input_paths[
            "05_feature_importance_gain.csv"
        ]
    )

    shap_summary = pd.read_csv(
        input_paths[
            "06_shap_summary_test.csv"
        ]
    )

    _validate_split_table(
        splits
    )

    _validate_metrics(
        metrics
    )

    selected_threshold = (
        _validate_threshold_table(
            thresholds
        )
    )

    _validate_importance(
        importance
    )

    _validate_shap(
        shap_summary
    )

    with matplotlib.rc_context(
        {
            "font.family":
                "DejaVu Sans",
            "axes.unicode_minus":
                False,
            "figure.dpi":
                100,
            "savefig.dpi":
                PNG_DPI,
        }
    ):
        _plot_split_prevalence(
            splits,
            output_paths[
                CHART_FILENAMES[
                    0
                ]
            ],
        )

        _plot_threshold_tradeoff(
            thresholds,
            selected_threshold,
            output_paths[
                CHART_FILENAMES[
                    1
                ]
            ],
        )

        _plot_metrics(
            metrics,
            output_paths[
                CHART_FILENAMES[
                    2
                ]
            ],
        )

        _plot_importance(
            importance,
            output_paths[
                CHART_FILENAMES[
                    3
                ]
            ],
        )

        _plot_shap(
            shap_summary,
            output_paths[
                CHART_FILENAMES[
                    4
                ]
            ],
        )

    chart_hashes = {
        filename:
            sha256_file(
                output_paths[
                    filename
                ]
            )
        for filename in CHART_FILENAMES
    }

    manifest = {
        "schema_version": 1,
        "pipeline":
            "canonical_ml_charts",
        "inputs": {
            filename:
                sha256_file(
                    path
                )
            for filename, path
            in sorted(
                input_paths.items()
            )
        },
        "charts": chart_hashes,
        "chart_count":
            len(
                CHART_FILENAMES
            ),
        "selected_threshold":
            selected_threshold,
        "selected_threshold_status":
            "statistical_baseline_not_operationally_homologated",
        "shap_split":
            "test",
        "shap_rows_explained":
            2498,
        "language":
            "pt-BR",
        "runtime": {
            "python":
                platform.python_version(),
            "pandas":
                pd.__version__,
            "matplotlib":
                matplotlib.__version__,
            "numpy":
                np.__version__,
        },
        "governance": {
            "synthetic_data":
                True,
            "weak_label":
                True,
            "r17_in_canonical_label":
                False,
            "human_review_required":
                True,
            "operational_threshold_homologated":
                False,
            "production_validation_claimed":
                False,
            "charts_are_post_hoc":
                True,
        },
    }

    output_paths[
        MANIFEST_FILENAME
    ].write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "chart_count":
            len(
                CHART_FILENAMES
            ),
        "artifact_count":
            len(
                ALL_OUTPUT_FILENAMES
            ),
        "selected_threshold":
            selected_threshold,
        "output_dir":
            str(
                output_dir
            ),
        "manifest":
            str(
                output_paths[
                    MANIFEST_FILENAME
                ]
            ),
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Gera gráficos canônicos reproduzíveis "
            "do experimento de ML."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=(
            "Diretório dos artefatos tabulares "
            "canônicos."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Diretório de destino dos gráficos "
            "canônicos."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Permite substituir somente os "
            "artefatos gráficos esperados; "
            "entradas desconhecidas são recusadas."
        ),
    )

    return parser


def main() -> int:
    """Run the chart CLI."""
    parser = build_parser()

    args = parser.parse_args()

    result = generate_charts(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        overwrite=args.overwrite,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
