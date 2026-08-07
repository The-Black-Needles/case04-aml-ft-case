from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd


MODULE_PATH = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "src"
    / "ml_model.py"
)

SPEC = (
    importlib.util
    .spec_from_file_location(
        "ml_model_explainability_under_test",
        MODULE_PATH,
    )
)

if (
    SPEC is None
    or SPEC.loader is None
):
    raise RuntimeError(
        "Não foi possível carregar src/ml_model.py"
    )

ML_MODEL = (
    importlib.util
    .module_from_spec(
        SPEC
    )
)

sys.modules[SPEC.name] = ML_MODEL
SPEC.loader.exec_module(
    ML_MODEL
)


class FakePreprocessor:
    def get_feature_names_out(
        self,
    ) -> np.ndarray:
        return np.asarray(
            [
                "categorical__occupation_A",
                "numeric__amount",
            ],
            dtype=object,
        )

    def transform(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        return np.asarray(
            [
                [
                    float(index + 1),
                    float(
                        frame.iloc[
                            index
                        ][
                            "amount"
                        ]
                    ),
                ]
                for index in range(
                    len(frame)
                )
            ],
            dtype=float,
        )


class FakeBooster:
    def __init__(
        self,
        scores: dict[str, float],
    ) -> None:
        self.scores = scores

    def get_score(
        self,
        *,
        importance_type: str,
    ) -> dict[str, float]:
        if importance_type != "gain":
            return {}

        return dict(
            self.scores
        )


class FakeModel:
    def __init__(
        self,
        scores: dict[str, float],
    ) -> None:
        self.booster = FakeBooster(
            scores
        )

    def get_booster(
        self,
    ) -> FakeBooster:
        return self.booster


class FakePipeline:
    def __init__(
        self,
        scores: dict[str, float],
    ) -> None:
        self.named_steps = {
            "preprocess":
                FakePreprocessor(),
            "model":
                FakeModel(
                    scores
                ),
        }


def fake_fit(
    scores: dict[str, float]
    | None = None,
) -> object:
    return ML_MODEL.CanonicalModelFit(
        pipeline=FakePipeline(
            scores
            if scores is not None
            else {
                "f0": 1.5,
                "f1": 3.5,
            }
        ),
        categorical_features=(
            "occupation",
        ),
        numeric_features=(
            "amount",
        ),
        scale_pos_weight=1.0,
        train_rows=2,
        train_positives=1,
        train_negatives=1,
    )


class CanonicalExplainabilityTests(
    unittest.TestCase
):
    def test_returns_fitted_transformed_feature_names(
        self,
    ) -> None:
        names = (
            ML_MODEL
            .get_transformed_feature_names(
                fake_fit()
            )
        )

        self.assertEqual(
            names,
            (
                "categorical__occupation_A",
                "numeric__amount",
            ),
        )

    def test_maps_native_gain_to_transformed_names(
        self,
    ) -> None:
        result = (
            ML_MODEL
            .canonical_xgboost_feature_importance(
                fake_fit(),
                importance_type="gain",
            )
        )

        self.assertEqual(
            list(
                result[
                    "feature"
                ]
            ),
            [
                "numeric__amount",
                "categorical__occupation_A",
            ],
        )

        self.assertEqual(
            list(
                result[
                    "importance"
                ]
            ),
            [
                3.5,
                1.5,
            ],
        )

        self.assertTrue(
            result[
                "importance_type"
            ]
            .eq(
                "gain"
            )
            .all()
        )

    def test_rejects_invalid_internal_feature_index(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "fora do intervalo",
        ):
            (
                ML_MODEL
                .canonical_xgboost_feature_importance(
                    fake_fit(
                        {
                            "f9": 1.0,
                        }
                    )
                )
            )

    def test_shap_summary_uses_explicit_partition(
        self,
    ) -> None:
        frame = pd.DataFrame(
            {
                "occupation": [
                    "A",
                    "A",
                ],
                "amount": [
                    10.0,
                    20.0,
                ],
            }
        )

        partitions = (
            ML_MODEL
            .CanonicalSplits(
                train=frame.copy(),
                calibration=frame.copy(),
                test=frame.copy(),
            )
        )

        class FakeExplainer:
            def __init__(
                self,
                model: object,
            ) -> None:
                self.model = model

            def shap_values(
                self,
                matrix: np.ndarray,
            ) -> np.ndarray:
                self.rows = len(
                    matrix
                )

                return np.asarray(
                    [
                        [
                            1.0,
                            -2.0,
                        ],
                        [
                            3.0,
                            4.0,
                        ],
                    ],
                    dtype=float,
                )[
                    :self.rows
                ]

        fake_shap = SimpleNamespace(
            TreeExplainer=FakeExplainer
        )

        with (
            patch.object(
                ML_MODEL,
                "split_canonical_dataset",
                return_value=partitions,
            ),
            patch.dict(
                sys.modules,
                {
                    "shap": fake_shap,
                },
            ),
        ):
            result = (
                ML_MODEL
                .canonical_shap_summary(
                    fake_fit(),
                    frame,
                    split="test",
                )
            )

        self.assertEqual(
            list(
                result[
                    "feature"
                ]
            ),
            [
                "numeric__amount",
                "categorical__occupation_A",
            ],
        )

        self.assertAlmostEqual(
            float(
                result.iloc[
                    0
                ][
                    "mean_abs_shap"
                ]
            ),
            3.0,
        )

        self.assertAlmostEqual(
            float(
                result.iloc[
                    1
                ][
                    "mean_abs_shap"
                ]
            ),
            2.0,
        )

        self.assertTrue(
            result[
                "split"
            ]
            .eq(
                "test"
            )
            .all()
        )

        self.assertTrue(
            result[
                "rows_explained"
            ]
            .eq(
                2
            )
            .all()
        )


if __name__ == "__main__":
    unittest.main()
