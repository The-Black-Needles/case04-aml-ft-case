from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src import t2_backtesting_runner


class T2BacktestingRunnerTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(
        cls,
    ) -> None:
        (
            cls.tx_rules,
            cls.tx_rule_columns,
            cls.month_rules,
            cls.month_rule_columns,
        ) = (
            t2_backtesting_runner
            .load_principal_rule_frames()
        )

        cls.tables = (
            t2_backtesting_runner
            .build_backtesting_tables(
                cls.tx_rules,
                cls.tx_rule_columns,
                cls.month_rules,
                cls.month_rule_columns,
            )
        )

    def test_table_contract_and_shapes(
        self,
    ) -> None:
        expected_rows = {
            "rule_hits_transaction": 16,
            "rule_hits_customer_month": 12,
            "rule_rail_transaction": 48,
            "rule_rail_presence_customer_month": 36,
            "alert_load": 2,
            "rule_count_distribution_transaction": 7,
            "transaction_load_by_status": 4,
            "transaction_load_by_rail": 3,
            "pairwise_review_transaction": 120,
            "pairwise_review_customer_month": 66,
        }

        for (
            key,
            expected,
        ) in expected_rows.items():
            self.assertEqual(
                len(
                    self.tables[
                        key
                    ]
                ),
                expected,
                key,
            )

        self.assertNotIn(
            "R17",
            set(
                self.tables[
                    "rule_hits_transaction"
                ][
                    "rule_id"
                ]
            ),
        )

    def test_manifest_preserves_limits(
        self,
    ) -> None:
        manifest = (
            t2_backtesting_runner
            .build_manifest(
                self.tables
            )
        )

        self.assertEqual(
            manifest[
                "principal_rule_engine"
            ][
                "total_rules"
            ],
            28,
        )

        self.assertFalse(
            manifest[
                "limitations"
            ][
                "independent_ground_truth"
            ]
        )

        self.assertFalse(
            manifest[
                "limitations"
            ][
                "rule_fp_fn_metrics_available"
            ]
        )

        self.assertTrue(
            manifest[
                "limitations"
            ][
                "human_review_required"
            ]
        )

    def test_summary_is_explicit_about_experimental_scope(
        self,
    ) -> None:
        summary = (
            t2_backtesting_runner
            .build_summary_markdown(
                self.tables
            )
        )

        self.assertIn(
            "base sintética",
            summary,
        )

        self.assertIn(
            "status` não é tratado como ground truth",
            summary,
        )

        self.assertIn(
            "não constitui homologação produtiva",
            summary,
        )

        self.assertIn(
            "A decisão final permanece supervisionada por humanos.",
            summary,
        )

    def test_output_generation_is_deterministic(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(
                temp
            )

            first = (
                t2_backtesting_runner
                .write_backtesting_outputs(
                    output_dir,
                    tables=self.tables,
                )
            )

            first_bytes = {
                path.name: path.read_bytes()
                for path in first
            }

            second = (
                t2_backtesting_runner
                .write_backtesting_outputs(
                    output_dir,
                    tables=self.tables,
                )
            )

            second_bytes = {
                path.name: path.read_bytes()
                for path in second
            }

            self.assertEqual(
                first_bytes,
                second_bytes,
            )

            manifest = json.loads(
                (
                    output_dir
                    / t2_backtesting_runner.MANIFEST_FILENAME
                ).read_text(
                    encoding="utf-8",
                )
            )

            self.assertEqual(
                manifest[
                    "operational_load"
                ][
                    "transaction_alerted"
                ],
                28204,
            )


if __name__ == "__main__":
    unittest.main()
