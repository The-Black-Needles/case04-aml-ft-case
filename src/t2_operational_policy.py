from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final


CATALOG_PATH: Final = Path(
    "outputs/t2_alert_system/01_alert_rules_catalog_t2.csv"
)

DEFAULT_OUTPUT_DIR: Final = Path(
    "outputs/t2_alert_system"
)

CSV_FILENAME: Final = (
    "19_rule_operational_policy.csv"
)

SUMMARY_FILENAME: Final = (
    "20_operational_policy_summary.md"
)

MAIN_RULE_IDS: Final = (
    *(f"R{i:02d}" for i in range(1, 17)),
    *(f"M{i:02d}" for i in range(1, 13)),
)

EVENT_OR_CATEGORY_RULES: Final = frozenset(
    {
        "R01",
        "R02",
        "R04",
        "R05",
        "R06",
        "R08",
        "R09",
        "R10",
        "R12",
        "R13",
        "R14",
        "M07",
        "M12",
    }
)

FIXED_NUMERIC_RULES: Final = frozenset(
    {
        "R03",
        "R07",
        "R11",
        "R15",
        "M02",
        "M03",
        "M04",
        "M05",
        "M06",
        "M08",
        "M09",
        "M10",
        "M11",
    }
)

DYNAMIC_ACTIVE_RULES: Final = frozenset(
    {
        "R16",
        "M01",
    }
)

CALIBRATABLE_CANDIDATES: Final = frozenset(
    {
        "R03",
        "R04",
        "R05",
        "R06",
        "R08",
        "R09",
        "R10",
        "R11",
        "R13",
        "R14",
        "R15",
        "M02",
        "M03",
        "M04",
        "M05",
        "M06",
        "M08",
        "M09",
        "M10",
        "M11",
    }
)

BINARY_OR_RELATIONAL_FIXED: Final = frozenset(
    {
        "R01",
        "R02",
        "R12",
        "M07",
        "M12",
    }
)

FIXED_PROTOTYPE_RULES: Final = frozenset(
    {
        "R07",
    }
)

ESCALATE_RULES: Final = frozenset(
    {
        "R01",
        "R02",
        "R12",
        "M07",
        "M12",
    }
)

MONITOR_RULES: Final = frozenset(
    {
        "R06",
        "R10",
        "R13",
        "R14",
    }
)

CONDITIONAL_BLOCK_RULES: Final = frozenset(
    {
        "R01",
        "R02",
        "M07",
    }
)


@dataclass(frozen=True)
class RuleOperationalPolicy:
    rule_id: str
    rule_name: str
    severity: str
    implemented_threshold_mode: str
    calibration_status: str
    recommended_action: str
    conditional_block_eligible: bool
    automatic_block: bool
    human_validation_required: bool
    escalation_condition: str
    policy_note: str


def load_catalog(
    catalog_path: Path = CATALOG_PATH,
) -> dict[str, dict[str, str]]:
    with catalog_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    result = {
        row["rule_id"]: row
        for row in rows
        if row["rule_id"] in MAIN_RULE_IDS
    }

    if set(result) != set(MAIN_RULE_IDS):
        raise RuntimeError(
            "Catálogo não contém exatamente as 28 regras "
            "do motor principal."
        )

    return result


def implemented_threshold_mode(
    rule_id: str,
) -> str:
    if rule_id in DYNAMIC_ACTIVE_RULES:
        return "DYNAMIC_ACTIVE"

    if rule_id in FIXED_NUMERIC_RULES:
        return "FIXED_NUMERIC"

    if rule_id in EVENT_OR_CATEGORY_RULES:
        return "EVENT_OR_CATEGORY"

    raise ValueError(
        f"Regra sem threshold mode: {rule_id}"
    )


def calibration_status(
    rule_id: str,
) -> str:
    if rule_id in DYNAMIC_ACTIVE_RULES:
        return "ACTIVE_DYNAMIC"

    if rule_id in CALIBRATABLE_CANDIDATES:
        return "CALIBRATABLE_CANDIDATE"

    if rule_id in BINARY_OR_RELATIONAL_FIXED:
        return "NOT_APPLICABLE_BINARY_OR_RELATIONAL"

    if rule_id in FIXED_PROTOTYPE_RULES:
        return "FIXED_PROTOTYPE"

    raise ValueError(
        f"Regra sem calibration status: {rule_id}"
    )


def recommended_action(
    rule_id: str,
) -> str:
    if rule_id in ESCALATE_RULES:
        return "ESCALATE"

    if rule_id in MONITOR_RULES:
        return "MONITOR"

    if rule_id in MAIN_RULE_IDS:
        return "REVIEW"

    raise ValueError(
        f"Regra desconhecida: {rule_id}"
    )


def escalation_condition(
    rule_id: str,
) -> str:
    if rule_id in CONDITIONAL_BLOCK_RULES:
        return (
            "Validar evidência crítica em fonte oficial e aplicar "
            "política/jurídico/Compliance antes de qualquer bloqueio."
        )

    if rule_id in MONITOR_RULES:
        return (
            "Escalar para revisão quando houver repetição, materialidade "
            "ou combinação com outros sinais independentes."
        )

    if rule_id in ESCALATE_RULES:
        return (
            "Escalar para investigação especializada; criticidade isolada "
            "não autoriza bloqueio automático."
        )

    return (
        "Revisar contexto, perfil, materialidade e combinação de sinais; "
        "escalar quando a evidência acumulada justificar."
    )


def build_policy(
) -> tuple[RuleOperationalPolicy, ...]:
    catalog = load_catalog()

    policies = tuple(
        RuleOperationalPolicy(
            rule_id=rule_id,
            rule_name=catalog[
                rule_id
            ][
                "rule_name"
            ],
            severity=catalog[
                rule_id
            ][
                "severidade"
            ],
            implemented_threshold_mode=(
                implemented_threshold_mode(
                    rule_id
                )
            ),
            calibration_status=(
                calibration_status(
                    rule_id
                )
            ),
            recommended_action=(
                recommended_action(
                    rule_id
                )
            ),
            conditional_block_eligible=(
                rule_id
                in CONDITIONAL_BLOCK_RULES
            ),
            automatic_block=False,
            human_validation_required=True,
            escalation_condition=(
                escalation_condition(
                    rule_id
                )
            ),
            policy_note=(
                "Política descritiva do protótipo; não altera lógica, "
                "score ou threshold da regra."
            ),
        )
        for rule_id in MAIN_RULE_IDS
    )

    if len(policies) != 28:
        raise RuntimeError(
            "Política operacional deve conter 28 regras."
        )

    return policies


def build_summary(
    policies: tuple[RuleOperationalPolicy, ...],
) -> str:
    mode_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    calibration_counts: dict[str, int] = {}

    for policy in policies:
        mode_counts[
            policy.implemented_threshold_mode
        ] = (
            mode_counts.get(
                policy.implemented_threshold_mode,
                0,
            )
            + 1
        )

        action_counts[
            policy.recommended_action
        ] = (
            action_counts.get(
                policy.recommended_action,
                0,
            )
            + 1
        )

        calibration_counts[
            policy.calibration_status
        ] = (
            calibration_counts.get(
                policy.calibration_status,
                0,
            )
            + 1
        )

    lines = [
        "# T2 — Política operacional das regras",
        "",
        "## Objetivo",
        "",
        (
            "Este artefato normaliza como o protótipo distingue "
            "threshold implementado, potencial de calibragem e ação "
            "operacional recomendada para as 28 regras do motor principal."
        ),
        "",
        (
            "A matriz não altera a lógica das regras, pontuação ou "
            "thresholds existentes."
        ),
        "",
        "## Thresholds implementados",
        "",
        (
            f"- `DYNAMIC_ACTIVE`: "
            f"{mode_counts.get('DYNAMIC_ACTIVE', 0)} regras — "
            "R16 e M01."
        ),
        (
            f"- `FIXED_NUMERIC`: "
            f"{mode_counts.get('FIXED_NUMERIC', 0)} regras."
        ),
        (
            f"- `EVENT_OR_CATEGORY`: "
            f"{mode_counts.get('EVENT_OR_CATEGORY', 0)} regras."
        ),
        "",
        (
            "`DYNAMIC_ACTIVE` significa que o valor efetivamente usado "
            "pelo motor varia de acordo com atributos do cliente. "
            "R16 depende da renda estimada e M01 combina renda e risco."
        ),
        "",
        (
            "Uma regra marcada como `CALIBRATABLE_CANDIDATE` continua "
            "usando o parâmetro fixo/categórico atual. A classificação "
            "apenas registra que uma calibragem futura pode ser testada."
        ),
        "",
        "## Ação operacional normalizada",
        "",
        (
            f"- `MONITOR`: "
            f"{action_counts.get('MONITOR', 0)} regras."
        ),
        (
            f"- `REVIEW`: "
            f"{action_counts.get('REVIEW', 0)} regras."
        ),
        (
            f"- `ESCALATE`: "
            f"{action_counts.get('ESCALATE', 0)} regras."
        ),
        "",
        (
            "`MONITOR` é reservado a sinais contextuais que, isoladamente, "
            "têm maior risco de ruído. Repetição, materialidade ou combinação "
            "com outros sinais pode elevar o caso para revisão."
        ),
        "",
        (
            "`REVIEW` direciona o caso para investigação humana antes de "
            "qualquer decisão material."
        ),
        "",
        (
            "`ESCALATE` é usado para sinais críticos, incluindo sanções e "
            "self-merchant, que exigem tratamento prioritário."
        ),
        "",
        "## Bloqueio",
        "",
        (
            "Nenhuma das 28 regras autoriza bloqueio automático."
        ),
        "",
        (
            "R01, R02 e M07 são `conditional_block_eligible` somente após "
            "validação da evidência crítica em fonte oficial e aplicação "
            "da política interna, jurídico e/ou Compliance."
        ),
        "",
        (
            "R12 e M12 são críticos e devem ser escalados, mas a relação "
            "self-merchant isolada não autoriza bloqueio automático."
        ),
        "",
        "## Limites",
        "",
        "- Base sintética.",
        "- Política operacional experimental.",
        "- Sem homologação produtiva.",
        "- Sem decisão autônoma.",
        "- Revisão humana obrigatória.",
        "",
    ]

    return "\n".join(
        lines
    )


def write_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> tuple[Path, Path]:
    policies = build_policy()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        output_dir
        / CSV_FILENAME
    )

    fieldnames = list(
        asdict(
            policies[0]
        ).keys()
    )

    with csv_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )

        writer.writeheader()

        for policy in policies:
            writer.writerow(
                asdict(
                    policy
                )
            )

    summary_path = (
        output_dir
        / SUMMARY_FILENAME
    )

    summary_path.write_text(
        build_summary(
            policies
        ),
        encoding="utf-8",
    )

    return (
        csv_path,
        summary_path,
    )


def main() -> None:
    for path in write_outputs():
        print(
            f"OUTPUT={path}"
        )


if __name__ == "__main__":
    main()
