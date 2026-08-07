"""Runner reproduzível do baseline canônico de ML do Case 04.

A execução usa somente o contrato canônico cliente-mês, seleciona o
threshold no conjunto de calibragem e usa o teste apenas para avaliação
e explicabilidade pós-hoc.

Os outputs legados de ``outputs/t3_ml`` não são utilizados nem
sobrescritos por este módulo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from features import (
    CANONICAL_LABEL_COLUMN,
    CANONICAL_SPLIT_COLUMN,
    RANDOM_STATE,
    build_canonical_customer_month_dataset,
)
from ml_model import (
    THRESHOLD_GRID,
    CanonicalModelFit,
    canonical_shap_summary,
    canonical_xgboost_feature_importance,
    classification_metrics_at_threshold,
    evaluate_calibration_and_test,
    fit_canonical_xgboost,
    prevalence_baseline_scores,
    score_distribution_metrics,
    split_canonical_dataset,
    threshold_metrics_table,
)


DEFAULT_INPUT = Path(
    "outputs/t1_suspects/"
    "04_client_month_alerts_all.csv"
)

DEFAULT_OUTPUT_DIR = Path(
    "outputs/t3_ml_canonical"
)

ARTIFACT_FILENAMES = (
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


def sha256_file(
    path: Path,
) -> str:
    """Return the hexadecimal SHA-256 of one file."""

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def prepare_output_dir(
    output_dir: Path,
    *,
    overwrite: bool,
) -> None:
    """Create or validate the output directory before any artifact write."""

    if output_dir.exists():
        if not output_dir.is_dir():
            raise NotADirectoryError(
                f"output-dir não é diretório: {output_dir}"
            )

        existing = sorted(
            output_dir.iterdir()
        )

        if existing and not overwrite:
            raise FileExistsError(
                "output-dir não está vazio; "
                "use --overwrite de forma explícita: "
                f"{output_dir}"
            )

        if overwrite:
            unexpected = [
                path.name
                for path in existing
                if (
                    path.name
                    not in ARTIFACT_FILENAMES
                    or not path.is_file()
                    or path.is_symlink()
                )
            ]

            if unexpected:
                raise FileExistsError(
                    "output-dir contém entradas fora do "
                    "contrato canônico; nenhuma escrita foi "
                    "realizada: "
                    + ", ".join(
                        unexpected
                    )
                )
    else:
        output_dir.mkdir(
            parents=True,
            exist_ok=False,
        )


def canonical_model_view(
    dataset: pd.DataFrame,
    model_fit: CanonicalModelFit,
) -> pd.DataFrame:
    """Return only IDs, split, weak label and approved model features."""

    feature_columns = list(
        model_fit.categorical_features
        + model_fit.numeric_features
    )

    columns = [
        "customer_id",
        "month",
        CANONICAL_SPLIT_COLUMN,
        CANONICAL_LABEL_COLUMN,
        *feature_columns,
    ]

    missing = [
        column
        for column in columns
        if column not in dataset.columns
    ]

    if missing:
        raise ValueError(
            "dataset canônico sem colunas necessárias: "
            + ", ".join(
                missing
            )
        )

    if len(columns) != len(set(columns)):
        raise ValueError(
            "view canônica contém colunas duplicadas"
        )

    return (
        dataset.loc[
            :,
            columns,
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )


def split_distribution(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize the explicit train/calibration/test partitions."""

    partitions = split_canonical_dataset(
        dataset
    )

    rows: list[dict[str, Any]] = []

    for split_name in (
        "train",
        "calibration",
        "test",
    ):
        frame = getattr(
            partitions,
            split_name,
        )

        target = (
            frame[
                CANONICAL_LABEL_COLUMN
            ]
            .astype(int)
        )

        positives = int(
            target.sum()
        )

        negatives = int(
            len(target)
            - positives
        )

        rows.append(
            {
                "split": split_name,
                "month": str(
                    frame[
                        "month"
                    ].iloc[0]
                ),
                "rows": int(
                    len(frame)
                ),
                "positives": positives,
                "negatives": negatives,
                "prevalence": float(
                    target.mean()
                ),
                "unique_customers": int(
                    frame[
                        "customer_id"
                    ].nunique()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def _metric_row(
    *,
    split_name: str,
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
    selection_rule: str,
    threshold_source: str,
    y_train: pd.Series,
) -> dict[str, Any]:
    """Build one transparent model-versus-baseline metric record."""

    ranking = score_distribution_metrics(
        y_true,
        probabilities,
    )

    classification = (
        classification_metrics_at_threshold(
            y_true,
            probabilities,
            threshold,
        )
    )

    baseline_probabilities = (
        prevalence_baseline_scores(
            y_train,
            len(
                y_true
            ),
        )
    )

    baseline = score_distribution_metrics(
        y_true,
        baseline_probabilities,
    )

    result: dict[str, Any] = {
        "split": split_name,
        "threshold_source":
            threshold_source,
        "selection_rule":
            selection_rule,
        "operationally_homologated":
            False,
        "train_prevalence_baseline":
            float(
                y_train.mean()
            ),
        "baseline_auc_pr":
            float(
                baseline[
                    "auc_pr"
                ]
            ),
        "baseline_auc_roc":
            float(
                baseline[
                    "auc_roc"
                ]
            ),
    }

    result.update(
        ranking
    )

    result.update(
        classification
    )

    return result


def metrics_summary(
    dataset: pd.DataFrame,
    model_fit: CanonicalModelFit,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    dict[str, Any],
    np.ndarray,
    np.ndarray,
]:
    """Evaluate calibration first and untouched test second."""

    partitions = split_canonical_dataset(
        dataset
    )

    feature_columns = list(
        model_fit.categorical_features
        + model_fit.numeric_features
    )

    y_train = (
        partitions.train[
            CANONICAL_LABEL_COLUMN
        ]
        .astype(int)
    )

    y_calibration = (
        partitions.calibration[
            CANONICAL_LABEL_COLUMN
        ]
        .astype(int)
    )

    y_test = (
        partitions.test[
            CANONICAL_LABEL_COLUMN
        ]
        .astype(int)
    )

    calibration_probabilities = (
        model_fit.pipeline
        .predict_proba(
            partitions.calibration[
                feature_columns
            ]
        )[
            :,
            1,
        ]
    )

    test_probabilities = (
        model_fit.pipeline
        .predict_proba(
            partitions.test[
                feature_columns
            ]
        )[
            :,
            1,
        ]
    )

    evaluation = (
        evaluate_calibration_and_test(
            y_calibration,
            calibration_probabilities,
            y_test,
            test_probabilities,
            thresholds=THRESHOLD_GRID,
        )
    )

    selection = dict(
        evaluation[
            "selection"
        ]
    )

    threshold = float(
        selection[
            "threshold"
        ]
    )

    selection_rule = str(
        selection[
            "selection_rule"
        ]
    )

    calibration_thresholds = (
        threshold_metrics_table(
            y_calibration,
            calibration_probabilities,
            thresholds=THRESHOLD_GRID,
        )
        .copy()
    )

    selected_mask = np.isclose(
        calibration_thresholds[
            "threshold"
        ].to_numpy(
            dtype=float
        ),
        threshold,
        rtol=0.0,
        atol=1e-12,
    )

    calibration_thresholds[
        "selected_statistical_baseline"
    ] = selected_mask

    calibration_thresholds[
        "selection_rule"
    ] = selection_rule

    calibration_thresholds[
        "operationally_homologated"
    ] = False

    if int(
        selected_mask.sum()
    ) != 1:
        raise RuntimeError(
            "threshold selecionado não corresponde "
            "a uma única linha do grid"
        )

    calibration_row = _metric_row(
        split_name="calibration",
        y_true=y_calibration,
        probabilities=calibration_probabilities,
        threshold=threshold,
        selection_rule=selection_rule,
        threshold_source="calibration",
        y_train=y_train,
    )

    test_row = _metric_row(
        split_name="test",
        y_true=y_test,
        probabilities=test_probabilities,
        threshold=threshold,
        selection_rule=selection_rule,
        threshold_source="calibration",
        y_train=y_train,
    )

    summary = pd.DataFrame(
        [
            calibration_row,
            test_row,
        ]
    )

    return (
        summary,
        calibration_thresholds,
        selection,
        np.asarray(
            calibration_probabilities,
            dtype=float,
        ),
        np.asarray(
            test_probabilities,
            dtype=float,
        ),
    )


def scored_test_top(
    dataset: pd.DataFrame,
    model_fit: CanonicalModelFit,
    test_probabilities: np.ndarray,
    *,
    threshold: float,
    top_n: int = 30,
) -> pd.DataFrame:
    """Return a deterministic synthetic test ranking for human review."""

    partitions = split_canonical_dataset(
        dataset
    )

    test = partitions.test.copy()

    if len(
        test_probabilities
    ) != len(
        test
    ):
        raise ValueError(
            "probabilidades de teste divergem "
            "do número de registros"
        )

    feature_columns = list(
        model_fit.categorical_features
        + model_fit.numeric_features
    )

    columns = [
        "customer_id",
        "month",
        CANONICAL_LABEL_COLUMN,
        *feature_columns,
    ]

    result = (
        test.loc[
            :,
            columns,
        ]
        .copy()
    )

    result[
        "ml_score"
    ] = np.asarray(
        test_probabilities,
        dtype=float,
    )

    result[
        "ml_pred_at_statistical_threshold"
    ] = (
        result[
            "ml_score"
        ]
        .ge(
            float(
                threshold
            )
        )
        .astype(int)
    )

    result[
        "threshold"
    ] = float(
        threshold
    )

    result[
        "threshold_status"
    ] = (
        "statistical_baseline_not_operationally_homologated"
    )

    return (
        result
        .sort_values(
            [
                "ml_score",
                "customer_id",
                "month",
            ],
            ascending=[
                False,
                True,
                True,
            ],
            kind="mergesort",
        )
        .head(
            int(
                top_n
            )
        )
        .reset_index(
            drop=True
        )
    )


def _write_dataframe(
    frame: pd.DataFrame,
    path: Path,
) -> None:
    """Write one deterministic UTF-8 CSV."""

    frame.to_csv(
        path,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        float_format="%.12g",
    )


def _summary_markdown(
    *,
    input_path: Path,
    input_sha256: str,
    dataset: pd.DataFrame,
    model_fit: CanonicalModelFit,
    split_table: pd.DataFrame,
    metrics: pd.DataFrame,
    selection: dict[str, Any],
) -> str:
    """Build the human-readable canonical ML summary."""

    test_row = (
        metrics.loc[
            metrics[
                "split"
            ].eq(
                "test"
            )
        ]
        .iloc[0]
    )

    threshold = float(
        selection[
            "threshold"
        ]
    )

    lines = [
        "# T3 — Machine Learning canônico",
        "",
        "Baseline experimental cliente-mês com XGBoost explicável.",
        "",
        "## Contrato",
        "",
        "- Base: sintética.",
        "- Label: fraco e derivado das regras determinísticas M01–M12.",
        "- R17: fora do label canônico.",
        "- Treino: julho/2025.",
        "- Calibragem: agosto/2025.",
        "- Teste temporal: setembro/2025.",
        "- Outubro/2025: excluído por mês incompleto.",
        "- `random_state=42`.",
        "- Revisão humana: obrigatória.",
        "- Validação produtiva: não alegada.",
        "",
        "## Entrada",
        "",
        f"- Arquivo: `{input_path.as_posix()}`.",
        f"- SHA-256: `{input_sha256}`.",
        f"- Registros canônicos: {len(dataset)}.",
        (
            "- Features primárias: "
            f"{len(model_fit.categorical_features)} categóricas + "
            f"{len(model_fit.numeric_features)} numéricas."
        ),
        "",
        "## Splits",
        "",
    ]

    for row in split_table.itertuples(
        index=False
    ):
        lines.append(
            "- "
            f"{row.split}: {row.month}; "
            f"{row.rows} registros; "
            f"{row.positives} positivos; "
            f"prevalência {row.prevalence:.4f}."
        )

    lines.extend(
        [
            "",
            "## Threshold",
            "",
            (
                "- Threshold estatístico selecionado na calibragem: "
                f"{threshold:.1f}."
            ),
            (
                "- Regra de seleção: "
                f"`{selection['selection_rule']}`."
            ),
            "- Restrições operacionais explícitas: não aplicadas.",
            "- Homologação operacional: não.",
            (
                "- O threshold é baseline estatístico e não deve ser "
                "interpretado como threshold de produção."
            ),
            "",
            "## Teste temporal",
            "",
            f"- AUC-PR: {float(test_row['auc_pr']):.4f}.",
            f"- AUC-ROC: {float(test_row['auc_roc']):.4f}.",
            f"- Precision: {float(test_row['precision']):.4f}.",
            f"- Recall: {float(test_row['recall']):.4f}.",
            f"- FPR: {float(test_row['fpr']):.4f}.",
            f"- MCC: {float(test_row['mcc']):.4f}.",
            (
                "- Alertas no threshold estatístico: "
                f"{int(test_row['alerts_generated'])} "
                f"de {int(test_row['rows'])}."
            ),
            "",
            "## Limitações de interpretação",
            "",
            (
                "- As métricas medem a capacidade de aproximar um label "
                "fraco, não de provar ilícito ou validar produção."
            ),
            (
                "- Há circularidade conceitual porque o label deriva de "
                "regras determinísticas e algumas features representam "
                "conceitos correlatos."
            ),
            (
                "- O split é temporal, mas as mesmas entidades aparecem "
                "em meses sucessivos; a independência entre clientes não "
                "é garantida."
            ),
            (
                "- SHAP e feature importance são explicabilidade pós-hoc "
                "e não participam da seleção do threshold."
            ),
            (
                "- Capacidade da fila, custo de falsos positivos e "
                "negativos, calibragem e drift ainda precisam de "
                "homologação antes de qualquer uso operacional."
            ),
            "",
        ]
    )

    return "\n".join(
        lines
    )


def _manifest(
    *,
    input_path: Path,
    input_sha256: str,
    dataset: pd.DataFrame,
    model_fit: CanonicalModelFit,
    split_table: pd.DataFrame,
    selection: dict[str, Any],
    artifact_hashes: dict[str, str],
) -> dict[str, Any]:
    """Build a deterministic audit manifest without runtime timestamps."""

    try:
        import shap
        import sklearn
        import xgboost
    except ImportError as error:
        raise ImportError(
            "dependências de ML incompletas"
        ) from error

    return {
        "schema_version": 1,
        "title": (
            "AML/FT & Financial Crime Analytics: "
            "Data, Machine Learning and AI Agents"
        ),
        "pipeline": "canonical_customer_month_xgboost",
        "data": {
            "synthetic": True,
            "weak_label": True,
            "label_column":
                CANONICAL_LABEL_COLUMN,
            "label_source":
                "deterministic_rules_M01_M12",
            "r17_in_label": False,
            "input_path":
                input_path.as_posix(),
            "input_sha256":
                input_sha256,
            "canonical_rows":
                int(
                    len(
                        dataset
                    )
                ),
        },
        "model": {
            "algorithm": "XGBoost",
            "random_state": RANDOM_STATE,
            "scale_pos_weight":
                float(
                    model_fit.scale_pos_weight
                ),
            "categorical_features":
                list(
                    model_fit.categorical_features
                ),
            "numeric_features":
                list(
                    model_fit.numeric_features
                ),
        },
        "splits":
            split_table.to_dict(
                orient="records"
            ),
        "threshold": {
            "selection_split":
                str(
                    selection[
                        "selection_split"
                    ]
                ),
            "selection_rule":
                str(
                    selection[
                        "selection_rule"
                    ]
                ),
            "value":
                float(
                    selection[
                        "threshold"
                    ]
                ),
            "operational_constraints_applied":
                False,
            "operationally_homologated":
                False,
        },
        "explainability": {
            "feature_importance_type":
                "gain",
            "shap_split":
                "test",
            "shap_used_for_training":
                False,
            "shap_used_for_threshold_selection":
                False,
        },
        "governance": {
            "human_review_required": True,
            "production_validation_claimed": False,
            "model_persisted": False,
            "legacy_t3_outputs_reused": False,
        },
        "runtime": {
            "python":
                platform.python_version(),
            "pandas":
                pd.__version__,
            "numpy":
                np.__version__,
            "scikit_learn":
                sklearn.__version__,
            "xgboost":
                xgboost.__version__,
            "shap":
                shap.__version__,
        },
        "artifacts":
            artifact_hashes,
    }


def run_pipeline(
    *,
    input_path: Path,
    output_dir: Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Execute the canonical experiment and persist auditable artifacts."""

    if not input_path.is_file():
        raise FileNotFoundError(
            f"entrada não encontrada: {input_path}"
        )

    prepare_output_dir(
        output_dir,
        overwrite=overwrite,
    )

    source = pd.read_csv(
        input_path,
        low_memory=False,
    )

    dataset, categorical, numeric = (
        build_canonical_customer_month_dataset(
            source
        )
    )

    model_fit = fit_canonical_xgboost(
        dataset,
        categorical,
        numeric,
    )

    model_dataset = canonical_model_view(
        dataset,
        model_fit,
    )

    splits = split_distribution(
        dataset
    )

    (
        metrics,
        threshold_table,
        selection,
        _calibration_probabilities,
        test_probabilities,
    ) = metrics_summary(
        dataset,
        model_fit,
    )

    importance = (
        canonical_xgboost_feature_importance(
            model_fit,
            importance_type="gain",
        )
    )

    shap_summary = canonical_shap_summary(
        model_fit,
        dataset,
        split="test",
    )

    top30 = scored_test_top(
        dataset,
        model_fit,
        test_probabilities,
        threshold=float(
            selection[
                "threshold"
            ]
        ),
        top_n=30,
    )

    input_sha256 = sha256_file(
        input_path
    )

    summary = _summary_markdown(
        input_path=input_path,
        input_sha256=input_sha256,
        dataset=dataset,
        model_fit=model_fit,
        split_table=splits,
        metrics=metrics,
        selection=selection,
    )

    artifact_frames = {
        "01_canonical_model_dataset.csv":
            model_dataset,
        "02_split_distribution.csv":
            splits,
        "03_metrics_summary.csv":
            metrics,
        "04_threshold_metrics_calibration.csv":
            threshold_table,
        "05_feature_importance_gain.csv":
            importance,
        "06_shap_summary_test.csv":
            shap_summary,
        "07_test_scored_top30.csv":
            top30,
    }

    (
        output_dir
        / "00_ml_canonical_summary.md"
    ).write_text(
        summary,
        encoding="utf-8",
    )

    for filename, frame in (
        artifact_frames.items()
    ):
        _write_dataframe(
            frame,
            output_dir
            / filename,
        )

    pre_manifest_files = (
        ARTIFACT_FILENAMES[
            :-1
        ]
    )

    artifact_hashes = {
        filename:
            sha256_file(
                output_dir
                / filename
            )
        for filename in pre_manifest_files
    }

    manifest = _manifest(
        input_path=input_path,
        input_sha256=input_sha256,
        dataset=dataset,
        model_fit=model_fit,
        split_table=splits,
        selection=selection,
        artifact_hashes=artifact_hashes,
    )

    (
        output_dir
        / "08_run_manifest.json"
    ).write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    final_files = tuple(
        sorted(
            path.name
            for path in output_dir.iterdir()
            if path.is_file()
        )
    )

    if final_files != tuple(
        sorted(
            ARTIFACT_FILENAMES
        )
    ):
        raise RuntimeError(
            "conjunto final de artefatos divergente: "
            + repr(
                final_files
            )
        )

    return {
        "input_sha256":
            input_sha256,
        "canonical_rows":
            int(
                len(
                    dataset
                )
            ),
        "train_rows":
            int(
                model_fit.train_rows
            ),
        "train_positives":
            int(
                model_fit.train_positives
            ),
        "scale_pos_weight":
            float(
                model_fit.scale_pos_weight
            ),
        "selected_threshold":
            float(
                selection[
                    "threshold"
                ]
            ),
        "selection_rule":
            str(
                selection[
                    "selection_rule"
                ]
            ),
        "operationally_homologated":
            False,
        "shap_rows_explained":
            int(
                shap_summary[
                    "rows_explained"
                ].iloc[0]
            ),
        "artifact_count":
            len(
                ARTIFACT_FILENAMES
            ),
        "output_dir":
            output_dir.as_posix(),
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the explicit non-interactive CLI."""

    parser = argparse.ArgumentParser(
        description=(
            "Regenera o baseline canônico de Machine Learning "
            "sem sobrescrever silenciosamente outputs legados."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "CSV cliente-mês produzido pelo motor determinístico "
            "M01-M12."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Diretório exclusivo dos novos artefatos "
            "canônicos."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Permite substituir somente artefatos canônicos "
            "esperados; recusa diretórios com entradas "
            "desconhecidas."
        ),
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """CLI entry point."""

    args = build_parser().parse_args(
        argv
    )

    result = run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        overwrite=bool(
            args.overwrite
        ),
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
