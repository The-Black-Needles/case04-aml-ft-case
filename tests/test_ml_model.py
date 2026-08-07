from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd


ROOT = Path(
    __file__
).resolve().parents[1]

ML_MODEL_PATH = (
    ROOT
    / "src"
    / "ml_model.py"
)


def load_ml_model_module() -> ModuleType:
    specification = (
        importlib.util
        .spec_from_file_location(
            "case04_ml_model_tests",
            ML_MODEL_PATH,
        )
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Não foi possível carregar "
            f"{ML_MODEL_PATH}"
        )

    module = (
        importlib.util
        .module_from_spec(
            specification
        )
    )

    sys.modules[
        specification.name
    ] = module

    specification.loader.exec_module(
        module
    )

    return module


ML_MODEL = load_ml_model_module()


def sample_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "customer_id": "C1",
                "month": "2025-07",
                "weak_label": 1,
                "ml_split": "train",
                "occupation": "A",
                "amount": 10.0,
            },
            {
                "customer_id": "C2",
                "month": "2025-07",
                "weak_label": 0,
                "ml_split": "train",
                "occupation": "B",
                "amount": 20.0,
            },
            {
                "customer_id": "C1",
                "month": "2025-08",
                "weak_label": 0,
                "ml_split": "calibration",
                "occupation": "A",
                "amount": 30.0,
            },
            {
                "customer_id": "C2",
                "month": "2025-08",
                "weak_label": 1,
                "ml_split": "calibration",
                "occupation": "B",
                "amount": 40.0,
            },
            {
                "customer_id": "C1",
                "month": "2025-09",
                "weak_label": 1,
                "ml_split": "test",
                "occupation": "A",
                "amount": 50.0,
            },
            {
                "customer_id": "C2",
                "month": "2025-09",
                "weak_label": 0,
                "ml_split": "test",
                "occupation": "B",
                "amount": 60.0,
            },
        ]
    )


class CanonicalMLContractTests(
    unittest.TestCase
):
    def test_threshold_grid_is_exact(
        self,
    ) -> None:
        self.assertEqual(
            ML_MODEL.THRESHOLD_GRID,
            (
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
            ),
        )

    def test_validates_and_splits_canonical_dataset(
        self,
    ) -> None:
        dataset = sample_dataset()

        categorical, numeric = (
            ML_MODEL
            .validate_canonical_dataset(
                dataset,
                categorical_features=[
                    "occupation",
                ],
                numeric_features=[
                    "amount",
                ],
            )
        )

        self.assertEqual(
            categorical,
            (
                "occupation",
            ),
        )
        self.assertEqual(
            numeric,
            (
                "amount",
            ),
        )

        partitions = (
            ML_MODEL
            .split_canonical_dataset(
                dataset
            )
        )

        self.assertEqual(
            len(
                partitions.train
            ),
            2,
        )
        self.assertEqual(
            len(
                partitions.calibration
            ),
            2,
        )
        self.assertEqual(
            len(
                partitions.test
            ),
            2,
        )

    def test_rejects_unknown_split_name(
        self,
    ) -> None:
        dataset = sample_dataset()

        dataset.loc[
            dataset[
                "ml_split"
            ].eq("test"),
            "ml_split",
        ] = "holdout"

        with self.assertRaisesRegex(
            ValueError,
            "Splits canônicos divergentes",
        ):
            ML_MODEL.validate_canonical_dataset(
                dataset
            )

    def test_rejects_non_temporal_split_order(
        self,
    ) -> None:
        dataset = sample_dataset()

        dataset.loc[
            dataset[
                "ml_split"
            ].eq("calibration"),
            "month",
        ] = "2025-06"

        with self.assertRaisesRegex(
            ValueError,
            "ordem temporal",
        ):
            ML_MODEL.validate_canonical_dataset(
                dataset
            )

    def test_rejects_non_binary_label(
        self,
    ) -> None:
        dataset = sample_dataset()

        dataset.loc[
            0,
            "weak_label",
        ] = 2

        with self.assertRaisesRegex(
            ValueError,
            "deve ser binário",
        ):
            ML_MODEL.validate_canonical_dataset(
                dataset
            )

    def test_rejects_direct_leakage_feature(
        self,
    ) -> None:
        dataset = sample_dataset()

        dataset[
            "month_rule_count"
        ] = 0

        with self.assertRaisesRegex(
            ValueError,
            "leakage direto",
        ):
            ML_MODEL.validate_canonical_dataset(
                dataset,
                categorical_features=[
                    "occupation",
                ],
                numeric_features=[
                    "month_rule_count",
                ],
            )

    def test_scale_pos_weight_uses_train_target(
        self,
    ) -> None:
        result = (
            ML_MODEL
            .compute_scale_pos_weight(
                [
                    1,
                    0,
                    0,
                    0,
                ]
            )
        )

        self.assertEqual(
            result,
            3.0,
        )

    def test_perfect_ranking_metrics_equal_one(
        self,
    ) -> None:
        y_true = [
            1,
            0,
            1,
            0,
        ]
        probabilities = [
            0.9,
            0.2,
            0.8,
            0.1,
        ]

        self.assertAlmostEqual(
            ML_MODEL
            .average_precision_binary(
                y_true,
                probabilities,
            ),
            1.0,
        )

        self.assertAlmostEqual(
            ML_MODEL
            .roc_auc_binary(
                y_true,
                probabilities,
            ),
            1.0,
        )

    def test_threshold_confusion_metrics(
        self,
    ) -> None:
        result = (
            ML_MODEL
            .classification_metrics_at_threshold(
                [
                    1,
                    0,
                    1,
                    0,
                ],
                [
                    0.9,
                    0.8,
                    0.4,
                    0.1,
                ],
                0.5,
            )
        )

        self.assertEqual(
            result["tp"],
            1,
        )
        self.assertEqual(
            result["fp"],
            1,
        )
        self.assertEqual(
            result["tn"],
            1,
        )
        self.assertEqual(
            result["fn"],
            1,
        )
        self.assertEqual(
            result[
                "alerts_generated"
            ],
            2,
        )
        self.assertAlmostEqual(
            result["precision"],
            0.5,
        )
        self.assertAlmostEqual(
            result["recall"],
            0.5,
        )
        self.assertAlmostEqual(
            result["fpr"],
            0.5,
        )
        self.assertAlmostEqual(
            result["mcc"],
            0.0,
        )

    def test_threshold_table_uses_fixed_grid(
        self,
    ) -> None:
        table = (
            ML_MODEL
            .threshold_metrics_table(
                [
                    1,
                    0,
                    1,
                    0,
                ],
                [
                    0.9,
                    0.8,
                    0.4,
                    0.1,
                ],
            )
        )

        self.assertEqual(
            len(table),
            9,
        )

        self.assertEqual(
            tuple(
                table[
                    "threshold"
                ]
            ),
            ML_MODEL.THRESHOLD_GRID,
        )

    def test_selects_threshold_with_capacity_and_recall(
        self,
    ) -> None:
        table = pd.DataFrame(
            [
                {
                    "threshold": 0.5,
                    "precision": 0.4,
                    "recall": 0.9,
                    "fpr": 0.2,
                    "mcc": 0.6,
                    "alerts_generated": 40,
                },
                {
                    "threshold": 0.7,
                    "precision": 0.6,
                    "recall": 0.8,
                    "fpr": 0.1,
                    "mcc": 0.55,
                    "alerts_generated": 20,
                },
                {
                    "threshold": 0.9,
                    "precision": 0.9,
                    "recall": 0.4,
                    "fpr": 0.01,
                    "mcc": 0.5,
                    "alerts_generated": 5,
                },
            ]
        )

        selection = (
            ML_MODEL
            .select_operating_threshold(
                table,
                max_alerts=30,
                min_recall=0.7,
            )
        )

        self.assertEqual(
            selection[
                "selection_split"
            ],
            "calibration",
        )
        self.assertEqual(
            selection[
                "threshold"
            ],
            0.7,
        )
        self.assertEqual(
            selection[
                "selection_rule"
            ],
            (
                "max_mcc_with_explicit_"
                "operational_constraints"
            ),
        )

    def test_calibration_selects_before_test_evaluation(
        self,
    ) -> None:
        result = (
            ML_MODEL
            .evaluate_calibration_and_test(
                [
                    1,
                    0,
                    1,
                    0,
                ],
                [
                    0.9,
                    0.8,
                    0.7,
                    0.1,
                ],
                [
                    1,
                    0,
                    0,
                    1,
                ],
                [
                    0.6,
                    0.5,
                    0.4,
                    0.3,
                ],
                thresholds=(
                    0.5,
                    0.8,
                ),
            )
        )

        selected_threshold = (
            result[
                "selection"
            ][
                "threshold"
            ]
        )

        self.assertEqual(
            selected_threshold,
            0.5,
        )
        self.assertEqual(
            result[
                "test_summary"
            ][
                "threshold"
            ],
            selected_threshold,
        )
        self.assertEqual(
            result[
                "test_summary"
            ][
                "threshold_source"
            ],
            "calibration",
        )
        self.assertEqual(
            result[
                "selection"
            ][
                "selection_rule"
            ],
            "max_mcc_statistical_baseline",
        )

    def test_prevalence_baseline_uses_train_only(
        self,
    ) -> None:
        scores = (
            ML_MODEL
            .prevalence_baseline_scores(
                [
                    1,
                    0,
                    0,
                    0,
                ],
                3,
            )
        )

        np.testing.assert_allclose(
            scores,
            np.array(
                [
                    0.25,
                    0.25,
                    0.25,
                ]
            ),
        )

    def test_legacy_contract_remains_available(
        self,
    ) -> None:
        self.assertTrue(
            callable(
                ML_MODEL.temporal_split
            )
        )
        self.assertTrue(
            callable(
                ML_MODEL.get_feature_columns
            )
        )
        self.assertTrue(
            callable(
                ML_MODEL.fit_xgboost_pf
            )
        )


if __name__ == "__main__":
    unittest.main()
