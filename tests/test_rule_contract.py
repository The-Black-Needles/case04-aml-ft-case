from __future__ import annotations

import ast
import csv
import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]

RULES_PATH = ROOT / "src" / "rules.py"
ALERTS_PATH = ROOT / "src" / "alerts.py"
T2_CATALOG_PATH = (
    ROOT
    / "outputs"
    / "t2_alert_system"
    / "01_alert_rules_catalog_t2.csv"
)

EXPECTED_TRANSACTION_IDS = tuple(
    f"R{index:02d}"
    for index in range(1, 17)
)

EXPECTED_MONTH_IDS = tuple(
    f"M{index:02d}"
    for index in range(1, 13)
)

EXPECTED_PRINCIPAL_IDS = (
    EXPECTED_TRANSACTION_IDS
    + EXPECTED_MONTH_IDS
)


def load_alerts_module() -> ModuleType:
    specification = (
        importlib.util.spec_from_file_location(
            "case04_alert_rule_contract",
            ALERTS_PATH,
        )
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Não foi possível carregar {ALERTS_PATH}"
        )

    module = importlib.util.module_from_spec(
        specification
    )

    sys.modules[
        specification.name
    ] = module

    specification.loader.exec_module(
        module
    )

    return module


def engine_rule_ids() -> tuple[str, ...]:
    tree = ast.parse(
        RULES_PATH.read_text(
            encoding="utf-8",
        )
    )

    identifiers: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Name):
            continue

        if node.func.id not in {"rule", "mr"}:
            continue

        if not node.args:
            continue

        first_argument = node.args[0]

        if not isinstance(
            first_argument,
            ast.Constant,
        ):
            continue

        if not isinstance(
            first_argument.value,
            str,
        ):
            continue

        identifiers.append(
            first_argument.value.split(
                "_",
                1,
            )[0]
        )

    return tuple(identifiers)


def t2_catalog_rows() -> list[dict[str, str]]:
    with T2_CATALOG_PATH.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


ALERTS = load_alerts_module()


class RuleContractTests(unittest.TestCase):
    def test_principal_engine_has_exact_28_rules(
        self,
    ) -> None:
        self.assertEqual(
            engine_rule_ids(),
            EXPECTED_PRINCIPAL_IDS,
        )

        self.assertEqual(
            len(EXPECTED_PRINCIPAL_IDS),
            28,
        )

    def test_r17_is_not_in_principal_engine(
        self,
    ) -> None:
        self.assertNotIn(
            "R17",
            engine_rule_ids(),
        )

    def test_alert_metadata_matches_principal_engine(
        self,
    ) -> None:
        metadata_ids = tuple(
            rule.rule_id
            for rule in ALERTS.ALERT_RULES
        )

        self.assertEqual(
            metadata_ids,
            EXPECTED_PRINCIPAL_IDS,
        )

        self.assertEqual(
            len(metadata_ids),
            len(set(metadata_ids)),
        )

    def test_alert_metadata_required_fields_are_present(
        self,
    ) -> None:
        for rule in ALERTS.ALERT_RULES:
            with self.subTest(
                rule_id=rule.rule_id,
            ):
                self.assertTrue(
                    rule.name.strip()
                )
                self.assertTrue(
                    rule.level.strip()
                )
                self.assertTrue(
                    rule.severity.strip()
                )
                self.assertGreater(
                    rule.points,
                    0,
                )
                self.assertTrue(
                    rule.typology.strip()
                )
                self.assertTrue(
                    rule.logic.strip()
                )
                self.assertTrue(
                    rule.parameters.strip()
                )
                self.assertIsInstance(
                    rule.dynamic_threshold,
                    bool,
                )

    def test_alert_levels_match_rule_family(
        self,
    ) -> None:
        levels = {
            rule.rule_id: rule.level
            for rule in ALERTS.ALERT_RULES
        }

        for rule_id in EXPECTED_TRANSACTION_IDS:
            with self.subTest(
                rule_id=rule_id,
            ):
                self.assertEqual(
                    levels[rule_id],
                    "transaction",
                )

        for rule_id in EXPECTED_MONTH_IDS:
            with self.subTest(
                rule_id=rule_id,
            ):
                self.assertEqual(
                    levels[rule_id],
                    "customer_month",
                )

    def test_t2_catalog_contains_principal_rules_plus_r17(
        self,
    ) -> None:
        catalog_ids = tuple(
            row["rule_id"]
            for row in t2_catalog_rows()
        )

        self.assertEqual(
            tuple(
                rule_id
                for rule_id in catalog_ids
                if rule_id != "R17"
            ),
            EXPECTED_PRINCIPAL_IDS,
        )

        self.assertEqual(
            catalog_ids.count("R17"),
            1,
        )

    def test_r17_is_documented_as_separate_catalog_rule(
        self,
    ) -> None:
        row = next(
            row
            for row in t2_catalog_rows()
            if row["rule_id"] == "R17"
        )

        self.assertEqual(
            row["rule_name"],
            "R17_tx_geo_jump_impossible_travel",
        )

        self.assertTrue(
            row["logica"].strip()
        )

        self.assertTrue(
            row["parametros"].strip()
        )

    def test_t2_catalog_has_governance_fields(
        self,
    ) -> None:
        required_columns = {
            "rule_id",
            "rule_name",
            "nome_pt",
            "nivel",
            "tipologia",
            "rail_aplicavel",
            "severidade",
            "pontos",
            "logica",
            "parametros",
            "limiar_dinamico",
            "qtd_acionamentos_base",
            "exemplo_id",
            "exemplo_na_base",
            "justificativa",
            "acao_operacional",
            "controle_falso_positivo",
        }

        rows = t2_catalog_rows()

        self.assertTrue(rows)

        self.assertTrue(
            required_columns.issubset(
                rows[0].keys()
            )
        )

        for row in rows:
            with self.subTest(
                rule_id=row["rule_id"],
            ):
                for column in required_columns:
                    self.assertTrue(
                        row[column].strip(),
                        (
                            f"{row['rule_id']} sem "
                            f"conteúdo em {column}"
                        ),
                    )


if __name__ == "__main__":
    unittest.main()
