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
