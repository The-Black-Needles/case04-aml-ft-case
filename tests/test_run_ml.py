from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(
        0,
        str(SRC),
    )

MODULE_PATH = SRC / "run_ml.py"

SPEC = (
    importlib.util
    .spec_from_file_location(
        "run_ml_under_test",
        MODULE_PATH,
    )
)

if (
    SPEC is None
    or SPEC.loader is None
):
    raise RuntimeError(
        "Não foi possível carregar src/run_ml.py"
    )

RUN_ML = (
    importlib.util
    .module_from_spec(
        SPEC
    )
)

sys.modules[SPEC.name] = RUN_ML
SPEC.loader.exec_module(
    RUN_ML
)


class CanonicalRunnerTests(
    unittest.TestCase
):
    def test_default_output_is_separate_from_legacy(
        self,
    ) -> None:
        parser = RUN_ML.build_parser()

        args = parser.parse_args(
            []
        )

        self.assertEqual(
            args.output_dir,
            Path(
                "outputs/t3_ml_canonical"
            ),
        )

        self.assertNotEqual(
            args.output_dir,
            Path(
                "outputs/t3_ml"
            ),
        )

        self.assertFalse(
            args.overwrite
        )

    def test_rejects_silent_overwrite(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as name:
            output_dir = Path(
                name
            )

            known_artifact = (
                output_dir
                / "00_ml_canonical_summary.md"
            )

            known_artifact.write_text(
                "previous canonical output",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FileExistsError,
                "não está vazio",
            ):
                RUN_ML.prepare_output_dir(
                    output_dir,
                    overwrite=False,
                )

            RUN_ML.prepare_output_dir(
                output_dir,
                overwrite=True,
            )

            self.assertEqual(
                known_artifact.read_text(
                    encoding="utf-8"
                ),
                "previous canonical output",
            )

    def test_rejects_unknown_entry_before_write(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as name:
            output_dir = Path(
                name
            )

            sentinel = (
                output_dir
                / "UNRELATED_SENTINEL.txt"
            )

            sentinel.write_text(
                "preserve-me",
                encoding="utf-8",
            )

            before = {
                path.name:
                    path.read_bytes()
                for path in output_dir.iterdir()
            }

            with self.assertRaisesRegex(
                FileExistsError,
                "fora do contrato canônico",
            ):
                RUN_ML.prepare_output_dir(
                    output_dir,
                    overwrite=True,
                )

            after = {
                path.name:
                    path.read_bytes()
                for path in output_dir.iterdir()
            }

            self.assertEqual(
                after,
                before,
            )

    def test_model_view_contains_only_contract_columns(
        self,
    ) -> None:
        dataset = pd.DataFrame(
            {
                "customer_id": [
                    "C1",
                ],
                "month": [
                    "2025-07",
                ],
                "ml_split": [
                    "train",
                ],
                "weak_label": [
                    1,
                ],
                "occupation": [
                    "A",
                ],
                "amount": [
                    10.0,
                ],
                "M01_private_rule": [
                    1,
                ],
                "rule_count": [
                    5,
                ],
                "full_name": [
                    "Synthetic Example",
                ],
            }
        )

        model_fit = SimpleNamespace(
            categorical_features=(
                "occupation",
            ),
            numeric_features=(
                "amount",
            ),
        )

        result = (
            RUN_ML
            .canonical_model_view(
                dataset,
                model_fit,
            )
        )

        self.assertEqual(
            list(
                result.columns
            ),
            [
                "customer_id",
                "month",
                "ml_split",
                "weak_label",
                "occupation",
                "amount",
            ],
        )

        self.assertNotIn(
            "M01_private_rule",
            result.columns,
        )

        self.assertNotIn(
            "rule_count",
            result.columns,
        )

        self.assertNotIn(
            "full_name",
            result.columns,
        )

    def test_artifact_contract_is_explicit(
        self,
    ) -> None:
        self.assertEqual(
            RUN_ML.ARTIFACT_FILENAMES,
            (
                "00_ml_canonical_summary.md",
                "01_canonical_model_dataset.csv",
                "02_split_distribution.csv",
                "03_metrics_summary.csv",
                "04_threshold_metrics_calibration.csv",
                "05_feature_importance_gain.csv",
                "06_shap_summary_test.csv",
                "07_test_scored_top30.csv",
                "08_run_manifest.json",
            ),
        )

        self.assertNotIn(
            "model_xgboost_pf_pipeline.pkl",
            RUN_ML.ARTIFACT_FILENAMES,
        )


if __name__ == "__main__":
    unittest.main()
