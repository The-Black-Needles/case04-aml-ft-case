from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "src" / "rules.py"

EXPECTED_MONTH_RULES = tuple(
    f"M{index:02d}"
    for index in range(1, 13)
)


def load_rules_module() -> ModuleType:
    specification = (
        importlib.util.spec_from_file_location(
            "case04_month_rule_tests",
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


def customer_row(
    **modifications: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        "customer_id": "C001",
        "full_name": "Synthetic Customer",
        "cpf_cnpj": "00000000000",
        "annual_income_brl": 600000.0,
        "risk_rating": "Low",
        "pep": "No",
        "kyc_tier": "Standard",
        "kyc_risk_score": 10,
        "sanctions_list_hit": "No",
        "declared_occupation": "Analyst",
        "date_of_birth": "1990-01-01",
        "registration_date": "2025-01-01",
        "state": "SP",
        "city": "Campinas",
        "beneficial_owner": None,
    }

    row.update(modifications)

    return row


def transaction_row(
    index: int,
    amount_brl: float = 100.0,
    **modifications: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        "customer_id": "C001",
        "month": "2025-07",
        "transaction_id": f"T{index:03d}",
        "is_confirmed": 1,
        "amount_brl": float(amount_brl),
        "dir_in": 0,
        "dir_out": 0,
        "amt_in": 0.0,
        "amt_out": 0.0,
        "is_pix": 1,
        "is_card": 0,
        "is_wire": 0,
        "is_crossborder": 0,
        "is_high_receiver": 0,
        "is_sanctions_tx": 0,
        "is_high_mcc": 0,
        "is_high_merchant": 0,
        "R08_card_ecommerce_without_3ds": 0,
        "is_chargeback": 0,
        "R13_ip_anomaly_or_proxy_tor_vpn": 0,
        "R14_rooted_device": 0,
        "near_10k": 0,
        "R12_self_merchant": 0,
        "tx_rule_score": 0.0,
        "receiver_id": f"CP{index:03d}",
    }

    row.update(modifications)

    return row


def rows_with_total(
    amounts: list[float],
) -> list[dict[str, object]]:
    return [
        transaction_row(
            index,
            amount,
        )
        for index, amount in enumerate(
            amounts,
            start=1,
        )
    ]


def monthly_case(
    rule_id: str,
    *,
    positive: bool,
) -> tuple[
    list[dict[str, object]],
    dict[str, object],
]:
    customer = customer_row()

    if rule_id == "M01":
        customer = customer_row(
            annual_income_brl=120000.0,
            risk_rating="Low",
        )

        amount = (
            20000.0
            if positive
            else 19999.99
        )

        return (
            [
                transaction_row(
                    1,
                    amount,
                )
            ],
            customer,
        )

    if rule_id == "M02":
        if positive:
            amounts = (
                [3000.0] * 14
                + [8000.0]
            )
        else:
            amounts = (
                [3000.0] * 13
                + [11000.0]
            )

        return (
            rows_with_total(amounts),
            customer,
        )

    if rule_id == "M03":
        count = (
            3
            if positive
            else 2
        )

        rows = [
            transaction_row(
                index,
                9500.0,
                near_10k=1,
            )
            for index in range(
                1,
                count + 1,
            )
        ]

        return rows, customer

    if rule_id == "M04":
        rows = [
            transaction_row(
                1,
                5000.0,
                dir_in=1,
                amt_in=5000.0,
            ),
            transaction_row(
                2,
                5000.0,
                dir_in=1,
                amt_in=5000.0,
            ),
        ]

        if positive:
            for index in range(
                3,
                8,
            ):
                rows.append(
                    transaction_row(
                        index,
                        2000.0,
                        dir_out=1,
                        amt_out=2000.0,
                    )
                )
        else:
            for index in range(
                3,
                7,
            ):
                rows.append(
                    transaction_row(
                        index,
                        2500.0,
                        dir_out=1,
                        amt_out=2500.0,
                    )
                )

        return rows, customer

    if rule_id == "M05":
        rows = [
            transaction_row(
                index,
                100.0,
                is_crossborder=(
                    1
                    if index <= (
                        3
                        if positive
                        else 2
                    )
                    else 0
                ),
            )
            for index in range(
                1,
                11,
            )
        ]

        return rows, customer

    if rule_id == "M06":
        count = (
            2
            if positive
            else 1
        )

        rows = [
            transaction_row(
                index,
                100.0,
                is_high_receiver=(
                    1
                    if index <= count
                    else 0
                ),
            )
            for index in range(
                1,
                3,
            )
        ]

        return rows, customer

    if rule_id == "M07":
        rows = [
            transaction_row(
                1,
                100.0,
                is_sanctions_tx=(
                    1
                    if positive
                    else 0
                ),
            )
        ]

        return rows, customer

    if rule_id == "M08":
        customer = customer_row(
            pep=(
                "Yes"
                if positive
                else "No"
            )
        )

        return (
            [
                transaction_row(
                    1,
                    50000.0,
                )
            ],
            customer,
        )

    if rule_id == "M09":
        count = (
            5
            if positive
            else 4
        )

        rows = [
            transaction_row(
                index,
                100.0,
                is_high_mcc=1,
            )
            for index in range(
                1,
                count + 1,
            )
        ]

        return rows, customer

    if rule_id == "M10":
        count = (
            2
            if positive
            else 1
        )

        rows = [
            transaction_row(
                index,
                100.0,
                R08_card_ecommerce_without_3ds=1,
            )
            for index in range(
                1,
                count + 1,
            )
        ]

        return rows, customer

    if rule_id == "M11":
        count = (
            3
            if positive
            else 2
        )

        rows = [
            transaction_row(
                index,
                100.0,
                R13_ip_anomaly_or_proxy_tor_vpn=1,
            )
            for index in range(
                1,
                count + 1,
            )
        ]

        return rows, customer

    if rule_id == "M12":
        return (
            [
                transaction_row(
                    1,
                    100.0,
                    R12_self_merchant=(
                        1
                        if positive
                        else 0
                    ),
                )
            ],
            customer,
        )

    raise ValueError(
        f"Regra mensal desconhecida: {rule_id}"
    )


def evaluate(
    transactions: list[dict[str, object]],
    customer: dict[str, object],
) -> tuple[pd.Series, pd.DataFrame]:
    evaluated, catalog = RULES.month_alerts(
        pd.DataFrame(transactions),
        pd.DataFrame([customer]),
    )

    if len(evaluated) != 1:
        raise AssertionError(
            "Fixture deve produzir exatamente "
            "um customer-month"
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
            "exatamente uma vez"
        )

    return str(
        matches.iloc[0]
    )


def triggered_rule_ids(
    row: pd.Series,
    catalog: pd.DataFrame,
) -> list[str]:
    return [
        rule_id
        for rule_id in EXPECTED_MONTH_RULES
        if bool(
            row[
                rule_column(
                    rule_id,
                    catalog,
                )
            ]
        )
    ]


class MonthRuleBehaviorTests(
    unittest.TestCase
):
    def test_month_catalog_contract_is_exact(
        self,
    ) -> None:
        transactions, customer = monthly_case(
            "M01",
            positive=False,
        )

        _, catalog = evaluate(
            transactions,
            customer,
        )

        self.assertEqual(
            tuple(
                catalog["rule_id"]
            ),
            EXPECTED_MONTH_RULES,
        )

        self.assertEqual(
            tuple(
                catalog["level"]
            ),
            (
                "customer_month",
            ) * 12,
        )

        self.assertEqual(
            len(
                set(
                    catalog["rule_id"]
                )
            ),
            12,
        )

    def test_neutral_month_triggers_no_rule(
        self,
    ) -> None:
        row, catalog = evaluate(
            [
                transaction_row(
                    1,
                    100.0,
                )
            ],
            customer_row(),
        )

        self.assertEqual(
            triggered_rule_ids(
                row,
                catalog,
            ),
            [],
        )

        self.assertEqual(
            int(
                row[
                    "month_rule_count"
                ]
            ),
            0,
        )

        self.assertEqual(
            float(
                row[
                    "month_rule_score"
                ]
            ),
            0.0,
        )

    def test_positive_case_for_every_month_rule(
        self,
    ) -> None:
        for rule_id in EXPECTED_MONTH_RULES:
            with self.subTest(
                rule_id=rule_id,
            ):
                transactions, customer = (
                    monthly_case(
                        rule_id,
                        positive=True,
                    )
                )

                row, catalog = evaluate(
                    transactions,
                    customer,
                )

                triggered = (
                    triggered_rule_ids(
                        row,
                        catalog,
                    )
                )

                self.assertEqual(
                    triggered,
                    [rule_id],
                )

                self.assertEqual(
                    int(
                        row[
                            "month_rule_count"
                        ]
                    ),
                    1,
                )

                points = int(
                    catalog.loc[
                        catalog[
                            "rule_id"
                        ].eq(rule_id),
                        "points",
                    ].iloc[0]
                )

                self.assertEqual(
                    float(
                        row[
                            "month_rule_score"
                        ]
                    ),
                    float(points),
                )

    def test_negative_case_for_every_month_rule(
        self,
    ) -> None:
        for rule_id in EXPECTED_MONTH_RULES:
            with self.subTest(
                rule_id=rule_id,
            ):
                transactions, customer = (
                    monthly_case(
                        rule_id,
                        positive=False,
                    )
                )

                row, catalog = evaluate(
                    transactions,
                    customer,
                )

                self.assertEqual(
                    triggered_rule_ids(
                        row,
                        catalog,
                    ),
                    [],
                )

    def test_m01_dynamic_thresholds_are_explicit(
        self,
    ) -> None:
        cases = (
            (
                "low_floor",
                120000.0,
                "Low",
                20000.0,
                19999.99,
            ),
            (
                "medium_factor",
                240000.0,
                "Medium",
                30000.0,
                29999.99,
            ),
            (
                "high_factor",
                360000.0,
                "High",
                30000.0,
                29999.99,
            ),
        )

        for (
            label,
            annual_income,
            risk_rating,
            at_threshold,
            below_threshold,
        ) in cases:
            with self.subTest(
                case=label,
            ):
                customer = customer_row(
                    annual_income_brl=annual_income,
                    risk_rating=risk_rating,
                )

                positive_row, catalog = evaluate(
                    [
                        transaction_row(
                            1,
                            at_threshold,
                        )
                    ],
                    customer,
                )

                self.assertEqual(
                    triggered_rule_ids(
                        positive_row,
                        catalog,
                    ),
                    ["M01"],
                )

                negative_row, catalog = evaluate(
                    [
                        transaction_row(
                            1,
                            below_threshold,
                        )
                    ],
                    customer,
                )

                self.assertNotIn(
                    "M01",
                    triggered_rule_ids(
                        negative_row,
                        catalog,
                    ),
                )

    def test_m07_has_two_independent_paths(
        self,
    ) -> None:
        transaction_path_row, catalog = evaluate(
            [
                transaction_row(
                    1,
                    100.0,
                    is_sanctions_tx=1,
                )
            ],
            customer_row(
                sanctions_list_hit="No",
            ),
        )

        self.assertEqual(
            triggered_rule_ids(
                transaction_path_row,
                catalog,
            ),
            ["M07"],
        )

        customer_path_row, catalog = evaluate(
            [
                transaction_row(
                    1,
                    100.0,
                    is_sanctions_tx=0,
                )
            ],
            customer_row(
                sanctions_list_hit="Yes",
            ),
        )

        self.assertEqual(
            triggered_rule_ids(
                customer_path_row,
                catalog,
            ),
            ["M07"],
        )

    def test_selected_boundaries_are_explicit(
        self,
    ) -> None:
        m02_positive, catalog = evaluate(
            rows_with_total(
                [3000.0] * 14
                + [8000.0]
            ),
            customer_row(),
        )

        self.assertIn(
            "M02",
            triggered_rule_ids(
                m02_positive,
                catalog,
            ),
        )

        m02_amount_below, catalog = evaluate(
            rows_with_total(
                [3000.0] * 14
                + [7999.99]
            ),
            customer_row(),
        )

        self.assertNotIn(
            "M02",
            triggered_rule_ids(
                m02_amount_below,
                catalog,
            ),
        )

        m04_ratio_at_rows = [
            transaction_row(
                1,
                5000.0,
                dir_in=1,
                amt_in=5000.0,
            ),
            transaction_row(
                2,
                5000.0,
                dir_in=1,
                amt_in=5000.0,
            ),
        ]

        for index in range(
            3,
            8,
        ):
            m04_ratio_at_rows.append(
                transaction_row(
                    index,
                    1400.0,
                    dir_out=1,
                    amt_out=1400.0,
                )
            )

        m04_ratio_at_rows.append(
            transaction_row(
                8,
                3000.0,
            )
        )

        m04_ratio_at, catalog = evaluate(
            m04_ratio_at_rows,
            customer_row(),
        )

        self.assertIn(
            "M04",
            triggered_rule_ids(
                m04_ratio_at,
                catalog,
            ),
        )

        m05_at_rows = [
            transaction_row(
                index,
                100.0,
                is_crossborder=(
                    1
                    if index <= 3
                    else 0
                ),
            )
            for index in range(
                1,
                11,
            )
        ]

        m05_at, catalog = evaluate(
            m05_at_rows,
            customer_row(),
        )

        self.assertIn(
            "M05",
            triggered_rule_ids(
                m05_at,
                catalog,
            ),
        )

        m05_below_rows = [
            transaction_row(
                index,
                100.0,
                is_crossborder=(
                    1
                    if index <= 3
                    else 0
                ),
            )
            for index in range(
                1,
                12,
            )
        ]

        m05_below, catalog = evaluate(
            m05_below_rows,
            customer_row(),
        )

        self.assertNotIn(
            "M05",
            triggered_rule_ids(
                m05_below,
                catalog,
            ),
        )

        pep_customer = customer_row(
            pep="Yes",
        )

        m08_at, catalog = evaluate(
            [
                transaction_row(
                    1,
                    50000.0,
                )
            ],
            pep_customer,
        )

        self.assertIn(
            "M08",
            triggered_rule_ids(
                m08_at,
                catalog,
            ),
        )

        m08_below, catalog = evaluate(
            [
                transaction_row(
                    1,
                    49999.99,
                )
            ],
            pep_customer,
        )

        self.assertNotIn(
            "M08",
            triggered_rule_ids(
                m08_below,
                catalog,
            ),
        )


if __name__ == "__main__":
    unittest.main()
