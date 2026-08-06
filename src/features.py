from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
import re

import numpy as np
import pandas as pd

RANDOM_STATE = 42

DEFAULT_COMPLETE_MONTHS = ("2025-07", "2025-08", "2025-09")
DEFAULT_SPLIT_MONTHS = {
    "train": "2025-07",
    "calibration": "2025-08",
    "test": "2025-09",
}
CANONICAL_MONTH_RULE_IDS = tuple(f"M{index:02d}" for index in range(1, 13))
CANONICAL_LABEL_COLUMN = "weak_label"
CANONICAL_SPLIT_COLUMN = "ml_split"
REQUIRED_SPLIT_NAMES = frozenset(
    {
        "train",
        "calibration",
        "test",
    }
)

PRIMARY_CATEGORICAL_FEATURES = (
    "declared_occupation",
    "kyc_tier",
    "state",
    "city",
    "beneficial_owner",
)
PRIMARY_NUMERIC_FEATURES = (
    "age",
    "months_since_registration",
    "annual_income_brl",
    "kyc_risk_score",
    "avg_amount",
    "max_amount",
    "confirmed_count",
    "pix_count",
    "card_count",
    "wire_count",
    "peer_group_size",
    "peer_total_amount_median",
    "peer_total_amount_mean",
    "peer_total_amount_std",
    "ratio_to_peer_median_total",
    "zscore_vs_peer_total",
)

# Identifiers, label outputs, deterministic-rule inputs/scores, full-period geo
# aggregates and the historical local-rule fields cannot enter the primary model.
PROHIBITED_EXACT_COLUMNS = frozenset(
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
        "peer_reference_month",
        "peer_reference_method",
        "month_rule_count",
        "month_rule_score",
        "month_rules_triggered",
        "tx_rule_score_sum",
        "tx_rule_score_max",
        "rule_count",
        "suspicious_label",
        "risk_rating",
        "pep",
        "sanctions_list_hit",
        "tx_count",
        "total_amount",
        "cash_in_count",
        "cash_out_count",
        "cash_in_amount",
        "cash_out_amount",
        "cash_in_total",
        "cash_out_total",
        "pass_through_ratio",
        "cross_border_count",
        "high_risk_country_count",
        "high_risk_any_country_count",
        "high_risk_receiver_country_count",
        "sanctions_tx_count",
        "high_risk_mcc_count",
        "mcc_high_risk_count",
        "mcc_high_risk_share",
        "high_risk_merchant_count",
        "merchant_high_risk_count",
        "merchant_high_risk_share",
        "ecommerce_no3ds_count",
        "ecom_no_3ds_count",
        "ip_anomaly_proxy_count",
        "ip_anomaly_count",
        "rooted_count",
        "device_rooted_count",
        "device_rooted_share",
        "near_10k_count",
        "round_100_count",
        "round_1000_count",
        "self_merchant_count",
        "unique_counterparties",
        "out_profile_threshold",
        "monthly_income_est",
        "chargeback_count",
        "high_value_50k_count",
        "geo_sender_id",
        "geo_avg_amount",
        "geo_counterparties",
        "geo_tx_count",
        "geo_tx_per_day",
        "geo_tx_window_days",
    }
)

_REQUIRED_CANONICAL_COLUMNS = frozenset(
    {
        "customer_id",
        "month",
        "month_rule_count",
        "total_amount",
        "declared_occupation",
        "date_of_birth",
        "registration_date",
    }
)


def _validate_calendar_month(month: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}", month) is None:
        raise ValueError(
            "Meses devem usar o formato YYYY-MM"
        )

    try:
        parsed = datetime.strptime(
            month,
            "%Y-%m",
        )
    except ValueError as error:
        raise ValueError(
            f"Mês calendário inválido: {month}"
        ) from error

    if parsed.strftime("%Y-%m") != month:
        raise ValueError(
            f"Mês calendário inválido: {month}"
        )

    return month


def _normalize_months(complete_months: Sequence[str]) -> tuple[str, ...]:
    months = tuple(
        _validate_calendar_month(
            str(month).strip()
        )
        for month in complete_months
    )

    if not months:
        raise ValueError(
            "complete_months não pode ser vazio"
        )

    if len(months) != len(set(months)):
        raise ValueError(
            "complete_months contém duplicidades"
        )

    if months != tuple(sorted(months)):
        raise ValueError(
            "complete_months deve estar em ordem temporal"
        )

    return months


def _canonical_month_rule_columns(columns: Sequence[str]) -> list[str]:
    names = list(columns)
    resolved: list[str] = []

    for rule_id in CANONICAL_MONTH_RULE_IDS:
        matches = [
            name
            for name in names
            if name.startswith(f"{rule_id}_")
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Esperada exatamente uma coluna para {rule_id}; "
                f"encontradas: {matches}"
            )

        resolved.append(matches[0])

    return resolved


def _as_binary_rule(series: pd.Series) -> pd.Series:
    if series.isna().any():
        raise ValueError(
            "Valor de regra ausente"
        )

    if pd.api.types.is_bool_dtype(series.dtype):
        return series.astype(int)

    numeric = pd.to_numeric(series, errors="coerce")
    non_missing = series.notna()

    if numeric.loc[non_missing].notna().all():
        numeric_values = numeric.loc[
            non_missing
        ]

        invalid_numeric = numeric_values.loc[
            ~numeric_values.isin(
                [
                    0,
                    1,
                ]
            )
        ]

        if not invalid_numeric.empty:
            raise ValueError(
                "Valor de regra não binário encontrado: "
                f"{invalid_numeric.iloc[0]!r}"
            )

        return (
            numeric.fillna(0)
            .astype(int)
        )

    normalized = (
        series.astype("string")
        .str.strip()
        .str.lower()
    )

    valid_values = {
        "0",
        "1",
        "false",
        "true",
        "no",
        "yes",
        "não",
        "nao",
        "sim",
    }

    invalid = normalized.loc[
        normalized.notna()
        & ~normalized.isin(valid_values)
    ]

    if not invalid.empty:
        raise ValueError(
            "Valor de regra não binário encontrado: "
            f"{invalid.iloc[0]!r}"
        )

    return normalized.isin(
        {
            "1",
            "true",
            "yes",
            "sim",
        }
    ).astype(int)


def _validate_canonical_input(
    customer_month_alerts: pd.DataFrame,
    complete_months: tuple[str, ...],
) -> list[str]:
    missing = sorted(
        _REQUIRED_CANONICAL_COLUMNS
        - set(customer_month_alerts.columns)
    )

    if missing:
        raise ValueError(
            "Colunas canônicas ausentes: "
            + ", ".join(missing)
        )

    for key_column in (
        "customer_id",
        "month",
    ):
        values = customer_month_alerts[
            key_column
        ]

        if values.isna().any():
            raise ValueError(
                f"{key_column} contém valor ausente"
            )

        blank_values = (
            values.astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
        )

        if blank_values.any():
            raise ValueError(
                f"{key_column} contém valor vazio"
            )

    for month_value in (
        customer_month_alerts[
            "month"
        ]
        .astype("string")
        .dropna()
        .unique()
    ):
        _validate_calendar_month(
            str(month_value)
        )

    duplicate_count = int(
        customer_month_alerts.duplicated(
            [
                "customer_id",
                "month",
            ]
        ).sum()
    )

    if duplicate_count:
        raise ValueError(
            "Chaves customer_id + month duplicadas: "
            f"{duplicate_count}"
        )

    available_months = set(
        customer_month_alerts["month"]
        .astype("string")
        .str.strip()
        .dropna()
    )

    missing_months = sorted(
        set(complete_months)
        - available_months
    )

    if missing_months:
        raise ValueError(
            "Meses completos ausentes: "
            + ", ".join(missing_months)
        )

    return _canonical_month_rule_columns(
        customer_month_alerts.columns
    )


def _leave_one_out_group_stats(
    values: pd.Series,
) -> pd.DataFrame:
    numeric = pd.to_numeric(
        values,
        errors="coerce",
    ).to_numpy(
        dtype=float,
    )

    rows: list[
        tuple[float, float, float, float]
    ] = []

    for position in range(len(numeric)):
        peers = np.delete(
            numeric,
            position,
        )

        peers = peers[
            ~np.isnan(peers)
        ]

        count = float(
            len(peers)
        )

        if not len(peers):
            rows.append(
                (
                    count,
                    np.nan,
                    np.nan,
                    np.nan,
                )
            )
            continue

        rows.append(
            (
                count,
                float(np.median(peers)),
                float(np.mean(peers)),
                (
                    float(
                        np.std(
                            peers,
                            ddof=1,
                        )
                    )
                    if len(peers) > 1
                    else np.nan
                ),
            )
        )

    return pd.DataFrame(
        rows,
        columns=[
            "peer_group_size",
            "peer_total_amount_median",
            "peer_total_amount_mean",
            "peer_total_amount_std",
        ],
        index=values.index,
    )


def _add_lagged_peer_features(
    dataset: pd.DataFrame,
    complete_months: tuple[str, ...],
) -> pd.DataFrame:
    result = dataset.copy()

    total_amount = pd.to_numeric(
        result["total_amount"],
        errors="coerce",
    )

    invalid_total = (
        result["total_amount"].notna()
        & total_amount.isna()
    )

    if invalid_total.any():
        raise ValueError(
            "total_amount contém valor não numérico"
        )

    result["total_amount"] = total_amount

    result["__peer_group_key"] = (
        result["declared_occupation"]
        .astype("string")
        .fillna("__MISSING__")
    )

    statistic_columns = (
        "peer_group_size",
        "peer_total_amount_median",
        "peer_total_amount_mean",
        "peer_total_amount_std",
    )

    for column in statistic_columns:
        result[column] = np.nan

    result["peer_reference_month"] = pd.Series(
        pd.NA,
        index=result.index,
        dtype="string",
    )

    result["peer_reference_method"] = pd.Series(
        pd.NA,
        index=result.index,
        dtype="string",
    )

    train_month = complete_months[0]
    train_mask = result["month"].eq(
        train_month
    )

    train = result.loc[
        train_mask
    ]

    for group_index in train.groupby(
        "__peer_group_key",
        dropna=False,
        sort=False,
    ).groups.values():
        stats = _leave_one_out_group_stats(
            result.loc[
                group_index,
                "total_amount",
            ]
        )

        for column in statistic_columns:
            result.loc[
                group_index,
                column,
            ] = stats[column]

    result.loc[
        train_mask,
        "peer_reference_month",
    ] = train_month

    result.loc[
        train_mask,
        "peer_reference_method",
    ] = "leave_one_out_train"

    for current_month, previous_month in zip(
        complete_months[1:],
        complete_months[:-1],
    ):
        reference = result.loc[
            result["month"].eq(
                previous_month
            ),
            [
                "__peer_group_key",
                "total_amount",
            ],
        ]

        reference_stats = reference.groupby(
            "__peer_group_key",
            dropna=False,
        )["total_amount"].agg(
            peer_group_size="count",
            peer_total_amount_median="median",
            peer_total_amount_mean="mean",
            peer_total_amount_std="std",
        )

        current_mask = result["month"].eq(
            current_month
        )

        current_keys = result.loc[
            current_mask,
            "__peer_group_key",
        ]

        for column in statistic_columns:
            result.loc[
                current_mask,
                column,
            ] = current_keys.map(
                reference_stats[column]
            )

        result.loc[
            current_mask,
            "peer_reference_month",
        ] = previous_month

        result.loc[
            current_mask,
            "peer_reference_method",
        ] = "prior_month"

    result[
        "ratio_to_peer_median_total"
    ] = (
        result["total_amount"]
        / result[
            "peer_total_amount_median"
        ].replace(
            0,
            np.nan,
        )
    )

    result[
        "zscore_vs_peer_total"
    ] = (
        result["total_amount"]
        - result[
            "peer_total_amount_mean"
        ]
    ) / result[
        "peer_total_amount_std"
    ].replace(
        0,
        np.nan,
    )

    return result.drop(
        columns=[
            "__peer_group_key",
        ]
    )


def _coerce_primary_numeric_features(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    missing_features = sorted(
        set(
            PRIMARY_NUMERIC_FEATURES
        )
        - set(result.columns)
    )

    if missing_features:
        raise ValueError(
            "Features canônicas ausentes: "
            + ", ".join(
                missing_features
            )
        )

    for column in PRIMARY_NUMERIC_FEATURES:
        original = result[
            column
        ]

        numeric = pd.to_numeric(
            original,
            errors="coerce",
        )

        invalid = (
            original.notna()
            & numeric.isna()
        )

        if invalid.any():
            first_value = original.loc[
                invalid
            ].iloc[0]

            raise ValueError(
                "Feature numérica contém valor "
                f"não numérico: {column}={first_value!r}"
            )

        finite_values = numeric.loc[
            numeric.notna()
        ]

        if not np.isfinite(
            finite_values.to_numpy(
                dtype=float
            )
        ).all():
            raise ValueError(
                "Feature numérica contém valor "
                f"infinito: {column}"
            )

        result[
            column
        ] = numeric

    return result


def is_prohibited_ml_column(
    column: str,
) -> bool:
    """Return whether a column is prohibited from the primary ML matrix."""

    return (
        column in PROHIBITED_EXACT_COLUMNS
        or bool(
            re.fullmatch(
                r"M\d{2}_.+",
                column,
            )
        )
        or column.startswith("r_")
        or column.startswith("R17")
    )


def get_canonical_feature_columns(
    dataset: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Return explicit categorical and numeric columns for the primary model."""

    required_features = set(
        PRIMARY_CATEGORICAL_FEATURES
        + PRIMARY_NUMERIC_FEATURES
    )

    missing_features = sorted(
        required_features
        - set(dataset.columns)
    )

    if missing_features:
        raise ValueError(
            "Features canônicas ausentes: "
            + ", ".join(
                missing_features
            )
        )

    categorical = list(
        PRIMARY_CATEGORICAL_FEATURES
    )

    numeric = list(
        PRIMARY_NUMERIC_FEATURES
    )

    selected = categorical + numeric

    prohibited = [
        column
        for column in selected
        if is_prohibited_ml_column(
            column
        )
    ]

    if prohibited:
        raise RuntimeError(
            "Contrato de features incluiu colunas proibidas: "
            + ", ".join(prohibited)
        )

    if not selected:
        raise ValueError(
            "Nenhuma feature canônica disponível"
        )

    return categorical, numeric


def build_canonical_customer_month_dataset(
    customer_month_alerts: pd.DataFrame,
    complete_months: Sequence[str] = DEFAULT_COMPLETE_MONTHS,
    split_months: Mapping[str, str] | None = None,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Build the canonical customer-month ML dataset.

    The weak label comes only from M01-M12 materialized by the deterministic
    engine. R17 is not integrated. No PF/PJ inference is performed because the
    synthetic KYC table has no reliable person-type attribute.

    The first complete month uses leave-one-out peer statistics inside the
    training sample. Each later month uses occupation statistics from the
    immediately preceding month, preventing same-month peer leakage in
    calibration and test. Static KYC fields are treated as a point-in-time
    snapshot. Missing values and outliers are preserved.
    """

    months = _normalize_months(
        complete_months
    )

    normalized = customer_month_alerts.copy()

    normalized["customer_id"] = (
        normalized["customer_id"]
        .astype("string")
        .str.strip()
    )

    normalized["month"] = (
        normalized["month"]
        .astype("string")
        .str.strip()
    )

    rule_columns = _validate_canonical_input(
        normalized,
        months,
    )

    dataset = normalized.loc[
        normalized["month"].isin(
            months
        )
    ].copy()

    canonical_rule_count = pd.Series(
        0,
        index=dataset.index,
        dtype=int,
    )

    for column in rule_columns:
        canonical_rule_count = (
            canonical_rule_count
            + _as_binary_rule(
                dataset[column]
            )
        )

    materialized_rule_count = pd.to_numeric(
        dataset["month_rule_count"],
        errors="coerce",
    )

    if materialized_rule_count.isna().any():
        raise ValueError(
            "month_rule_count contém valor "
            "ausente ou não numérico"
        )

    finite_rule_counts = np.isfinite(
        materialized_rule_count.to_numpy(
            dtype=float
        )
    )

    if not finite_rule_counts.all():
        raise ValueError(
            "month_rule_count contém valor infinito"
        )

    fractional_rule_counts = (
        materialized_rule_count
        .mod(1)
        .ne(0)
    )

    if fractional_rule_counts.any():
        raise ValueError(
            "month_rule_count deve conter "
            "somente valores inteiros"
        )

    outside_range = (
        ~materialized_rule_count.between(
            0,
            len(
                CANONICAL_MONTH_RULE_IDS
            ),
            inclusive="both",
        )
    )

    if outside_range.any():
        raise ValueError(
            "month_rule_count fora do intervalo "
            "canônico de 0 a 12"
        )

    materialized_rule_count = (
        materialized_rule_count
        .astype(int)
    )

    mismatch = canonical_rule_count.ne(
        materialized_rule_count
    )

    if mismatch.any():
        first_index = mismatch.loc[
            mismatch
        ].index[0]

        raise ValueError(
            "month_rule_count diverge da soma "
            "M01-M12 na linha de índice "
            f"{first_index}"
        )

    dataset[
        CANONICAL_LABEL_COLUMN
    ] = (
        canonical_rule_count
        .ge(3)
        .astype(int)
    )

    period_end = (
        pd.to_datetime(
            dataset["month"] + "-01",
            errors="coerce",
        )
        + pd.offsets.MonthEnd(0)
    )

    date_of_birth = pd.to_datetime(
        dataset["date_of_birth"],
        errors="coerce",
    )

    registration_date = pd.to_datetime(
        dataset["registration_date"],
        errors="coerce",
    )

    dataset["age"] = (
        (
            period_end
            - date_of_birth
        ).dt.days
        / 365.25
    ).clip(
        lower=0
    )

    dataset[
        "months_since_registration"
    ] = (
        (
            period_end
            - registration_date
        ).dt.days
        / 30.44
    ).clip(
        lower=0
    )

    dataset = _add_lagged_peer_features(
        dataset,
        months,
    )

    dataset = _coerce_primary_numeric_features(
        dataset
    )

    resolved_splits = (
        DEFAULT_SPLIT_MONTHS.copy()
        if split_months is None
        else {
            str(name): str(month)
            for name, month
            in split_months.items()
        }
    )

    split_names = set(
        resolved_splits
    )

    if split_names != REQUIRED_SPLIT_NAMES:
        missing_names = sorted(
            REQUIRED_SPLIT_NAMES
            - split_names
        )

        unexpected_names = sorted(
            split_names
            - REQUIRED_SPLIT_NAMES
        )

        raise ValueError(
            "Nomes de split inválidos; "
            f"ausentes={missing_names}, "
            f"inesperados={unexpected_names}"
        )

    invalid_split_months = sorted(
        set(
            resolved_splits.values()
        )
        - set(months)
    )

    if invalid_split_months:
        raise ValueError(
            "Split referencia mês fora de "
            "complete_months: "
            + ", ".join(
                invalid_split_months
            )
        )

    if len(
        resolved_splits.values()
    ) != len(
        set(
            resolved_splits.values()
        )
    ):
        raise ValueError(
            "Meses duplicados entre splits"
        )

    reverse_split = {
        month: split_name
        for split_name, month
        in resolved_splits.items()
    }

    dataset[
        CANONICAL_SPLIT_COLUMN
    ] = (
        dataset["month"]
        .map(reverse_split)
        .astype("string")
    )

    if dataset[
        CANONICAL_SPLIT_COLUMN
    ].isna().any():
        missing_split_months = sorted(
            dataset.loc[
                dataset[
                    CANONICAL_SPLIT_COLUMN
                ].isna(),
                "month",
            ].unique()
        )

        raise ValueError(
            "Meses sem split definido: "
            + ", ".join(
                missing_split_months
            )
        )

    dataset = dataset.sort_values(
        [
            "month",
            "customer_id",
        ],
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    categorical, numeric = (
        get_canonical_feature_columns(
            dataset
        )
    )

    return (
        dataset,
        categorical,
        numeric,
    )


def build_customer_month_dataset(
    transactions: pd.DataFrame,
    kyc_profiles: pd.DataFrame,
    merchants: pd.DataFrame,
    geo_behavior: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Build the legacy, non-canonical T3 dataset.

    This function is retained temporarily for backward compatibility with the
    historical notebook. It recreates eighteen local rules and must not be
    used by the canonical ML pipeline, whose label comes from M01-M12 produced
    by src/rules.py.
    """
    tx = transactions.copy()
    kyc = kyc_profiles.copy()
    merchants = merchants.copy()
    geo = geo_behavior.copy()

    tx["timestamp"] = pd.to_datetime(tx["timestamp"], errors="coerce")
    tx["month"] = tx["timestamp"].dt.to_period("M").astype(str)
    tx = tx.merge(
        merchants[["merchant_id", "mcc_risk", "merchant_high_risk_flag", "merchant_chargeback_ratio_90d", "owner_customer_id"]],
        left_on="receiver_id",
        right_on="merchant_id",
        how="left",
    )

    out = tx[tx["sender_id"].astype(str).str.startswith("C")].copy()
    out["customer_id"] = out["sender_id"]
    out["direction"] = "out"
    out["counterparty_id"] = out["receiver_id"]
    out["signed_amount"] = -out["amount_brl"]

    inc = tx[tx["receiver_id"].astype(str).str.startswith("C")].copy()
    inc["customer_id"] = inc["receiver_id"]
    inc["direction"] = "in"
    inc["counterparty_id"] = inc["sender_id"]
    inc["signed_amount"] = inc["amount_brl"]

    p = pd.concat([out, inc], ignore_index=True)

    flags = {
        "is_sent": p["direction"].eq("out"),
        "is_received": p["direction"].eq("in"),
        "is_pix": p["transaction_type"].eq("PIX"),
        "is_card": p["transaction_type"].eq("Card"),
        "is_wire": p["transaction_type"].eq("Wire"),
        "is_cash_out": p["direction"].eq("out") & p["pix_flow"].eq("cash_out"),
        "is_cash_in": p["direction"].eq("in") & p["pix_flow"].eq("cash_in"),
        "is_cross_border": p["cross_border"].eq("Yes"),
        "is_high_risk_receiver_country": p["country_risk_receiver"].eq("High"),
        "is_high_risk_any_country": p[["country_risk_geo", "country_risk_ip", "country_risk_sender", "country_risk_receiver"]].eq("High").any(axis=1),
        "is_sanctions_tx": p["sanctions_screening_hit"].eq("Yes"),
        "is_high_value_50k": p["amount_brl"].ge(50000),
        "is_ecom_no_3ds": p["transaction_type"].eq("Card") & p["capture_method"].eq("E-commerce") & p["auth_3ds"].eq("No"),
        "is_mcc_high_risk": p["mcc_risk"].eq("High"),
        "is_merchant_high_risk": p["merchant_high_risk_flag"].eq("Yes"),
        "is_ip_anomaly": p["ip_anomaly"].eq("Yes"),
        "is_device_rooted": p["device_rooted"].eq("Yes"),
        "is_round_100": (p["amount_brl"] >= 1000) & (np.isclose(p["amount_brl"] % 100, 0, atol=0.01)),
        "is_round_1000": (p["amount_brl"] >= 1000) & (np.isclose(p["amount_brl"] % 1000, 0, atol=0.01)),
    }
    for name, cond in flags.items():
        p[name] = cond.fillna(False).astype(int)

    d = p.groupby(["customer_id", "month"]).agg(
        tx_count=("transaction_id", "count"),
        total_amount=("amount_brl", "sum"),
        avg_amount=("amount_brl", "mean"),
        median_amount=("amount_brl", "median"),
        std_amount=("amount_brl", "std"),
        max_amount=("amount_brl", "max"),
        net_flow=("signed_amount", "sum"),
        sent_count=("is_sent", "sum"),
        received_count=("is_received", "sum"),
        pix_count=("is_pix", "sum"),
        card_count=("is_card", "sum"),
        wire_count=("is_wire", "sum"),
        cash_out_count=("is_cash_out", "sum"),
        cash_in_count=("is_cash_in", "sum"),
        cross_border_count=("is_cross_border", "sum"),
        high_risk_receiver_country_count=("is_high_risk_receiver_country", "sum"),
        high_risk_any_country_count=("is_high_risk_any_country", "sum"),
        sanctions_tx_count=("is_sanctions_tx", "sum"),
        high_value_50k_count=("is_high_value_50k", "sum"),
        ecom_no_3ds_count=("is_ecom_no_3ds", "sum"),
        mcc_high_risk_count=("is_mcc_high_risk", "sum"),
        merchant_high_risk_count=("is_merchant_high_risk", "sum"),
        ip_anomaly_count=("is_ip_anomaly", "sum"),
        device_rooted_count=("is_device_rooted", "sum"),
        round_100_count=("is_round_100", "sum"),
        round_1000_count=("is_round_1000", "sum"),
        unique_counterparties=("counterparty_id", "nunique"),
    ).reset_index()

    idx = d.set_index(["customer_id", "month"]).index
    d["cash_in_total"] = p[p["is_cash_in"].eq(1)].groupby(["customer_id", "month"])["amount_brl"].sum().reindex(idx).fillna(0).values
    d["cash_out_total"] = p[p["is_cash_out"].eq(1)].groupby(["customer_id", "month"])["amount_brl"].sum().reindex(idx).fillna(0).values
    d["pass_through_ratio"] = np.where(d["total_amount"] > 0, np.abs(d["net_flow"]) / d["total_amount"], np.nan)
    d["pix_share"] = d["pix_count"] / d["tx_count"]
    d["card_share"] = d["card_count"] / d["tx_count"]
    d["wire_share"] = d["wire_count"] / d["tx_count"]
    d["cross_border_share"] = d["cross_border_count"] / d["tx_count"]
    d["mcc_high_risk_share"] = d["mcc_high_risk_count"] / d["tx_count"]
    d["merchant_high_risk_share"] = d["merchant_high_risk_count"] / d["tx_count"]
    d["device_rooted_share"] = d["device_rooted_count"] / d["tx_count"]

    d = d.merge(kyc, on="customer_id", how="left")
    d = d.merge(geo.add_prefix("geo_"), left_on="customer_id", right_on="geo_sender_id", how="left")

    d["period_end"] = pd.to_datetime(d["month"]) + pd.offsets.MonthEnd(0)
    d["date_of_birth"] = pd.to_datetime(d["date_of_birth"], errors="coerce")
    d["registration_date"] = pd.to_datetime(d["registration_date"], errors="coerce")
    d["age"] = ((d["period_end"] - d["date_of_birth"]).dt.days / 365.25).clip(lower=0)
    d["months_since_registration"] = ((d["period_end"] - d["registration_date"]).dt.days / 30.44).clip(lower=0)

    occ_med = d.groupby(["month", "declared_occupation"])["total_amount"].transform("median")
    occ_mean = d.groupby(["month", "declared_occupation"])["total_amount"].transform("mean")
    occ_std = d.groupby(["month", "declared_occupation"])["total_amount"].transform("std")
    d["occupation_month_median_total"] = occ_med
    d["ratio_to_occupation_median_total"] = d["total_amount"] / occ_med.replace(0, np.nan)
    d["zscore_vs_occupation_total"] = (d["total_amount"] - occ_mean) / occ_std.replace(0, np.nan)

    risk_factor = d["risk_rating"].map({"Low": 2.0, "Medium": 1.5, "High": 1.0}).fillna(2.0)
    out_profile_threshold = np.maximum(d["annual_income_brl"].fillna(0) * risk_factor, 20000)

    rules = {
        "r_out_of_profile": d["total_amount"].ge(out_profile_threshold) & d["tx_count"].ge(5),
        "r_pep_activity": d["pep"].eq("Yes") & d["total_amount"].ge(10000),
        "r_sanctions_customer": d["sanctions_list_hit"].eq("Yes"),
        "r_tx_sanctions": d["sanctions_tx_count"].gt(0),
        "r_high_risk_country": d["high_risk_any_country_count"].gt(0),
        "r_cross_border_high_risk": d["cross_border_count"].gt(0) & d["high_risk_any_country_count"].gt(0),
        "r_high_value_50k": d["high_value_50k_count"].gt(0),
        "r_ecom_no_3ds": d["ecom_no_3ds_count"].ge(2),
        "r_mcc_high_risk_concentration": d["mcc_high_risk_count"].ge(3) & d["mcc_high_risk_share"].ge(0.50),
        "r_merchant_high_risk_concentration": d["merchant_high_risk_count"].ge(3) & d["merchant_high_risk_share"].ge(0.40),
        "r_ip_anomaly": d["ip_anomaly_count"].gt(0),
        "r_device_rooted_recurrent": d["device_rooted_count"].ge(2),
        "r_round_values": d["round_100_count"].ge(10),
        "r_many_counterparties": d["unique_counterparties"].ge(25),
        "r_pass_through": d["cash_in_total"].gt(0) & d["cash_out_total"].gt(0) & d["pass_through_ratio"].le(0.20) & d["total_amount"].ge(20000),
        "r_velocity_pass_through": d["cash_out_count"].ge(60) & d["cash_in_count"].ge(9) & d["round_100_count"].ge(10),
        "r_geo_velocity": d["geo_tx_per_day"].ge(1.0),
        "r_high_risk_volume": d["risk_rating"].eq("High") & d["total_amount"].ge(50000),
    }
    rule_cols = []
    for name, cond in rules.items():
        d[name] = cond.fillna(False).astype(int)
        rule_cols.append(name)

    d["rule_count"] = d[rule_cols].sum(axis=1)
    d["suspicious_label"] = d["rule_count"].ge(3).astype(int)
    d["entity_type_model"] = np.where(d["cpf_cnpj"].astype(str).str.len().eq(14), "PJ", "PF")
    return d, rule_cols
