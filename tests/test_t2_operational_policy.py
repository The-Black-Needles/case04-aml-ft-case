from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src import t2_operational_policy


class T2OperationalPolicyTests(
    unittest.TestCase
):
    def test_contract_covers_exact_main_engine(
        self,
    ) -> None:
        policies = (
            t2_operational_policy
            .build_policy()
        )

        self.assertEqual(
            len(policies),
            28,
        )

        self.assertEqual(
            {
                policy.rule_id
                for policy in policies
            },
            set(
                t2_operational_policy
                .MAIN_RULE_IDS
            ),
        )

        self.assertNotIn(
            "R17",
            {
                policy.rule_id
                for policy in policies
            },
        )

    def test_only_r16_and_m01_are_dynamic_active(
        self,
    ) -> None:
        policies = (
            t2_operational_policy
            .build_policy()
        )

        dynamic = {
            policy.rule_id
            for policy in policies
            if (
                policy
                .implemented_threshold_mode
                == "DYNAMIC_ACTIVE"
            )
        }

        self.assertEqual(
            dynamic,
            {
                "R16",
                "M01",
            },
        )

    def test_blocking_is_never_automatic(
        self,
    ) -> None:
        policies = (
            t2_operational_policy
            .build_policy()
        )

        self.assertTrue(
            all(
                not policy.automatic_block
                for policy in policies
            )
        )

        self.assertTrue(
            all(
                policy.human_validation_required
                for policy in policies
            )
        )

        conditional = {
            policy.rule_id
            for policy in policies
            if policy.conditional_block_eligible
        }

        self.assertEqual(
            conditional,
            {
                "R01",
                "R02",
                "M07",
            },
        )

    def test_outputs_are_deterministic_and_explicit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(
                temp
            )

            first = (
                t2_operational_policy
                .write_outputs(
                    root
                )
            )

            first_bytes = {
                path.name: path.read_bytes()
                for path in first
            }

            second = (
                t2_operational_policy
                .write_outputs(
                    root
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

            summary = (
                root
                / t2_operational_policy
                .SUMMARY_FILENAME
            ).read_text(
                encoding="utf-8",
            )

            self.assertIn(
                "Nenhuma das 28 regras autoriza bloqueio automático.",
                summary,
            )

            self.assertIn(
                "R16 e M01",
                summary,
            )

            self.assertIn(
                "Revisão humana obrigatória.",
                summary,
            )


if __name__ == "__main__":
    unittest.main()
