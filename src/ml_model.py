from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


RANDOM_STATE = 42

CANONICAL_LABEL_COLUMN = "weak_label"
CANONICAL_SPLIT_COLUMN = "ml_split"
CANONICAL_SPLITS = (
    "train",
    "calibration",
    "test",
)
CANONICAL_ID_COLUMNS = (
    "customer_id",
    "month",
)

THRESHOLD_GRID = tuple(
    round(index / 10, 1)
    for index in range(1, 10)
)

DEFAULT_QUEUE_CAPACITY = 30

DIRECT_LEAKAGE_COLUMNS = frozenset(
    {
        "customer_id",
        "month",
        "full_name",
        "cpf_cnpj",
        "date_of_birth",
        "registration_date",
        "period_end",
        "entity_type_model",
        CANONICAL_LABEL_COLUMN,
        CANONICAL_SPLIT_COLUMN,
        "month_rule_count",
        "month_rule_score",
        "month_rules_triggered",
        "tx_rule_count",
        "tx_rule_score",
        "tx_rules_triggered",
        "rule_count",
        "suspicious_label",
    }
)


@dataclass(frozen=True)
class CanonicalSplits:
    """Explicit temporal partitions for model development."""

    train: pd.DataFrame
    calibration: pd.DataFrame
    test: pd.DataFrame


@dataclass(frozen=True)
class CanonicalModelFit:
    """Metadata and fitted pipeline for the canonical XGBoost baseline."""

    pipeline: Any
    categorical_features: tuple[str, ...]
    numeric_features: tuple[str, ...]
    scale_pos_weight: float
    train_rows: int
    train_positives: int
    train_negatives: int


def _normalize_feature_names(
    names: Sequence[str],
    *,
    group_name: str,
) -> tuple[str, ...]:
    normalized = tuple(
        str(name)
        for name in names
    )

    for name in normalized:
        if not name:
            raise ValueError(
                f"{group_name} contém nome vazio"
            )

        if name != name.strip():
            raise ValueError(
                f"{group_name} contém whitespace externo: "
                f"{name!r}"
            )

    if len(normalized) != len(
        set(normalized)
    ):
        raise ValueError(
            f"{group_name} contém duplicidades"
        )

    return normalized


def is_direct_leakage_column(
    column: str,
) -> bool:
    """Return whether a field directly exposes labels, rules or identity."""

    return (
        column in DIRECT_LEAKAGE_COLUMNS
        or column.startswith("r_")
        or column.startswith("R17")
        or (
            len(column) > 4
            and column.startswith("M")
            and column[1:3].isdigit()
            and column[3] == "_"
        )
    )


def _binary_target(
    values: Sequence[int] | pd.Series | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    series = pd.Series(
        values,
        copy=False,
    )

    if series.isna().any():
        raise ValueError(
            f"{name} contém valor ausente"
        )

    numeric = pd.to_numeric(
        series,
        errors="coerce",
    )

    if numeric.isna().any():
        raise ValueError(
            f"{name} contém valor não numérico"
        )

    if not numeric.isin(
        [
            0,
            1,
        ]
    ).all():
        raise ValueError(
            f"{name} deve ser binário"
        )

    return numeric.astype(
        int
    ).to_numpy()


def _probabilities(
    values: Sequence[float] | pd.Series | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    array = np.asarray(
        values,
        dtype=float,
    )

    if array.ndim != 1:
        raise ValueError(
            f"{name} deve ser unidimensional"
        )

    if not np.isfinite(array).all():
        raise ValueError(
            f"{name} contém valor ausente ou infinito"
        )

    if (
        (array < 0)
        | (array > 1)
    ).any():
        raise ValueError(
            f"{name} deve estar no intervalo [0, 1]"
        )

    return array


def _validated_thresholds(
    thresholds: Sequence[float],
) -> tuple[float, ...]:
    resolved = tuple(
        float(threshold)
        for threshold in thresholds
    )

    if not resolved:
        raise ValueError(
            "thresholds não pode ser vazio"
        )

    if len(resolved) != len(
        set(resolved)
    ):
        raise ValueError(
            "thresholds contém duplicidades"
        )

    if resolved != tuple(
        sorted(resolved)
    ):
        raise ValueError(
            "thresholds deve estar em ordem crescente"
        )

    if any(
        not 0 < threshold < 1
        for threshold in resolved
    ):
        raise ValueError(
            "thresholds deve estar no intervalo aberto (0, 1)"
        )

    return resolved


def validate_canonical_dataset(
    dataset: pd.DataFrame,
    categorical_features: Sequence[str] = (),
    numeric_features: Sequence[str] = (),
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Validate the canonical customer-month modeling contract."""

    required = {
        *CANONICAL_ID_COLUMNS,
        CANONICAL_LABEL_COLUMN,
        CANONICAL_SPLIT_COLUMN,
    }

    missing_required = sorted(
        required
        - set(dataset.columns)
    )

    if missing_required:
        raise ValueError(
            "Colunas canônicas ausentes: "
            + ", ".join(
                missing_required
            )
        )

    if dataset.empty:
        raise ValueError(
            "Dataset canônico não pode ser vazio"
        )

    for column in CANONICAL_ID_COLUMNS:
        values = dataset[column]

        if values.isna().any():
            raise ValueError(
                f"{column} contém valor ausente"
            )

        blank = (
            values.astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
        )

        if blank.any():
            raise ValueError(
                f"{column} contém valor vazio"
            )

    duplicate_keys = int(
        dataset.duplicated(
            list(
                CANONICAL_ID_COLUMNS
            )
        ).sum()
    )

    if duplicate_keys:
        raise ValueError(
            "Chaves customer_id + month duplicadas: "
            f"{duplicate_keys}"
        )

    _binary_target(
        dataset[
            CANONICAL_LABEL_COLUMN
        ],
        name=CANONICAL_LABEL_COLUMN,
    )

    split_values = dataset[
        CANONICAL_SPLIT_COLUMN
    ]

    if split_values.isna().any():
        raise ValueError(
            f"{CANONICAL_SPLIT_COLUMN} contém valor ausente"
        )

    actual_splits = set(
        split_values.astype(str)
    )

    expected_splits = set(
        CANONICAL_SPLITS
    )

    if actual_splits != expected_splits:
        raise ValueError(
            "Splits canônicos divergentes; "
            f"esperados={sorted(expected_splits)}, "
            f"encontrados={sorted(actual_splits)}"
        )

    for split_name in CANONICAL_SPLITS:
        if not split_values.eq(
            split_name
        ).any():
            raise ValueError(
                f"Split vazio: {split_name}"
            )

    month_values = dataset[
        "month"
    ].astype("string")

    try:
        periods = pd.PeriodIndex(
            month_values,
            freq="M",
        )
    except Exception as error:
        raise ValueError(
            "month contém valor calendário inválido"
        ) from error

    split_periods = {
        split_name: periods[
            split_values.eq(
                split_name
            ).to_numpy()
        ]
        for split_name in CANONICAL_SPLITS
    }

    if not (
        split_periods["train"].max()
        < split_periods["calibration"].min()
        and split_periods["calibration"].max()
        < split_periods["test"].min()
    ):
        raise ValueError(
            "Splits não respeitam ordem temporal "
            "train < calibration < test"
        )

    categorical = _normalize_feature_names(
        categorical_features,
        group_name="categorical_features",
    )
    numeric = _normalize_feature_names(
        numeric_features,
        group_name="numeric_features",
    )

    selected = categorical + numeric

    if len(selected) != len(
        set(selected)
    ):
        raise ValueError(
            "Feature repetida entre grupos categórico e numérico"
        )

    missing_features = sorted(
        set(selected)
        - set(dataset.columns)
    )

    if missing_features:
        raise ValueError(
            "Features ausentes: "
            + ", ".join(
                missing_features
            )
        )

    prohibited = [
        column
        for column in selected
        if is_direct_leakage_column(
            column
        )
    ]

    if prohibited:
        raise ValueError(
            "Features com leakage direto: "
            + ", ".join(
                prohibited
            )
        )

    for column in numeric:
        original = dataset[column]

        converted = pd.to_numeric(
            original,
            errors="coerce",
        )

        invalid = (
            original.notna()
            & converted.isna()
        )

        if invalid.any():
            raise ValueError(
                f"Feature numérica inválida: {column}"
            )

        non_missing = converted.dropna()

        if not np.isfinite(
            non_missing.to_numpy(
                dtype=float
            )
        ).all():
            raise ValueError(
                f"Feature numérica infinita: {column}"
            )

    return (
        categorical,
        numeric,
    )


def split_canonical_dataset(
    dataset: pd.DataFrame,
) -> CanonicalSplits:
    """Return explicit train, calibration and untouched test partitions."""

    validate_canonical_dataset(
        dataset
    )

    return CanonicalSplits(
        train=dataset.loc[
            dataset[
                CANONICAL_SPLIT_COLUMN
            ].eq("train")
        ].copy(),
        calibration=dataset.loc[
            dataset[
                CANONICAL_SPLIT_COLUMN
            ].eq("calibration")
        ].copy(),
        test=dataset.loc[
            dataset[
                CANONICAL_SPLIT_COLUMN
            ].eq("test")
        ].copy(),
    )


def compute_scale_pos_weight(
    y_train: Sequence[int] | pd.Series | np.ndarray,
) -> float:
    """Calculate class weighting exclusively from the training target."""

    target = _binary_target(
        y_train,
        name="y_train",
    )

    positives = int(
        target.sum()
    )
    negatives = int(
        len(target)
        - positives
    )

    if positives == 0:
        raise ValueError(
            "y_train não contém positivos"
        )

    if negatives == 0:
        raise ValueError(
            "y_train não contém negativos"
        )

    return negatives / positives


def average_precision_binary(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    probabilities: Sequence[float] | pd.Series | np.ndarray,
) -> float:
    """Compute non-interpolated average precision for a binary target."""

    target = _binary_target(
        y_true,
        name="y_true",
    )
    scores = _probabilities(
        probabilities,
        name="probabilities",
    )

    if len(target) != len(scores):
        raise ValueError(
            "y_true e probabilities possuem tamanhos diferentes"
        )

    positives = int(
        target.sum()
    )

    if positives == 0:
        return float("nan")

    order = np.argsort(
        -scores,
        kind="mergesort",
    )

    sorted_target = target[
        order
    ]
    sorted_scores = scores[
        order
    ]

    distinct_ends = np.r_[
        np.flatnonzero(
            np.diff(
                sorted_scores
            )
            != 0
        ),
        len(sorted_scores) - 1,
    ]

    cumulative_true = np.cumsum(
        sorted_target
    )[distinct_ends]

    predicted_positive = (
        distinct_ends
        + 1
    )

    precision = (
        cumulative_true
        / predicted_positive
    )

    recall = (
        cumulative_true
        / positives
    )

    recall_gain = np.diff(
        np.r_[
            0.0,
            recall,
        ]
    )

    return float(
        np.sum(
            recall_gain
            * precision
        )
    )


def roc_auc_binary(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    probabilities: Sequence[float] | pd.Series | np.ndarray,
) -> float:
    """Compute ROC AUC through the Mann-Whitney rank statistic."""

    target = _binary_target(
        y_true,
        name="y_true",
    )
    scores = _probabilities(
        probabilities,
        name="probabilities",
    )

    if len(target) != len(scores):
        raise ValueError(
            "y_true e probabilities possuem tamanhos diferentes"
        )

    positives = int(
        target.sum()
    )
    negatives = int(
        len(target)
        - positives
    )

    if positives == 0 or negatives == 0:
        return float("nan")

    order = np.argsort(
        scores,
        kind="mergesort",
    )

    sorted_scores = scores[
        order
    ]

    sorted_ranks = np.empty(
        len(scores),
        dtype=float,
    )

    start = 0

    while start < len(scores):
        end = start + 1

        while (
            end < len(scores)
            and sorted_scores[end]
            == sorted_scores[start]
        ):
            end += 1

        average_rank = (
            (start + 1)
            + end
        ) / 2.0

        sorted_ranks[
            start:end
        ] = average_rank

        start = end

    ranks = np.empty_like(
        sorted_ranks
    )

    ranks[
        order
    ] = sorted_ranks

    positive_rank_sum = float(
        ranks[
            target == 1
        ].sum()
    )

    auc = (
        positive_rank_sum
        - positives
        * (positives + 1)
        / 2.0
    ) / (
        positives
        * negatives
    )

    return float(auc)


def classification_metrics_at_threshold(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    probabilities: Sequence[float] | pd.Series | np.ndarray,
    threshold: float,
) -> dict[str, float | int]:
    """Evaluate one operating threshold without changing model scores."""

    target = _binary_target(
        y_true,
        name="y_true",
    )
    scores = _probabilities(
        probabilities,
        name="probabilities",
    )

    if len(target) != len(scores):
        raise ValueError(
            "y_true e probabilities possuem tamanhos diferentes"
        )

    resolved_threshold = float(
        threshold
    )

    if not 0 < resolved_threshold < 1:
        raise ValueError(
            "threshold deve estar no intervalo aberto (0, 1)"
        )

    predicted = (
        scores
        >= resolved_threshold
    ).astype(int)

    tp = int(
        (
            (target == 1)
            & (predicted == 1)
        ).sum()
    )
    fp = int(
        (
            (target == 0)
            & (predicted == 1)
        ).sum()
    )
    tn = int(
        (
            (target == 0)
            & (predicted == 0)
        ).sum()
    )
    fn = int(
        (
            (target == 1)
            & (predicted == 0)
        ).sum()
    )

    precision_denominator = (
        tp
        + fp
    )
    recall_denominator = (
        tp
        + fn
    )
    fpr_denominator = (
        fp
        + tn
    )

    precision = (
        tp
        / precision_denominator
        if precision_denominator
        else 0.0
    )
    recall = (
        tp
        / recall_denominator
        if recall_denominator
        else 0.0
    )
    fpr = (
        fp
        / fpr_denominator
        if fpr_denominator
        else 0.0
    )

    mcc_denominator = np.sqrt(
        (tp + fp)
        * (tp + fn)
        * (tn + fp)
        * (tn + fn)
    )

    mcc = (
        (
            tp * tn
            - fp * fn
        )
        / mcc_denominator
        if mcc_denominator
        else 0.0
    )

    alerts_generated = int(
        predicted.sum()
    )

    return {
        "threshold": resolved_threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": float(
            precision
        ),
        "recall": float(
            recall
        ),
        "fpr": float(
            fpr
        ),
        "mcc": float(
            mcc
        ),
        "alerts_generated": alerts_generated,
        "alert_rate": (
            alerts_generated
            / len(target)
            if len(target)
            else 0.0
        ),
    }


def threshold_metrics_table(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    probabilities: Sequence[float] | pd.Series | np.ndarray,
    thresholds: Sequence[float] = THRESHOLD_GRID,
) -> pd.DataFrame:
    """Evaluate the fixed threshold grid on one labeled partition."""

    resolved_thresholds = _validated_thresholds(
        thresholds
    )

    rows = [
        classification_metrics_at_threshold(
            y_true,
            probabilities,
            threshold,
        )
        for threshold in resolved_thresholds
    ]

    return pd.DataFrame(
        rows
    )


def score_distribution_metrics(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    probabilities: Sequence[float] | pd.Series | np.ndarray,
) -> dict[str, float | int]:
    """Return threshold-independent metrics for one partition."""

    target = _binary_target(
        y_true,
        name="y_true",
    )
    scores = _probabilities(
        probabilities,
        name="probabilities",
    )

    if len(target) != len(scores):
        raise ValueError(
            "y_true e probabilities possuem tamanhos diferentes"
        )

    positives = int(
        target.sum()
    )
    negatives = int(
        len(target)
        - positives
    )

    return {
        "rows": int(
            len(target)
        ),
        "positives": positives,
        "negatives": negatives,
        "prevalence": (
            positives
            / len(target)
            if len(target)
            else 0.0
        ),
        "auc_pr": average_precision_binary(
            target,
            scores,
        ),
        "auc_roc": roc_auc_binary(
            target,
            scores,
        ),
    }


def select_operating_threshold(
    threshold_table: pd.DataFrame,
    *,
    max_alerts: int | None = None,
    min_recall: float | None = None,
) -> dict[str, float | int | str]:
    """Select a threshold only from calibration metrics.

    Eligible thresholds are ranked by MCC, recall and precision. FPR,
    generated alerts and the threshold itself provide deterministic
    conservative tie-breakers. Operational constraints are optional and
    explicit.
    """

    required_columns = {
        "threshold",
        "precision",
        "recall",
        "fpr",
        "mcc",
        "alerts_generated",
    }

    missing = sorted(
        required_columns
        - set(
            threshold_table.columns
        )
    )

    if missing:
        raise ValueError(
            "Colunas ausentes na tabela de thresholds: "
            + ", ".join(
                missing
            )
        )

    if threshold_table.empty:
        raise ValueError(
            "Tabela de thresholds não pode ser vazia"
        )

    eligible = threshold_table.copy()

    if max_alerts is not None:
        if (
            isinstance(
                max_alerts,
                bool,
            )
            or int(max_alerts) != max_alerts
            or max_alerts < 0
        ):
            raise ValueError(
                "max_alerts deve ser inteiro não negativo"
            )

        eligible = eligible.loc[
            eligible[
                "alerts_generated"
            ].le(
                int(max_alerts)
            )
        ]

    if min_recall is not None:
        resolved_min_recall = float(
            min_recall
        )

        if not 0 <= resolved_min_recall <= 1:
            raise ValueError(
                "min_recall deve estar no intervalo [0, 1]"
            )

        eligible = eligible.loc[
            eligible[
                "recall"
            ].ge(
                resolved_min_recall
            )
        ]

    if eligible.empty:
        raise ValueError(
            "Nenhum threshold atende às restrições operacionais"
        )

    ordered = eligible.sort_values(
        [
            "mcc",
            "recall",
            "precision",
            "fpr",
            "alerts_generated",
            "threshold",
        ],
        ascending=[
            False,
            False,
            False,
            True,
            True,
            False,
        ],
        kind="mergesort",
    )

    best = ordered.iloc[0]

    operational_constraints_applied = (
        max_alerts is not None
        or min_recall is not None
    )

    selection_rule = (
        "max_mcc_with_explicit_operational_constraints"
        if operational_constraints_applied
        else "max_mcc_statistical_baseline"
    )

    return {
        "selection_split": "calibration",
        "selection_rule": selection_rule,
        "threshold": float(
            best["threshold"]
        ),
        "precision": float(
            best["precision"]
        ),
        "recall": float(
            best["recall"]
        ),
        "fpr": float(
            best["fpr"]
        ),
        "mcc": float(
            best["mcc"]
        ),
        "alerts_generated": int(
            best["alerts_generated"]
        ),
    }


def evaluate_calibration_and_test(
    y_calibration: Sequence[int] | pd.Series | np.ndarray,
    calibration_probabilities: Sequence[float] | pd.Series | np.ndarray,
    y_test: Sequence[int] | pd.Series | np.ndarray,
    test_probabilities: Sequence[float] | pd.Series | np.ndarray,
    *,
    thresholds: Sequence[float] = THRESHOLD_GRID,
    max_alerts: int | None = None,
    min_recall: float | None = None,
) -> dict[str, Any]:
    """Select on calibration, then evaluate the untouched test once."""

    calibration_thresholds = (
        threshold_metrics_table(
            y_calibration,
            calibration_probabilities,
            thresholds,
        )
    )

    selection = select_operating_threshold(
        calibration_thresholds,
        max_alerts=max_alerts,
        min_recall=min_recall,
    )

    selected_threshold = float(
        selection[
            "threshold"
        ]
    )

    calibration_summary = (
        score_distribution_metrics(
            y_calibration,
            calibration_probabilities,
        )
    )
    calibration_summary.update(
        classification_metrics_at_threshold(
            y_calibration,
            calibration_probabilities,
            selected_threshold,
        )
    )

    test_summary = (
        score_distribution_metrics(
            y_test,
            test_probabilities,
        )
    )
    test_summary.update(
        classification_metrics_at_threshold(
            y_test,
            test_probabilities,
            selected_threshold,
        )
    )

    test_summary[
        "threshold_source"
    ] = "calibration"

    return {
        "calibration_thresholds":
            calibration_thresholds,
        "selection": selection,
        "calibration_summary":
            calibration_summary,
        "test_summary": test_summary,
    }


def prevalence_baseline_scores(
    y_train: Sequence[int] | pd.Series | np.ndarray,
    row_count: int,
) -> np.ndarray:
    """Create a transparent baseline using training prevalence only."""

    if (
        isinstance(
            row_count,
            bool,
        )
        or int(row_count) != row_count
        or row_count < 0
    ):
        raise ValueError(
            "row_count deve ser inteiro não negativo"
        )

    target = _binary_target(
        y_train,
        name="y_train",
    )

    prevalence = float(
        target.mean()
    )

    return np.full(
        int(row_count),
        prevalence,
        dtype=float,
    )


def build_xgboost_pipeline(
    categorical_features: Sequence[str],
    numeric_features: Sequence[str],
    *,
    scale_pos_weight: float,
) -> Any:
    """Build the deterministic canonical XGBoost pipeline lazily.

    Categorical values are one-hot encoded, including missing as an
    observable category. Numeric values pass through without scaling,
    blanket imputation or automatic outlier removal.
    """

    categorical = _normalize_feature_names(
        categorical_features,
        group_name="categorical_features",
    )
    numeric = _normalize_feature_names(
        numeric_features,
        group_name="numeric_features",
    )

    if not categorical and not numeric:
        raise ValueError(
            "Ao menos uma feature deve ser informada"
        )

    resolved_weight = float(
        scale_pos_weight
    )

    if (
        not np.isfinite(
            resolved_weight
        )
        or resolved_weight <= 0
    ):
        raise ValueError(
            "scale_pos_weight deve ser positivo e finito"
        )

    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        from xgboost import XGBClassifier
    except ImportError as error:
        raise ImportError(
            "Dependências de modelagem ausentes. "
            "Instale as versões fixadas em requirements.txt "
            "antes de treinar o modelo canônico."
        ) from error

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
                list(
                    categorical
                ),
            ),
            (
                "numeric",
                "passthrough",
                list(
                    numeric
                ),
            ),
        ],
        remainder="drop",
        sparse_threshold=1.0,
    )

    model = XGBClassifier(
        n_estimators=250,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=5,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=1,
        scale_pos_weight=resolved_weight,
        verbosity=0,
    )

    return Pipeline(
        [
            (
                "preprocess",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )


def fit_canonical_xgboost(
    dataset: pd.DataFrame,
    categorical_features: Sequence[str],
    numeric_features: Sequence[str],
) -> CanonicalModelFit:
    """Fit only on the canonical training partition."""

    categorical, numeric = (
        validate_canonical_dataset(
            dataset,
            categorical_features,
            numeric_features,
        )
    )

    partitions = split_canonical_dataset(
        dataset
    )

    y_train = partitions.train[
        CANONICAL_LABEL_COLUMN
    ].astype(int)

    scale_pos_weight = (
        compute_scale_pos_weight(
            y_train
        )
    )

    pipeline = build_xgboost_pipeline(
        categorical,
        numeric,
        scale_pos_weight=scale_pos_weight,
    )

    feature_columns = list(
        categorical
        + numeric
    )

    pipeline.fit(
        partitions.train[
            feature_columns
        ],
        y_train,
    )

    positives = int(
        y_train.sum()
    )
    negatives = int(
        len(y_train)
        - positives
    )

    return CanonicalModelFit(
        pipeline=pipeline,
        categorical_features=categorical,
        numeric_features=numeric,
        scale_pos_weight=scale_pos_weight,
        train_rows=len(
            partitions.train
        ),
        train_positives=positives,
        train_negatives=negatives,
    )


def temporal_split(
    df: pd.DataFrame,
    validation_start_month: str = "2025-09",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split legacy customer-month data temporally."""

    train = df.loc[
        df["month"]
        < validation_start_month
    ].copy()

    valid = df.loc[
        df["month"]
        >= validation_start_month
    ].copy()

    return (
        train,
        valid,
    )


def get_feature_columns(
    df: pd.DataFrame,
    rule_cols: list[str],
) -> tuple[list[str], list[str]]:
    """Return legacy feature columns while excluding direct label fields."""

    id_cols = [
        "customer_id",
        "month",
        "full_name",
        "cpf_cnpj",
        "period_end",
        "date_of_birth",
        "registration_date",
        "geo_sender_id",
    ]

    leakage_cols = [
        "suspicious_label",
        "rule_count",
    ] + rule_cols

    exclude = set(
        id_cols
        + leakage_cols
        + [
            "sender_id",
            "merchant_id",
            "owner_customer_id",
        ]
    )

    candidates = [
        column
        for column in df.columns
        if column not in exclude
    ]

    categorical = [
        column
        for column in candidates
        if (
            df[column].dtype
            == "object"
            and column
            != "entity_type_model"
        )
    ]

    numeric = [
        column
        for column in candidates
        if (
            column not in categorical
            and not pd.api.types
            .is_datetime64_any_dtype(
                df[column]
            )
        )
    ]

    return (
        categorical,
        numeric,
    )


def fit_xgboost_pf(
    df: pd.DataFrame,
    rule_cols: list[str],
) -> Any:
    """Fit the retained legacy PF XGBoost pipeline."""

    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        from xgboost import XGBClassifier
    except ImportError as error:
        raise ImportError(
            "Dependências de modelagem ausentes. "
            "Instale as versões fixadas em requirements.txt."
        ) from error

    pf = df.loc[
        df[
            "entity_type_model"
        ].eq("PF")
    ].copy()

    train, _ = temporal_split(
        pf
    )

    categorical, numeric = (
        get_feature_columns(
            pf,
            rule_cols,
        )
    )

    for column in categorical:
        train[column] = (
            train[column]
            .fillna("__MISSING__")
            .astype(str)
        )

    X_train = train[
        categorical
        + numeric
    ]

    y_train = train[
        "suspicious_label"
    ].astype(int)

    positive = int(
        y_train.sum()
    )
    negative = int(
        len(y_train)
        - positive
    )

    scale_pos_weight = (
        negative
        / max(
            positive,
            1,
        )
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
                categorical,
            ),
            (
                "num",
                "passthrough",
                numeric,
            ),
        ]
    )

    model = XGBClassifier(
        n_estimators=250,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=5,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=4,
        scale_pos_weight=scale_pos_weight,
    )

    pipeline = Pipeline(
        [
            (
                "preprocess",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    return pipeline
