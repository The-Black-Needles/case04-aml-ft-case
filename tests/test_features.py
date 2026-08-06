from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = ROOT / "src" / "features.py"


def load_features_module() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "case04_features_tests",
        FEATURES_PATH,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Não foi possível carregar {FEATURES_PATH}"
        )

    module = importlib.util.module_from_spec(
        specification
    )

    specification.loader.exec_module(
        module
    )

    return module


FEATURES = load_features_module()


def make_row(
    customer_id: str,
    month: str,
    occupation: str,
    total_amount: float,
    rule_count: int,
    *,
    avg_amount: float | None = 100.0,
    max_amount: float = 500.0,
) -> dict[str, object]:
    row: dict[str, object] = {
        "customer_id": customer_id,
        "month": month,
        "month_rule_count": rule_count,
        "total_amount": total_amount,
        "declared_occupation": occupation,
        "date_of_birth": "1990-01-15",
        "registration_date": "2020-02-01",
        "annual_income_brl": 120000.0,
        "kyc_tier": "L2",
        "kyc_risk_score": 50.0,
        "state": "SP",
        "city": "São Paulo",
        "beneficial_owner": "No",
        "avg_amount": avg_amount,
        "max_amount": max_amount,
        "confirmed_count": 2,
        "pix_count": 3,
        "card_count": 1,
        "wire_count": 0,
        "risk_rating": "Medium",
        "pep": "No",
        "sanctions_list_hit": "No",
        "tx_count": 4,
        "unique_counterparties": 4,
        "R17_geo_jump_candidate": 1,
    }

    for index in range(1, 13):
        row[
            f"M{index:02d}_test_rule"
        ] = int(
            index <= rule_count
        )

    return row


def sample_frame() -> pd.DataFrame:
    rows = [
        make_row(
            "C1",
            "2025-07",
            "A",
            10.0,
            3,
            avg_amount=np.nan,
        ),
        make_row(
            "C2",
            "2025-07",
            "A",
            30.0,
            2,
        ),
        make_row(
            "C3",
            "2025-07",
            "B",
            50.0,
            1,
        ),
        make_row(
            "C1",
            "2025-08",
            "A",
            100.0,
            4,
        ),
        make_row(
            "C2",
            "2025-08",
            "A",
            200.0,
            0,
        ),
        make_row(
            "C3",
            "2025-08",
            "B",
            80.0,
            3,
        ),
        make_row(
            "C4",
            "2025-08",
            "C",
            9999999.0,
            0,
            max_amount=9999999.0,
        ),
        make_row(
            "C1",
            "2025-09",
            "A",
            300.0,
            2,
        ),
        make_row(
            "C2",
            "2025-09",
            "A",
            500.0,
            3,
        ),
        make_row(
            "C3",
            "2025-09",
            "B",
            120.0,
            0,
        ),
        make_row(
            "C4",
            "2025-09",
            "C",
            110.0,
            1,
        ),
        make_row(
            "C1",
            "2025-10",
            "A",
            900.0,
            12,
        ),
    ]

    return pd.DataFrame(
        rows
    )


class CanonicalFeatureTests(
    unittest.TestCase
):
    def test_builds_canonical_label_and_excludes_incomplete_month(
        self,
    ) -> None:
        dataset, categorical, numeric = (
            FEATURES
            .build_canonical_customer_month_dataset(
                sample_frame()
            )
        )

        self.assertEqual(
            set(dataset["month"]),
            {
                "2025-07",
                "2025-08",
                "2025-09",
            },
        )

        self.assertEqual(
            len(dataset),
            11,
        )

        self.assertNotIn(
            "entity_type_model",
            dataset.columns,
        )

        labels = dataset.set_index(
            [
                "customer_id",
                "month",
            ]
        )["weak_label"]

        self.assertEqual(
            int(
                labels.loc[
                    (
                        "C1",
                        "2025-07",
                    )
                ]
            ),
            1,
        )

        self.assertEqual(
            int(
                labels.loc[
                    (
                        "C2",
                        "2025-07",
                    )
                ]
            ),
            0,
        )

        self.assertEqual(
            int(
                labels.loc[
                    (
                        "C3",
                        "2025-08",
                    )
                ]
            ),
            1,
        )

        all_features = (
            categorical
            + numeric
        )

        self.assertTrue(
            all_features
        )

        self.assertNotIn(
            "month_rule_count",
            all_features,
        )

        self.assertNotIn(
            "risk_rating",
            all_features,
        )

        self.assertNotIn(
            "pep",
            all_features,
        )

        self.assertNotIn(
            "sanctions_list_hit",
            all_features,
        )

        self.assertNotIn(
            "tx_count",
            all_features,
        )

        self.assertFalse(
            any(
                column.startswith("M")
                for column in all_features
            )
        )

        self.assertFalse(
            any(
                column.startswith("R17")
                for column in all_features
            )
        )

    def test_split_contract_is_temporal_and_explicit(
        self,
    ) -> None:
        dataset, _, _ = (
            FEATURES
            .build_canonical_customer_month_dataset(
                sample_frame()
            )
        )

        splits = (
            dataset[
                [
                    "month",
                    "ml_split",
                ]
            ]
            .drop_duplicates()
            .set_index(
                "month"
            )[
                "ml_split"
            ]
            .to_dict()
        )

        self.assertEqual(
            splits,
            {
                "2025-07": "train",
                "2025-08": "calibration",
                "2025-09": "test",
            },
        )

    def test_peer_features_use_leave_one_out_then_prior_month(
        self,
    ) -> None:
        dataset, _, _ = (
            FEATURES
            .build_canonical_customer_month_dataset(
                sample_frame()
            )
        )

        indexed = dataset.set_index(
            [
                "customer_id",
                "month",
            ]
        )

        july_c1 = indexed.loc[
            (
                "C1",
                "2025-07",
            )
        ]

        self.assertEqual(
            july_c1[
                "peer_reference_method"
            ],
            "leave_one_out_train",
        )

        self.assertEqual(
            july_c1[
                "peer_reference_month"
            ],
            "2025-07",
        )

        self.assertEqual(
            float(
                july_c1[
                    "peer_group_size"
                ]
            ),
            1.0,
        )

        self.assertEqual(
            float(
                july_c1[
                    "peer_total_amount_median"
                ]
            ),
            30.0,
        )

        july_c3 = indexed.loc[
            (
                "C3",
                "2025-07",
            )
        ]

        self.assertEqual(
            float(
                july_c3[
                    "peer_group_size"
                ]
            ),
            0.0,
        )

        self.assertTrue(
            math.isnan(
                float(
                    july_c3[
                        "peer_total_amount_median"
                    ]
                )
            )
        )

        august_c1 = indexed.loc[
            (
                "C1",
                "2025-08",
            )
        ]

        self.assertEqual(
            august_c1[
                "peer_reference_method"
            ],
            "prior_month",
        )

        self.assertEqual(
            august_c1[
                "peer_reference_month"
            ],
            "2025-07",
        )

        self.assertEqual(
            float(
                august_c1[
                    "peer_group_size"
                ]
            ),
            2.0,
        )

        self.assertEqual(
            float(
                august_c1[
                    "peer_total_amount_median"
                ]
            ),
            20.0,
        )

        self.assertEqual(
            float(
                august_c1[
                    "ratio_to_peer_median_total"
                ]
            ),
            5.0,
        )

        august_c4 = indexed.loc[
            (
                "C4",
                "2025-08",
            )
        ]

        self.assertTrue(
            math.isnan(
                float(
                    august_c4[
                        "peer_total_amount_median"
                    ]
                )
            )
        )

        september_c1 = indexed.loc[
            (
                "C1",
                "2025-09",
            )
        ]

        self.assertEqual(
            september_c1[
                "peer_reference_month"
            ],
            "2025-08",
        )

        self.assertEqual(
            float(
                september_c1[
                    "peer_total_amount_median"
                ]
            ),
            150.0,
        )

        september_c4 = indexed.loc[
            (
                "C4",
                "2025-09",
            )
        ]

        self.assertEqual(
            float(
                september_c4[
                    "peer_total_amount_median"
                ]
            ),
            9999999.0,
        )

    def test_preserves_missing_values_and_outliers(
        self,
    ) -> None:
        dataset, _, numeric = (
            FEATURES
            .build_canonical_customer_month_dataset(
                sample_frame()
            )
        )

        indexed = dataset.set_index(
            [
                "customer_id",
                "month",
            ]
        )

        self.assertTrue(
            math.isnan(
                float(
                    indexed.loc[
                        (
                            "C1",
                            "2025-07",
                        ),
                        "avg_amount",
                    ]
                )
            )
        )

        self.assertEqual(
            float(
                indexed.loc[
                    (
                        "C4",
                        "2025-08",
                    ),
                    "max_amount",
                ]
            ),
            9999999.0,
        )

        self.assertIn(
            "avg_amount",
            numeric,
        )

        self.assertIn(
            "max_amount",
            numeric,
        )

    def test_rejects_duplicate_customer_month_keys(
        self,
    ) -> None:
        frame = sample_frame()

        frame = pd.concat(
            [
                frame,
                frame.iloc[
                    [
                        0,
                    ]
                ],
            ],
            ignore_index=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicadas",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_month_rule_count_inconsistent_with_m01_m12(
        self,
    ) -> None:
        frame = sample_frame()

        frame.loc[
            0,
            "month_rule_count",
        ] = 7

        with self.assertRaisesRegex(
            ValueError,
            "diverge da soma M01-M12",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_missing_complete_month(
        self,
    ) -> None:
        frame = sample_frame()

        frame = frame.loc[
            ~frame[
                "month"
            ].eq(
                "2025-09"
            )
        ].copy()

        with self.assertRaisesRegex(
            ValueError,
            "Meses completos ausentes",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_prohibited_column_contract_covers_legacy_and_r17(
        self,
    ) -> None:
        self.assertTrue(
            FEATURES.is_prohibited_ml_column(
                "r_out_of_profile"
            )
        )

        self.assertTrue(
            FEATURES.is_prohibited_ml_column(
                "M01_any_rule"
            )
        )

        self.assertTrue(
            FEATURES.is_prohibited_ml_column(
                "R17_geo_jump"
            )
        )

        self.assertTrue(
            FEATURES.is_prohibited_ml_column(
                "month_rule_score"
            )
        )

        self.assertFalse(
            FEATURES.is_prohibited_ml_column(
                "avg_amount"
            )
        )

    def test_rejects_duplicate_keys_created_by_normalization(
        self,
    ) -> None:
        frame = sample_frame()

        duplicate = frame.iloc[
            [
                0,
            ]
        ].copy()

        duplicate[
            "customer_id"
        ] = (
            " "
            + str(
                duplicate[
                    "customer_id"
                ].iloc[0]
            )
        )

        frame = pd.concat(
            [
                frame,
                duplicate,
            ],
            ignore_index=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicadas",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_numeric_rule_value_above_one(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "M01_test_rule"
        ] = frame[
            "M01_test_rule"
        ].astype(object)

        frame.loc[
            0,
            "M01_test_rule",
        ] = 2

        with self.assertRaisesRegex(
            ValueError,
            "não binário",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_negative_numeric_rule_value(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "M12_test_rule"
        ] = frame[
            "M12_test_rule"
        ].astype(object)

        frame.loc[
            0,
            "M12_test_rule",
        ] = -1

        with self.assertRaisesRegex(
            ValueError,
            "não binário",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_missing_primary_feature(
        self,
    ) -> None:
        frame = sample_frame().drop(
            columns=[
                "annual_income_brl",
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Features canônicas ausentes",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_arbitrary_split_names(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Nomes de split inválidos",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                sample_frame(),
                split_months={
                    "fit": "2025-07",
                    "tune": "2025-08",
                    "holdout": "2025-09",
                },
            )

    def test_rejects_blank_customer_id(
        self,
    ) -> None:
        frame = sample_frame()

        frame.loc[
            0,
            "customer_id",
        ] = "   "

        with self.assertRaisesRegex(
            ValueError,
            "customer_id contém valor vazio",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_missing_customer_id(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "customer_id"
        ] = frame[
            "customer_id"
        ].astype("string")

        frame.loc[
            0,
            "customer_id",
        ] = pd.NA

        with self.assertRaisesRegex(
            ValueError,
            "customer_id contém valor ausente",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_blank_month(
        self,
    ) -> None:
        frame = sample_frame()

        frame.loc[
            0,
            "month",
        ] = "   "

        with self.assertRaisesRegex(
            ValueError,
            "month contém valor vazio",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_invalid_calendar_month(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Mês calendário inválido",
        ):
            FEATURES._normalize_months(
                (
                    "2025-13",
                )
            )

    def test_rejects_missing_rule_value(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "M01_test_rule"
        ] = frame[
            "M01_test_rule"
        ].astype(object)

        frame.loc[
            0,
            "M01_test_rule",
        ] = pd.NA

        frame.loc[
            0,
            "month_rule_count",
        ] = (
            int(
                frame.loc[
                    0,
                    "month_rule_count",
                ]
            )
            - 1
        )

        with self.assertRaisesRegex(
            ValueError,
            "Valor de regra ausente",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_fractional_month_rule_count(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "month_rule_count"
        ] = frame[
            "month_rule_count"
        ].astype(float)

        frame.loc[
            0,
            "month_rule_count",
        ] = (
            float(
                frame.loc[
                    0,
                    "month_rule_count",
                ]
            )
            + 0.5
        )

        with self.assertRaisesRegex(
            ValueError,
            "somente valores inteiros",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )

    def test_rejects_non_numeric_primary_feature(
        self,
    ) -> None:
        frame = sample_frame()

        frame[
            "annual_income_brl"
        ] = frame[
            "annual_income_brl"
        ].astype(object)

        frame.loc[
            0,
            "annual_income_brl",
        ] = "not-a-number"

        with self.assertRaisesRegex(
            ValueError,
            "não numérico",
        ):
            FEATURES.build_canonical_customer_month_dataset(
                frame
            )


if __name__ == "__main__":
    unittest.main()
