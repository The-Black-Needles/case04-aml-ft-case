from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "src"
    / "rule_backtesting.py"
)


def load_module() -> ModuleType:
    specification = (
        importlib.util.spec_from_file_location(
            "case04_rule_backtesting_tests",
            MODULE_PATH,
        )
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Não foi possível carregar {MODULE_PATH}"
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


BACKTESTING = load_module()


def transaction_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "R01_alpha": [
                True,
                True,
                False,
                False,
            ],
            "R02_beta": [
                True,
                False,
                True,
                False,
            ],
            "R03_zero": [
                False,
                False,
                False,
                False,
            ],
        }
    )


class RuleBacktestingTests(
    unittest.TestCase
):
    def test_rule_hit_summary_is_exact_and_ordered(
        self,
    ) -> None:
        result = BACKTESTING.rule_hit_summary(
            transaction_fixture(),
            (
                "R01_alpha",
                "R02_beta",
                "R03_zero",
            ),
            level="transaction",
        )

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.RULE_HIT_COLUMNS,
        )

        self.assertEqual(
            result[
                "rule_id"
            ].tolist(),
            [
                "R01",
                "R02",
                "R03",
            ],
        )

        self.assertEqual(
            result[
                "hits"
            ].tolist(),
            [
                2,
                2,
                0,
            ],
        )

        self.assertEqual(
            result[
                "observations"
            ].tolist(),
            [
                4,
                4,
                4,
            ],
        )

        self.assertEqual(
            result[
                "hit_rate"
            ].tolist(),
            [
                0.5,
                0.5,
                0.0,
            ],
        )

    def test_pairwise_cooccurrence_uses_explicit_metrics(
        self,
    ) -> None:
        result = (
            BACKTESTING
            .pairwise_rule_cooccurrence(
                transaction_fixture(),
                (
                    "R01_alpha",
                    "R02_beta",
                    "R03_zero",
                ),
                level="transaction",
            )
        )

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.COOCCURRENCE_COLUMNS,
        )

        self.assertEqual(
            len(result),
            3,
        )

        pair = result[
            result["rule_a_id"].eq(
                "R01"
            )
            & result["rule_b_id"].eq(
                "R02"
            )
        ].iloc[0]

        self.assertEqual(
            int(pair["hits_a"]),
            2,
        )
        self.assertEqual(
            int(pair["hits_b"]),
            2,
        )
        self.assertEqual(
            int(pair["both_hits"]),
            1,
        )
        self.assertEqual(
            int(pair["union_hits"]),
            3,
        )
        self.assertAlmostEqual(
            float(pair["jaccard"]),
            1 / 3,
        )
        self.assertAlmostEqual(
            float(
                pair[
                    "overlap_coefficient"
                ]
            ),
            0.5,
        )
        self.assertAlmostEqual(
            float(
                pair[
                    "p_a_given_b"
                ]
            ),
            0.5,
        )
        self.assertAlmostEqual(
            float(
                pair[
                    "p_b_given_a"
                ]
            ),
            0.5,
        )

    def test_empty_frame_returns_zero_rates(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "R01_alpha": pd.Series(
                    [],
                    dtype=bool,
                ),
            }
        )

        result = BACKTESTING.rule_hit_summary(
            frame,
            (
                "R01_alpha",
            ),
            level="transaction",
        )

        self.assertEqual(
            int(
                result.iloc[
                    0
                ]["observations"]
            ),
            0,
        )
        self.assertEqual(
            int(
                result.iloc[
                    0
                ]["hits"]
            ),
            0,
        )
        self.assertEqual(
            float(
                result.iloc[
                    0
                ]["hit_rate"]
            ),
            0.0,
        )

    def test_rejects_duplicate_rule_columns(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "duplicadas",
        ):
            BACKTESTING.rule_hit_summary(
                transaction_fixture(),
                (
                    "R01_alpha",
                    "R01_alpha",
                ),
                level="transaction",
            )

    def test_rejects_duplicate_rule_ids(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "R01_alpha": [
                    True,
                    False,
                ],
                "R01_beta": [
                    False,
                    True,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "ID de regra duplicado",
        ):
            BACKTESTING.rule_hit_summary(
                frame,
                (
                    "R01_alpha",
                    "R01_beta",
                ),
                level="transaction",
            )

    def test_rejects_missing_rule_column(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "ausente",
        ):
            BACKTESTING.rule_hit_summary(
                transaction_fixture(),
                (
                    "R04_missing",
                ),
                level="transaction",
            )

    def test_rejects_non_boolean_rule_column(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "R01_alpha": [
                    1,
                    0,
                ],
            }
        )

        with self.assertRaisesRegex(
            TypeError,
            "booleana",
        ):
            BACKTESTING.rule_hit_summary(
                frame,
                (
                    "R01_alpha",
                ),
                level="transaction",
            )

    def test_rejects_r17_in_principal_backtest(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "R17_geo_jump": [
                    True,
                    False,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "regra separada",
        ):
            BACKTESTING.rule_hit_summary(
                frame,
                (
                    "R17_geo_jump",
                ),
                level="transaction",
            )

    def test_rejects_rule_family_level_mismatch(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "M01_month": [
                    True,
                    False,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "não pertence",
        ):
            BACKTESTING.rule_hit_summary(
                frame,
                (
                    "M01_month",
                ),
                level="transaction",
            )


    def test_transaction_rule_rail_summary_is_exact(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "transaction_type": [
                    "PIX",
                    "PIX",
                    "Card",
                    "Wire",
                ],
                "R01_alpha": [
                    True,
                    False,
                    True,
                    False,
                ],
                "R02_beta": [
                    False,
                    True,
                    False,
                    False,
                ],
            }
        )

        result = (
            BACKTESTING
            .transaction_rule_rail_summary(
                frame,
                (
                    "R01_alpha",
                    "R02_beta",
                ),
            )
        )

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.TRANSACTION_RAIL_COLUMNS,
        )

        self.assertEqual(
            len(result),
            6,
        )

        r01_pix = result[
            result["rule_id"].eq("R01")
            & result["rail"].eq("PIX")
        ].iloc[0]

        self.assertEqual(
            int(r01_pix["observations"]),
            2,
        )
        self.assertEqual(
            int(r01_pix["hits"]),
            1,
        )
        self.assertEqual(
            float(r01_pix["hit_rate"]),
            0.5,
        )

        r01_wire = result[
            result["rule_id"].eq("R01")
            & result["rail"].eq("Wire")
        ].iloc[0]

        self.assertEqual(
            int(r01_wire["observations"]),
            1,
        )
        self.assertEqual(
            int(r01_wire["hits"]),
            0,
        )

    def test_transaction_rail_rejects_unknown_rail(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "transaction_type": [
                    "PIX",
                    "Cash",
                ],
                "R01_alpha": [
                    True,
                    False,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Rail não suportado",
        ):
            BACKTESTING.transaction_rule_rail_summary(
                frame,
                (
                    "R01_alpha",
                ),
            )

    def test_transaction_rail_rejects_missing_rail(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "transaction_type": [
                    "PIX",
                    None,
                ],
                "R01_alpha": [
                    True,
                    False,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "rails ausentes",
        ):
            BACKTESTING.transaction_rule_rail_summary(
                frame,
                (
                    "R01_alpha",
                ),
            )

    def test_month_rail_presence_is_non_exclusive(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "pix_count": [
                    1,
                    0,
                    1,
                ],
                "card_count": [
                    1,
                    1,
                    0,
                ],
                "wire_count": [
                    0,
                    0,
                    1,
                ],
                "M01_alpha": [
                    True,
                    True,
                    False,
                ],
                "M02_beta": [
                    False,
                    True,
                    True,
                ],
            }
        )

        result = (
            BACKTESTING
            .customer_month_rule_rail_presence_summary(
                frame,
                (
                    "M01_alpha",
                    "M02_beta",
                ),
            )
        )

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.MONTH_RAIL_PRESENCE_COLUMNS,
        )

        self.assertEqual(
            len(result),
            6,
        )

        self.assertTrue(
            result[
                "rail_presence_non_exclusive"
            ].all()
        )

        m01_pix = result[
            result["rule_id"].eq("M01")
            & result["rail"].eq("PIX")
        ].iloc[0]

        self.assertEqual(
            int(m01_pix["customer_months"]),
            2,
        )
        self.assertEqual(
            int(m01_pix["hits"]),
            1,
        )
        self.assertEqual(
            float(m01_pix["hit_rate"]),
            0.5,
        )

        m01_card = result[
            result["rule_id"].eq("M01")
            & result["rail"].eq("Card")
        ].iloc[0]

        self.assertEqual(
            int(m01_card["customer_months"]),
            2,
        )
        self.assertEqual(
            int(m01_card["hits"]),
            2,
        )
        self.assertEqual(
            float(m01_card["hit_rate"]),
            1.0,
        )

    def test_month_rail_rejects_fractional_counts(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "pix_count": [
                    1.5,
                ],
                "card_count": [
                    0,
                ],
                "wire_count": [
                    0,
                ],
                "M01_alpha": [
                    True,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "contagens fracionárias",
        ):
            BACKTESTING.customer_month_rule_rail_presence_summary(
                frame,
                (
                    "M01_alpha",
                ),
            )

    def test_month_rail_rejects_negative_counts(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "pix_count": [
                    -1,
                ],
                "card_count": [
                    0,
                ],
                "wire_count": [
                    0,
                ],
                "M01_alpha": [
                    True,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "valores negativos",
        ):
            BACKTESTING.customer_month_rule_rail_presence_summary(
                frame,
                (
                    "M01_alpha",
                ),
            )

    def test_month_rail_rejects_non_numeric_counts(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "pix_count": [
                    "invalid",
                ],
                "card_count": [
                    0,
                ],
                "wire_count": [
                    0,
                ],
                "M01_alpha": [
                    True,
                ],
            }
        )

        with self.assertRaisesRegex(
            TypeError,
            "deve ser numérica",
        ):
            BACKTESTING.customer_month_rule_rail_presence_summary(
                frame,
                (
                    "M01_alpha",
                ),
            )



    def test_alert_load_summary_is_exact(
        self,
    ) -> None:
        result = BACKTESTING.alert_load_summary(
            transaction_fixture(),
            (
                "R01_alpha",
                "R02_beta",
                "R03_zero",
            ),
            level="transaction",
        )

        row = result.iloc[0]

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.ALERT_LOAD_COLUMNS,
        )
        self.assertEqual(
            int(row["observations"]),
            4,
        )
        self.assertEqual(
            int(row["alerted_observations"]),
            3,
        )
        self.assertEqual(
            float(row["alert_rate"]),
            0.75,
        )
        self.assertEqual(
            int(row["total_rule_hits"]),
            4,
        )
        self.assertEqual(
            float(
                row[
                    "mean_rule_hits_per_observation"
                ]
            ),
            1.0,
        )
        self.assertEqual(
            int(
                row[
                    "max_rule_hits_per_observation"
                ]
            ),
            2,
        )

    def test_empty_alert_load_is_zero(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "R01_alpha": pd.Series(
                    [],
                    dtype=bool,
                ),
            }
        )

        result = BACKTESTING.alert_load_summary(
            frame,
            (
                "R01_alpha",
            ),
            level="transaction",
        )

        row = result.iloc[0]

        self.assertEqual(
            int(row["observations"]),
            0,
        )
        self.assertEqual(
            int(row["alerted_observations"]),
            0,
        )
        self.assertEqual(
            float(row["alert_rate"]),
            0.0,
        )
        self.assertEqual(
            int(row["total_rule_hits"]),
            0,
        )
        self.assertEqual(
            int(
                row[
                    "max_rule_hits_per_observation"
                ]
            ),
            0,
        )

    def test_rule_count_distribution_is_exact(
        self,
    ) -> None:
        result = BACKTESTING.rule_count_distribution(
            transaction_fixture(),
            (
                "R01_alpha",
                "R02_beta",
                "R03_zero",
            ),
            level="transaction",
        )

        self.assertEqual(
            tuple(result.columns),
            BACKTESTING.RULE_COUNT_DISTRIBUTION_COLUMNS,
        )

        self.assertEqual(
            result[
                "rule_count"
            ].tolist(),
            [
                0,
                1,
                2,
            ],
        )

        self.assertEqual(
            result[
                "observations"
            ].tolist(),
            [
                1,
                2,
                1,
            ],
        )

        self.assertEqual(
            result[
                "observation_share"
            ].tolist(),
            [
                0.25,
                0.5,
                0.25,
            ],
        )

    def test_transaction_alert_load_by_rail_is_exact(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "transaction_type": [
                    "PIX",
                    "PIX",
                    "Card",
                    "Wire",
                ],
                "R01_alpha": [
                    True,
                    False,
                    True,
                    False,
                ],
                "R02_beta": [
                    True,
                    False,
                    False,
                    True,
                ],
            }
        )

        result = (
            BACKTESTING
            .transaction_alert_load_by_rail(
                frame,
                (
                    "R01_alpha",
                    "R02_beta",
                ),
            )
        )

        pix = result[
            result[
                "segment_value"
            ].eq(
                "PIX"
            )
        ].iloc[0]

        self.assertEqual(
            int(pix["observations"]),
            2,
        )
        self.assertEqual(
            int(
                pix[
                    "alerted_observations"
                ]
            ),
            1,
        )
        self.assertEqual(
            int(pix["total_rule_hits"]),
            2,
        )
        self.assertEqual(
            int(
                pix[
                    "max_rule_hits_per_observation"
                ]
            ),
            2,
        )

    def test_transaction_alert_load_by_status_is_exact(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "status": [
                    "Confirmed",
                    "Pending",
                    "Failed",
                    "Chargeback",
                ],
                "R01_alpha": [
                    True,
                    False,
                    True,
                    True,
                ],
            }
        )

        result = (
            BACKTESTING
            .transaction_alert_load_by_status(
                frame,
                (
                    "R01_alpha",
                ),
            )
        )

        confirmed = result[
            result[
                "segment_value"
            ].eq(
                "Confirmed"
            )
        ].iloc[0]

        pending = result[
            result[
                "segment_value"
            ].eq(
                "Pending"
            )
        ].iloc[0]

        self.assertEqual(
            int(
                confirmed[
                    "alerted_observations"
                ]
            ),
            1,
        )
        self.assertEqual(
            int(
                pending[
                    "alerted_observations"
                ]
            ),
            0,
        )

    def test_transaction_status_rejects_unknown_value(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "status": [
                    "Confirmed",
                    "Unknown",
                ],
                "R01_alpha": [
                    True,
                    False,
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Status transacional não suportado",
        ):
            BACKTESTING.transaction_alert_load_by_status(
                frame,
                (
                    "R01_alpha",
                ),
            )


if __name__ == "__main__":
    unittest.main()
