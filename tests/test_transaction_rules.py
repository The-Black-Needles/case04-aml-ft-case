from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "src" / "rules.py"

EXPECTED_TRANSACTION_RULES = tuple(
    f"R{index:02d}"
    for index in range(1, 17)
)


def load_rules_module() -> ModuleType:
    specification = (
        importlib.util.spec_from_file_location(
            "case04_transaction_rule_tests",
            RULES_PATH,
        )
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Não foi possível carregar {RULES_PATH}"
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


RULES = load_rules_module()


def neutral_row() -> dict[str, object]:
    return {
        "sanctions_screening_hit": "No",
        "kyc_sanctions_list_hit": "No",
        "kyc_pep": "No",
        "cross_border": "No",
        "amount_brl": 100.0,
        "country_risk_receiver": "Low",
        "transaction_type": "PIX",
        "country_risk_geo": "Low",
        "country_risk_ip": "Low",
        "country_risk_sender": "Low",
        "capture_method": "App",
        "card_present": "Yes",
        "auth_3ds": "Yes",
        "status": "Confirmed",
        "merchant_mcc_risk": "Low",
        "merchant_merchant_high_risk_flag": "No",
        "merchant_merchant_chargeback_ratio_90d": 0.01,
        "subject_customer_id": "C001",
        "merchant_owner_customer_id": "C002",
        "ip_anomaly": "No",
        "ip_proxy_vpn_tor": "None",
        "device_rooted": "No",
        "near_10k": False,
        "monthly_income_est": 10000.0,
    }


POSITIVE_CASES: dict[
    str,
    dict[str, object],
] = {
    "R01": {
        "sanctions_screening_hit": "Yes",
    },
    "R02": {
        "kyc_sanctions_list_hit": "Yes",
    },
    "R03": {
        "kyc_pep": "Yes",
        "cross_border": "Yes",
    },
    "R04": {
        "transaction_type": "Wire",
        "country_risk_receiver": "High",
    },
    "R05": {
        "cross_border": "Yes",
        "country_risk_receiver": "High",
    },
    "R06": {
        "country_risk_ip": "High",
    },
    "R07": {
        "amount_brl": 50000.0,
        "monthly_income_est": 100000.0,
    },
    "R08": {
        "transaction_type": "Card",
        "capture_method": "E-commerce",
        "card_present": "No",
        "auth_3ds": "No",
    },
    "R09": {
        "status": "Chargeback",
    },
    "R10": {
        "merchant_mcc_risk": "High",
    },
    "R11": {
        "merchant_merchant_high_risk_flag": "Yes",
    },
    "R12": {
        "subject_customer_id": "C001",
        "merchant_owner_customer_id": "C001",
    },
    "R13": {
        "ip_anomaly": "Yes",
    },
    "R14": {
        "device_rooted": "Yes",
    },
    "R15": {
        "amount_brl": 9500.0,
        "near_10k": True,
    },
    "R16": {
        "amount_brl": 20000.0,
        "monthly_income_est": 10000.0,
    },
}


NEGATIVE_CASES: dict[
    str,
    dict[str, object],
] = {
    "R01": {
        "sanctions_screening_hit": "No",
    },
    "R02": {
        "kyc_sanctions_list_hit": "No",
    },
    "R03": {
        "kyc_pep": "Yes",
        "cross_border": "No",
        "amount_brl": 9999.99,
        "country_risk_receiver": "Low",
    },
    "R04": {
        "transaction_type": "Wire",
        "country_risk_receiver": "Low",
    },
    "R05": {
        "cross_border": "Yes",
        "country_risk_receiver": "Low",
    },
    "R06": {
        "country_risk_geo": "Low",
        "country_risk_ip": "Low",
        "country_risk_sender": "Low",
    },
    "R07": {
        "amount_brl": 49999.99,
        "monthly_income_est": 100000.0,
    },
    "R08": {
        "transaction_type": "Card",
        "capture_method": "E-commerce",
        "card_present": "No",
        "auth_3ds": "Yes",
    },
    "R09": {
        "status": "Confirmed",
    },
    "R10": {
        "merchant_mcc_risk": "Low",
    },
    "R11": {
        "merchant_merchant_high_risk_flag": "No",
        "merchant_merchant_chargeback_ratio_90d": 0.0799,
    },
    "R12": {
        "subject_customer_id": "C001",
        "merchant_owner_customer_id": "C002",
    },
    "R13": {
        "ip_anomaly": "No",
        "ip_proxy_vpn_tor": "None",
    },
    "R14": {
        "device_rooted": "No",
    },
    "R15": {
        "amount_brl": 8999.99,
        "near_10k": False,
    },
    "R16": {
        "amount_brl": 19999.99,
        "monthly_income_est": 10000.0,
    },
}


def evaluate(
    modifications: dict[str, object],
) -> tuple[pd.Series, pd.DataFrame]:
    row = neutral_row()
    row.update(modifications)

    evaluated, catalog = RULES.add_rules(
        pd.DataFrame([row])
    )

    return (
        evaluated.iloc[0],
        catalog,
    )


def rule_column(
    rule_id: str,
    catalog: pd.DataFrame,
) -> str:
    matches = catalog.loc[
        catalog["rule_id"].eq(rule_id),
        "rule_name",
    ]

    if len(matches) != 1:
        raise AssertionError(
            f"Regra {rule_id} não encontrada "
            "exatamente uma vez no catálogo"
        )

    return str(
        matches.iloc[0]
    )


class TransactionRuleBehaviorTests(
    unittest.TestCase
):
    def test_fixture_contract_covers_all_transaction_rules(
        self,
    ) -> None:
        self.assertEqual(
            tuple(POSITIVE_CASES),
            EXPECTED_TRANSACTION_RULES,
        )

        self.assertEqual(
            tuple(NEGATIVE_CASES),
            EXPECTED_TRANSACTION_RULES,
        )

    def test_neutral_fixture_triggers_no_transaction_rule(
        self,
    ) -> None:
        row, catalog = evaluate({})

        columns = [
            rule_column(
                rule_id,
                catalog,
            )
            for rule_id in EXPECTED_TRANSACTION_RULES
        ]

        triggered = [
            column
            for column in columns
            if bool(row[column])
        ]

        self.assertEqual(
            triggered,
            [],
        )

        self.assertEqual(
            int(row["tx_rule_count"]),
            0,
        )

        self.assertEqual(
            float(row["tx_rule_score"]),
            0.0,
        )

    def test_positive_case_for_every_transaction_rule(
        self,
    ) -> None:
        for (
            rule_id,
            modifications,
        ) in POSITIVE_CASES.items():
            with self.subTest(
                rule_id=rule_id,
            ):
                row, catalog = evaluate(
                    modifications
                )

                column = rule_column(
                    rule_id,
                    catalog,
                )

                self.assertTrue(
                    bool(row[column]),
                    (
                        f"{rule_id} deveria disparar "
                        f"com {modifications}"
                    ),
                )

    def test_negative_case_for_every_transaction_rule(
        self,
    ) -> None:
        for (
            rule_id,
            modifications,
        ) in NEGATIVE_CASES.items():
            with self.subTest(
                rule_id=rule_id,
            ):
                row, catalog = evaluate(
                    modifications
                )

                column = rule_column(
                    rule_id,
                    catalog,
                )

                self.assertFalse(
                    bool(row[column]),
                    (
                        f"{rule_id} não deveria disparar "
                        f"com {modifications}"
                    ),
                )

    def test_alternative_rule_branches_are_explicit(
        self,
    ) -> None:
        alternate_positive_cases = (
            (
                "R03_high_value",
                "R03",
                {
                    "kyc_pep": "Yes",
                    "amount_brl": 10000.0,
                },
            ),
            (
                "R03_high_risk_receiver",
                "R03",
                {
                    "kyc_pep": "Yes",
                    "country_risk_receiver": "High",
                },
            ),
            (
                "R06_geo",
                "R06",
                {
                    "country_risk_geo": "High",
                },
            ),
            (
                "R06_sender",
                "R06",
                {
                    "country_risk_sender": "High",
                },
            ),
            (
                "R11_ratio",
                "R11",
                {
                    "merchant_merchant_high_risk_flag": "No",
                    "merchant_merchant_chargeback_ratio_90d": 0.08,
                },
            ),
            (
                "R13_proxy",
                "R13",
                {
                    "ip_proxy_vpn_tor": "Proxy",
                },
            ),
            (
                "R13_vpn",
                "R13",
                {
                    "ip_proxy_vpn_tor": "VPN",
                },
            ),
            (
                "R13_tor",
                "R13",
                {
                    "ip_proxy_vpn_tor": "Tor",
                },
            ),
            (
                "R16_absolute_floor",
                "R16",
                {
                    "amount_brl": 10000.0,
                    "monthly_income_est": 4000.0,
                },
            ),
        )

        for (
            label,
            rule_id,
            modifications,
        ) in alternate_positive_cases:
            with self.subTest(
                case=label,
            ):
                row, catalog = evaluate(
                    modifications
                )

                triggered = [
                    candidate_id
                    for candidate_id
                    in EXPECTED_TRANSACTION_RULES
                    if bool(
                        row[
                            rule_column(
                                candidate_id,
                                catalog,
                            )
                        ]
                    )
                ]

                self.assertEqual(
                    triggered,
                    [rule_id],
                )

        row, catalog = evaluate(
            {
                "amount_brl": 9999.99,
                "monthly_income_est": 4000.0,
            }
        )

        self.assertFalse(
            bool(
                row[
                    rule_column(
                        "R16",
                        catalog,
                    )
                ]
            )
        )

    def test_r15_uses_precomputed_near_10k_flag(
        self,
    ) -> None:
        for amount in (
            100.0,
            9500.0,
            15000.0,
        ):
            with self.subTest(
                amount_brl=amount,
            ):
                row, catalog = evaluate(
                    {
                        "amount_brl": amount,
                        "near_10k": True,
                    }
                )

                triggered = [
                    rule_id
                    for rule_id
                    in EXPECTED_TRANSACTION_RULES
                    if bool(
                        row[
                            rule_column(
                                rule_id,
                                catalog,
                            )
                        ]
                    )
                ]

                self.assertEqual(
                    triggered,
                    ["R15"],
                )

        row, catalog = evaluate(
            {
                "amount_brl": 9500.0,
                "near_10k": False,
            }
        )

        self.assertFalse(
            bool(
                row[
                    rule_column(
                        "R15",
                        catalog,
                    )
                ]
            )
        )

    def test_threshold_and_proxy_cases_are_explicit(
        self,
    ) -> None:
        expected_boundaries = {
            "R07": (
                50000.0,
                49999.99,
            ),
            "R11": (
                0.08,
                0.0799,
            ),
            "R15": (
                True,
                False,
            ),
            "R16": (
                20000.0,
                19999.99,
            ),
        }

        self.assertEqual(
            POSITIVE_CASES["R07"]["amount_brl"],
            expected_boundaries["R07"][0],
        )
        self.assertEqual(
            NEGATIVE_CASES["R07"]["amount_brl"],
            expected_boundaries["R07"][1],
        )

        positive_r11 = dict(
            POSITIVE_CASES["R11"]
        )
        positive_r11[
            "merchant_merchant_high_risk_flag"
        ] = "No"
        positive_r11[
            "merchant_merchant_chargeback_ratio_90d"
        ] = expected_boundaries["R11"][0]

        row, catalog = evaluate(
            positive_r11
        )

        self.assertTrue(
            bool(
                row[
                    rule_column(
                        "R11",
                        catalog,
                    )
                ]
            )
        )

        self.assertEqual(
            NEGATIVE_CASES["R11"][
                "merchant_merchant_chargeback_ratio_90d"
            ],
            expected_boundaries["R11"][1],
        )

        self.assertEqual(
            POSITIVE_CASES["R15"]["near_10k"],
            expected_boundaries["R15"][0],
        )
        self.assertEqual(
            NEGATIVE_CASES["R15"]["near_10k"],
            expected_boundaries["R15"][1],
        )

        self.assertEqual(
            POSITIVE_CASES["R16"]["amount_brl"],
            expected_boundaries["R16"][0],
        )
        self.assertEqual(
            NEGATIVE_CASES["R16"]["amount_brl"],
            expected_boundaries["R16"][1],
        )


if __name__ == "__main__":
    unittest.main()
