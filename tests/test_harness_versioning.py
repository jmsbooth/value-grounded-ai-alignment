from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch

from experiments.harness.common import render_report
from vgta_eval.registry import RegistryError, append_unique, read_jsonl
from vgta_eval.reporting import ImmutableArtifactError, allocate_analysis, immutable_write
from vgta_eval.run_identity import new_run_id, next_analysis_revision, reserve_run_directory, validate_run_id


class HarnessVersioningTests(unittest.TestCase):
    def test_run_ids_do_not_collide_with_same_second(self):
        now = datetime(2026, 9, 9, 1, 15, 32, tzinfo=timezone.utc)
        ids = {new_run_id(now=now) for _ in range(256)}
        self.assertEqual(len(ids), 256)
        for run_id in ids:
            validate_run_id(run_id)

    def test_atomic_directory_reservation_handles_concurrent_calls(self):
        with TemporaryDirectory() as directory:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: reserve_run_directory(directory), range(32)))
            self.assertEqual(len({run_id for run_id, _ in results}), 32)
            self.assertEqual(len(list(Path(directory).iterdir())), 32)

    def test_analysis_revision_increments_without_overwrite(self):
        with TemporaryDirectory() as directory:
            parent = Path(directory) / "analysis"
            parent.mkdir()
            (parent / "analysis-r001").mkdir()
            self.assertEqual(next_analysis_revision(parent), 2)
            revision, allocated = allocate_analysis(directory, "hv-v0.5.0", "demo", "20260909T011532Z-7c4a2f")
            self.assertEqual(revision, 1)
            self.assertTrue(allocated.name == "analysis-r001")

    def test_existing_report_cannot_be_overwritten(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            immutable_write(path, "first\n")
            immutable_write(path, "first\n")
            with self.assertRaises(ImmutableArtifactError):
                immutable_write(path, "changed\n")

    def test_registry_rejects_duplicate_report_ids(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reports.jsonl"
            record = {"report_id": "r1", "status": "complete"}
            append_unique(path, record, identity_field="report_id")
            with self.assertRaises(RegistryError):
                append_unique(path, record, identity_field="report_id")
            self.assertEqual(len(read_jsonl(path)), 1)

    def test_confirmatory_execution_fails_closed_on_dirty_tree(self):
        from experiments.harness.common import run_experiment
        with patch("experiments.harness.common.working_tree_clean", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "clean Git tree"):
                run_experiment(experiment_id="test-confirmatory", research_question="test", compute=lambda records: {}, run_mode="confirmatory")

    def test_report_contains_raw_analysis_identity(self):
        report = render_report(result={"research_question": "q", "results": {"metric": 1}, "gate_passed": False}, report_id="hv-v0.5.0__demo__20260909T011532Z-7c4a2f__a001", protocol="hv-v0.5.0", experiment_id="demo", run_id="20260909T011532Z-7c4a2f", revision=1, created_at="2026-09-09T01:15:32+00:00", git_sha="abc", clean=True, identities={"dataset_sha256": "d", "ontology_sha256": "o", "ground_truth_sha256": "g", "verifier_sha256": "v", "attack_suite_sha256": "a", "metric_suite_sha256": "m"}, run_validity="valid", run_mode="development", raw_path=Path("results/raw/demo"), analysis_path=Path("results/analyses/demo"))
        self.assertIn("Report ID: `hv-v0.5.0__demo__20260909T011532Z-7c4a2f__a001`", report)
        self.assertIn("Raw run: `results/raw/demo`", report)
        self.assertIn("Analysis: `results/analyses/demo`", report)

    def test_utc_timestamp_shape_is_second_resolution(self):
        value = new_run_id(now=datetime(2026, 9, 9, 1, 15, 32, tzinfo=timezone.utc), suffix="abcdef")
        self.assertTrue(value.startswith("20260909T011532Z-"))
