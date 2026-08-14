from __future__ import annotations

import itertools
import re
from collections.abc import Sequence

import pandas as pd
from pandas.api.types import is_bool_dtype


SUPPORTED_LEVELS = {
    "transaction": "R",
    "customer_month": "M",
}

SEPARATE_RULE_IDS = frozenset(
    {
        "R17",
    }
)

RULE_ID_PATTERN = re.compile(
    r"^[RM][0-9]{2}$"
)

RULE_HIT_COLUMNS = (
    "rule_id",
    "rule_name",
    "level",
    "observations",
    "hits",
    "hit_rate",
)

COOCCURRENCE_COLUMNS = (
    "rule_a_id",
    "rule_a_name",
    "rule_b_id",
    "rule_b_name",
    "level",
    "hits_a",
    "hits_b",
    "both_hits",
    "union_hits",
    "jaccard",
    "overlap_coefficient",
    "p_a_given_b",
    "p_b_given_a",
)

PRINCIPAL_RAILS = (
    "PIX",
    "Card",
    "Wire",
)

TRANSACTION_RAIL_COLUMNS = (
    "rule_id",
    "rule_name",
    "level",
    "rail",
    "observations",
    "hits",
    "hit_rate",
)

MONTH_RAIL_PRESENCE_COLUMNS = (
    "rule_id",
    "rule_name",
    "level",
    "rail",
    "customer_months",
    "hits",
    "hit_rate",
    "rail_presence_non_exclusive",
)

PRINCIPAL_TRANSACTION_STATUSES = (
    "Confirmed",
    "Pending",
    "Failed",
    "Chargeback",
)

ALERT_LOAD_COLUMNS = (
    "level",
    "observations",
    "alerted_observations",
    "alert_rate",
    "total_rule_hits",
    "mean_rule_hits_per_observation",
    "max_rule_hits_per_observation",
)

RULE_COUNT_DISTRIBUTION_COLUMNS = (
    "level",
    "rule_count",
    "observations",
    "observation_share",
)

TRANSACTION_SEGMENT_LOAD_COLUMNS = (
    "segment",
    "segment_value",
    "observations",
    "alerted_observations",
    "alert_rate",
    "total_rule_hits",
    "mean_rule_hits_per_observation",
    "max_rule_hits_per_observation",
)


def _rule_id(
    rule_name: str,
) -> str:
    if not isinstance(
        rule_name,
        str,
    ):
        raise TypeError(
            "Nome de regra deve ser string."
        )

    if "_" not in rule_name:
        raise ValueError(
            "Nome de regra deve conter ID e descrição."
        )

    identifier = rule_name.split(
        "_",
        1,
    )[0]

    if RULE_ID_PATTERN.fullmatch(
        identifier
    ) is None:
        raise ValueError(
            f"ID de regra inválido: {identifier}"
        )

    return identifier


def _validate_rule_frame(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    level: str,
) -> tuple[str, ...]:
    if level not in SUPPORTED_LEVELS:
        raise ValueError(
            f"Nível de regra não suportado: {level}"
        )

    columns = tuple(
        rule_columns
    )

    if not columns:
        raise ValueError(
            "Ao menos uma coluna de regra é necessária."
        )

    if len(columns) != len(
        set(columns)
    ):
        raise ValueError(
            "Colunas de regra duplicadas não são permitidas."
        )

    expected_prefix = SUPPORTED_LEVELS[
        level
    ]

    identifiers: list[str] = []

    for column in columns:
        identifier = _rule_id(
            column
        )

        if identifier in SEPARATE_RULE_IDS:
            raise ValueError(
                f"{identifier} é regra separada e não integra "
                "o backtesting principal."
            )

        if not identifier.startswith(
            expected_prefix
        ):
            raise ValueError(
                f"{identifier} não pertence ao nível {level}."
            )

        if column not in frame.columns:
            raise ValueError(
                f"Coluna de regra ausente: {column}"
            )

        series = frame[
            column
        ]

        if not is_bool_dtype(
            series.dtype
        ):
            raise TypeError(
                f"Coluna {column} deve ser booleana."
            )

        if series.isna().any():
            raise ValueError(
                f"Coluna {column} contém valores ausentes."
            )

        if identifier in identifiers:
            raise ValueError(
                f"ID de regra duplicado: {identifier}"
            )

        identifiers.append(
            identifier
        )

    return tuple(
        identifiers
    )


def rule_hit_summary(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    level: str,
) -> pd.DataFrame:
    """Resume acionamentos do motor sem alterar sua lógica."""

    identifiers = _validate_rule_frame(
        frame,
        rule_columns,
        level,
    )

    observations = len(
        frame
    )

    rows: list[
        dict[str, object]
    ] = []

    for (
        identifier,
        column,
    ) in zip(
        identifiers,
        rule_columns,
        strict=True,
    ):
        hits = int(
            frame[column].sum()
        )

        hit_rate = (
            hits / observations
            if observations
            else 0.0
        )

        rows.append(
            {
                "rule_id": identifier,
                "rule_name": column,
                "level": level,
                "observations": observations,
                "hits": hits,
                "hit_rate": hit_rate,
            }
        )

    return pd.DataFrame(
        rows,
        columns=RULE_HIT_COLUMNS,
    )


def pairwise_rule_cooccurrence(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    level: str,
) -> pd.DataFrame:
    """Mede coocorrência sem inferir redundância automaticamente."""

    identifiers = _validate_rule_frame(
        frame,
        rule_columns,
        level,
    )

    id_by_column = dict(
        zip(
            rule_columns,
            identifiers,
            strict=True,
        )
    )

    hit_counts = {
        column: int(
            frame[column].sum()
        )
        for column in rule_columns
    }

    rows: list[
        dict[str, object]
    ] = []

    for (
        rule_a,
        rule_b,
    ) in itertools.combinations(
        rule_columns,
        2,
    ):
        hits_a = hit_counts[
            rule_a
        ]
        hits_b = hit_counts[
            rule_b
        ]

        both_hits = int(
            (
                frame[rule_a]
                & frame[rule_b]
            ).sum()
        )

        union_hits = (
            hits_a
            + hits_b
            - both_hits
        )

        minimum_hits = min(
            hits_a,
            hits_b,
        )

        jaccard = (
            both_hits / union_hits
            if union_hits
            else 0.0
        )

        overlap = (
            both_hits / minimum_hits
            if minimum_hits
            else 0.0
        )

        p_a_given_b = (
            both_hits / hits_b
            if hits_b
            else 0.0
        )

        p_b_given_a = (
            both_hits / hits_a
            if hits_a
            else 0.0
        )

        rows.append(
            {
                "rule_a_id": id_by_column[
                    rule_a
                ],
                "rule_a_name": rule_a,
                "rule_b_id": id_by_column[
                    rule_b
                ],
                "rule_b_name": rule_b,
                "level": level,
                "hits_a": hits_a,
                "hits_b": hits_b,
                "both_hits": both_hits,
                "union_hits": union_hits,
                "jaccard": jaccard,
                "overlap_coefficient": overlap,
                "p_a_given_b": p_a_given_b,
                "p_b_given_a": p_b_given_a,
            }
        )

    return pd.DataFrame(
        rows,
        columns=COOCCURRENCE_COLUMNS,
    )

def _validate_transaction_rails(
    frame: pd.DataFrame,
    rail_column: str,
) -> None:
    if rail_column not in frame.columns:
        raise ValueError(
            f"Coluna de rail ausente: {rail_column}"
        )

    rails = frame[
        rail_column
    ]

    if rails.isna().any():
        raise ValueError(
            f"Coluna {rail_column} contém rails ausentes."
        )

    invalid_type = ~rails.map(
        lambda value: isinstance(
            value,
            str,
        )
    )

    if invalid_type.any():
        raise TypeError(
            f"Coluna {rail_column} deve conter strings."
        )

    invalid = sorted(
        set(
            rails.astype(str)
        )
        - set(PRINCIPAL_RAILS)
    )

    if invalid:
        raise ValueError(
            "Rail não suportado no motor principal: "
            + ", ".join(
                invalid
            )
        )


def transaction_rule_rail_summary(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    rail_column: str = "transaction_type",
) -> pd.DataFrame:
    """Resume acionamentos por rail transacional principal."""

    identifiers = _validate_rule_frame(
        frame,
        rule_columns,
        "transaction",
    )

    _validate_transaction_rails(
        frame,
        rail_column,
    )

    rows: list[
        dict[str, object]
    ] = []

    for (
        identifier,
        rule_name,
    ) in zip(
        identifiers,
        rule_columns,
        strict=True,
    ):
        for rail in PRINCIPAL_RAILS:
            rail_mask = frame[
                rail_column
            ].eq(
                rail
            )

            observations = int(
                rail_mask.sum()
            )

            hits = int(
                frame.loc[
                    rail_mask,
                    rule_name,
                ].sum()
            )

            hit_rate = (
                hits / observations
                if observations
                else 0.0
            )

            rows.append(
                {
                    "rule_id": identifier,
                    "rule_name": rule_name,
                    "level": "transaction",
                    "rail": rail,
                    "observations": observations,
                    "hits": hits,
                    "hit_rate": hit_rate,
                }
            )

    return pd.DataFrame(
        rows,
        columns=TRANSACTION_RAIL_COLUMNS,
    )


def _validate_month_rail_counts(
    frame: pd.DataFrame,
    rail_count_columns: dict[str, str],
) -> None:
    if tuple(
        rail_count_columns
    ) != PRINCIPAL_RAILS:
        raise ValueError(
            "Contrato de rails mensal deve seguir "
            "PIX, Card e Wire."
        )

    for (
        rail,
        column,
    ) in rail_count_columns.items():
        if column not in frame.columns:
            raise ValueError(
                f"Coluna de presença do rail {rail} "
                f"ausente: {column}"
            )

        values = frame[
            column
        ]

        if values.isna().any():
            raise ValueError(
                f"Coluna {column} contém valores ausentes."
            )

        numeric = pd.to_numeric(
            values,
            errors="coerce",
        )

        if numeric.isna().any():
            raise TypeError(
                f"Coluna {column} deve ser numérica."
            )

        if numeric.mod(1).ne(0).any():
            raise ValueError(
                f"Coluna {column} contém contagens fracionárias."
            )

        if numeric.lt(0).any():
            raise ValueError(
                f"Coluna {column} contém valores negativos."
            )


def customer_month_rule_rail_presence_summary(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    rail_count_columns: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Mede cobertura mensal por presença não exclusiva de rail."""

    identifiers = _validate_rule_frame(
        frame,
        rule_columns,
        "customer_month",
    )

    mapping = (
        rail_count_columns
        if rail_count_columns is not None
        else {
            "PIX": "pix_count",
            "Card": "card_count",
            "Wire": "wire_count",
        }
    )

    _validate_month_rail_counts(
        frame,
        mapping,
    )

    rows: list[
        dict[str, object]
    ] = []

    for (
        identifier,
        rule_name,
    ) in zip(
        identifiers,
        rule_columns,
        strict=True,
    ):
        for rail in PRINCIPAL_RAILS:
            count_column = mapping[
                rail
            ]

            present = pd.to_numeric(
                frame[
                    count_column
                ],
                errors="raise",
            ).gt(0)

            customer_months = int(
                present.sum()
            )

            hits = int(
                frame.loc[
                    present,
                    rule_name,
                ].sum()
            )

            hit_rate = (
                hits / customer_months
                if customer_months
                else 0.0
            )

            rows.append(
                {
                    "rule_id": identifier,
                    "rule_name": rule_name,
                    "level": "customer_month",
                    "rail": rail,
                    "customer_months": customer_months,
                    "hits": hits,
                    "hit_rate": hit_rate,
                    "rail_presence_non_exclusive": True,
                }
            )

    return pd.DataFrame(
        rows,
        columns=MONTH_RAIL_PRESENCE_COLUMNS,
    )

def _rule_counts(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    level: str,
) -> pd.Series:
    _validate_rule_frame(
        frame,
        rule_columns,
        level,
    )

    return frame.loc[
        :,
        list(rule_columns),
    ].sum(
        axis=1
    ).astype(
        "int64"
    )


def alert_load_summary(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    level: str,
) -> pd.DataFrame:
    """Resume carga operacional sem interpretar mérito do alerta."""

    counts = _rule_counts(
        frame,
        rule_columns,
        level=level,
    )

    observations = len(
        counts
    )

    alerted = int(
        counts.gt(0).sum()
    )

    total_hits = int(
        counts.sum()
    )

    return pd.DataFrame(
        [
            {
                "level": level,
                "observations": observations,
                "alerted_observations": alerted,
                "alert_rate": (
                    alerted / observations
                    if observations
                    else 0.0
                ),
                "total_rule_hits": total_hits,
                "mean_rule_hits_per_observation": (
                    total_hits / observations
                    if observations
                    else 0.0
                ),
                "max_rule_hits_per_observation": (
                    int(counts.max())
                    if observations
                    else 0
                ),
            }
        ],
        columns=ALERT_LOAD_COLUMNS,
    )


def rule_count_distribution(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    level: str,
) -> pd.DataFrame:
    """Distribui observações pelo número de regras acionadas."""

    counts = _rule_counts(
        frame,
        rule_columns,
        level=level,
    )

    observations = len(
        counts
    )

    frequencies = (
        counts
        .value_counts()
        .sort_index()
    )

    rows = [
        {
            "level": level,
            "rule_count": int(rule_count),
            "observations": int(frequency),
            "observation_share": (
                int(frequency) / observations
                if observations
                else 0.0
            ),
        }
        for (
            rule_count,
            frequency,
        ) in frequencies.items()
    ]

    return pd.DataFrame(
        rows,
        columns=RULE_COUNT_DISTRIBUTION_COLUMNS,
    )


def _segment_load_row(
    counts: pd.Series,
    mask: pd.Series,
    *,
    segment: str,
    segment_value: str,
) -> dict[str, object]:
    selected = counts.loc[
        mask
    ]

    observations = len(
        selected
    )

    alerted = int(
        selected.gt(0).sum()
    )

    total_hits = int(
        selected.sum()
    )

    return {
        "segment": segment,
        "segment_value": segment_value,
        "observations": observations,
        "alerted_observations": alerted,
        "alert_rate": (
            alerted / observations
            if observations
            else 0.0
        ),
        "total_rule_hits": total_hits,
        "mean_rule_hits_per_observation": (
            total_hits / observations
            if observations
            else 0.0
        ),
        "max_rule_hits_per_observation": (
            int(selected.max())
            if observations
            else 0
        ),
    }


def transaction_alert_load_by_rail(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    rail_column: str = "transaction_type",
) -> pd.DataFrame:
    """Mede carga agregada por rail sem alterar o motor."""

    counts = _rule_counts(
        frame,
        rule_columns,
        level="transaction",
    )

    _validate_transaction_rails(
        frame,
        rail_column,
    )

    rows = [
        _segment_load_row(
            counts,
            frame[
                rail_column
            ].eq(
                rail
            ),
            segment="rail",
            segment_value=rail,
        )
        for rail in PRINCIPAL_RAILS
    ]

    return pd.DataFrame(
        rows,
        columns=TRANSACTION_SEGMENT_LOAD_COLUMNS,
    )


def _validate_transaction_statuses(
    frame: pd.DataFrame,
    status_column: str,
) -> None:
    if status_column not in frame.columns:
        raise ValueError(
            f"Coluna de status ausente: {status_column}"
        )

    values = frame[
        status_column
    ]

    if values.isna().any():
        raise ValueError(
            f"Coluna {status_column} contém status ausentes."
        )

    invalid_type = ~values.map(
        lambda value: isinstance(
            value,
            str,
        )
    )

    if invalid_type.any():
        raise TypeError(
            f"Coluna {status_column} deve conter strings."
        )

    invalid = sorted(
        set(
            values.astype(str)
        )
        - set(
            PRINCIPAL_TRANSACTION_STATUSES
        )
    )

    if invalid:
        raise ValueError(
            "Status transacional não suportado: "
            + ", ".join(
                invalid
            )
        )


def transaction_alert_load_by_status(
    frame: pd.DataFrame,
    rule_columns: Sequence[str],
    *,
    status_column: str = "status",
) -> pd.DataFrame:
    """Segmenta carga por status; status não é ground truth."""

    counts = _rule_counts(
        frame,
        rule_columns,
        level="transaction",
    )

    _validate_transaction_statuses(
        frame,
        status_column,
    )

    rows = [
        _segment_load_row(
            counts,
            frame[
                status_column
            ].eq(
                status_value
            ),
            segment="status",
            segment_value=status_value,
        )
        for status_value
        in PRINCIPAL_TRANSACTION_STATUSES
    ]

    return pd.DataFrame(
        rows,
        columns=TRANSACTION_SEGMENT_LOAD_COLUMNS,
    )
