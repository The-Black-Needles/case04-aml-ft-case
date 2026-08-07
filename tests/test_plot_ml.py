from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(
    __file__
).resolve().parents[
    1
]

SRC = ROOT / "src"

if str(
    SRC
) not in sys.path:
    sys.path.insert(
        0,
        str(
            SRC
        ),
    )

import plot_ml


CANONICAL = (
    ROOT
    / "outputs"
    / "t3_ml_canonical"
)


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


class CanonicalMlChartsTests(
    unittest.TestCase
):
    def test_contract_has_five_portuguese_charts(
        self,
    ) -> None:
        self.assertEqual(
            len(
                plot_ml.CHART_FILENAMES
            ),
            5,
        )

        expected = (
            "09_chart_01_prevalencia_splits.png",
            "10_chart_02_tradeoff_thresholds_calibracao.png",
            "11_chart_03_metricas_calibracao_teste.png",
            "12_chart_04_importancia_features_gain.png",
            "13_chart_05_shap_top_features.png",
        )

        self.assertEqual(
            plot_ml.CHART_FILENAMES,
            expected,
        )

        self.assertEqual(
            plot_ml.MANIFEST_FILENAME,
            "14_charts_manifest.json",
        )

    def test_generate_charts_creates_expected_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(
                temp
            )

            result = (
                plot_ml.generate_charts(
                    input_dir=CANONICAL,
                    output_dir=output,
                )
            )

            self.assertEqual(
                result[
                    "chart_count"
                ],
                5,
            )

            self.assertEqual(
                result[
                    "artifact_count"
                ],
                6,
            )

            self.assertAlmostEqual(
                result[
                    "selected_threshold"
                ],
                0.3,
            )

            actual = tuple(
                sorted(
                    path.name
                    for path in output.iterdir()
                )
            )

            self.assertEqual(
                actual,
                tuple(
                    sorted(
                        plot_ml.ALL_OUTPUT_FILENAMES
                    )
                ),
            )

            for filename in (
                plot_ml.CHART_FILENAMES
            ):
                payload = (
                    output
                    / filename
                ).read_bytes()

                self.assertTrue(
                    payload.startswith(
                        b"\x89PNG\r\n\x1a\n"
                    )
                )

                self.assertGreater(
                    len(
                        payload
                    ),
                    10_000,
                )

            manifest = json.loads(
                (
                    output
                    / plot_ml.MANIFEST_FILENAME
                ).read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                manifest[
                    "language"
                ],
                "pt-BR",
            )

            self.assertFalse(
                manifest[
                    "governance"
                ][
                    "production_validation_claimed"
                ]
            )

            self.assertFalse(
                manifest[
                    "governance"
                ][
                    "operational_threshold_homologated"
                ]
            )

            self.assertTrue(
                manifest[
                    "governance"
                ][
                    "human_review_required"
                ]
            )

    def test_generation_is_byte_for_byte_deterministic(
        self,
    ) -> None:
        with (
            tempfile.TemporaryDirectory()
            as temp_a,
            tempfile.TemporaryDirectory()
            as temp_b,
        ):
            output_a = Path(
                temp_a
            )

            output_b = Path(
                temp_b
            )

            plot_ml.generate_charts(
                input_dir=CANONICAL,
                output_dir=output_a,
            )

            plot_ml.generate_charts(
                input_dir=CANONICAL,
                output_dir=output_b,
            )

            for filename in (
                plot_ml.ALL_OUTPUT_FILENAMES
            ):
                self.assertEqual(
                    sha256_file(
                        output_a
                        / filename
                    ),
                    sha256_file(
                        output_b
                        / filename
                    ),
                    filename,
                )

    def test_existing_chart_requires_explicit_overwrite(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(
                temp
            )

            existing = (
                output
                / plot_ml.CHART_FILENAMES[
                    0
                ]
            )

            existing.write_bytes(
                b"sentinel"
            )

            with self.assertRaises(
                FileExistsError
            ):
                plot_ml.generate_charts(
                    input_dir=CANONICAL,
                    output_dir=output,
                )

            self.assertEqual(
                existing.read_bytes(),
                b"sentinel",
            )

            plot_ml.generate_charts(
                input_dir=CANONICAL,
                output_dir=output,
                overwrite=True,
            )

            self.assertNotEqual(
                existing.read_bytes(),
                b"sentinel",
            )

    def test_missing_input_fails_before_writing(
        self,
    ) -> None:
        with (
            tempfile.TemporaryDirectory()
            as input_temp,
            tempfile.TemporaryDirectory()
            as output_temp,
        ):
            input_dir = Path(
                input_temp
            )

            output_dir = Path(
                output_temp
            )

            sentinel = (
                output_dir
                / "sentinel.txt"
            )

            sentinel.write_text(
                "preservar",
                encoding="utf-8",
            )

            with self.assertRaises(
                FileNotFoundError
            ):
                plot_ml.generate_charts(
                    input_dir=input_dir,
                    output_dir=output_dir,
                )

            self.assertEqual(
                sentinel.read_text(
                    encoding="utf-8"
                ),
                "preservar",
            )

            self.assertEqual(
                tuple(
                    path.name
                    for path in output_dir.iterdir()
                ),
                (
                    "sentinel.txt",
                ),
            )

    def test_unknown_entry_is_rejected_before_writing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(
                temp
            )

            sentinel = (
                output
                / "sentinel.txt"
            )

            sentinel.write_text(
                "preservar",
                encoding="utf-8",
            )

            with self.assertRaises(
                RuntimeError
            ):
                plot_ml.generate_charts(
                    input_dir=CANONICAL,
                    output_dir=output,
                    overwrite=True,
                )

            self.assertEqual(
                sentinel.read_text(
                    encoding="utf-8"
                ),
                "preservar",
            )

            self.assertEqual(
                tuple(
                    path.name
                    for path in output.iterdir()
                ),
                (
                    "sentinel.txt",
                ),
            )

    def test_same_canonical_directory_allows_known_base_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            canonical_copy = Path(
                temp
            )

            for filename in (
                plot_ml.CANONICAL_BASE_FILENAMES
            ):
                shutil.copyfile(
                    CANONICAL
                    / filename,
                    canonical_copy
                    / filename,
                )

            result = plot_ml.generate_charts(
                input_dir=canonical_copy,
                output_dir=canonical_copy,
            )

            self.assertEqual(
                result[
                    "chart_count"
                ],
                5,
            )

            actual_names = {
                path.name
                for path in canonical_copy.iterdir()
            }

            self.assertEqual(
                actual_names,
                set(
                    plot_ml.CANONICAL_BASE_FILENAMES
                )
                | set(
                    plot_ml.ALL_OUTPUT_FILENAMES
                ),
            )

    def test_feature_labels_are_public_and_portuguese(
        self,
    ) -> None:
        self.assertEqual(
            plot_ml.feature_label(
                "numeric__confirmed_count"
            ),
            "Transações confirmadas",
        )

        self.assertEqual(
            plot_ml.feature_label(
                "categorical__declared_occupation_Dentist"
            ),
            "Profissão: Dentista",
        )

        self.assertEqual(
            plot_ml.feature_label(
                "numeric__kyc_risk_score"
            ),
            "Score de risco KYC",
        )


if __name__ == "__main__":
    unittest.main()
