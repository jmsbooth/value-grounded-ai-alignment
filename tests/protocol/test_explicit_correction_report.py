"""Integration tests use fixture receipts, not pretrained model outputs."""
import json
import subprocess
import sys
from pathlib import Path

from test_verified_inventory import setup
from vgta_eval.verified_inventory import digest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "experiments/transformer/correction_report.py"


def cli(root: Path, *extra: str):
    return [sys.executable, str(SCRIPT), "--root", str(root), "--inventory", str(root / "inventory.json"),
            "--approved-plan-sha256", digest(root / "plan.json"), "--scope", "fixture", *extra]


def test_explicit_report_creates_unique_hash_bound_artifacts(tmp_path):
    setup(tmp_path)
    a = subprocess.run(cli(tmp_path), capture_output=True, text=True)
    b = subprocess.run(cli(tmp_path), capture_output=True, text=True)
    assert a.returncode == b.returncode == 0, (a.stderr, b.stderr)
    one, two = json.loads(a.stdout), json.loads(b.stdout)
    assert one["report_dir"] != two["report_dir"]
    for entry in (one, two):
        directory = Path(entry["report_dir"])
        report = json.loads((directory / "report.json").read_text())
        manifest = json.loads((directory / "report-manifest.json").read_text())
        assert report["scope"] == "fixture"
        assert report["complete_model_protocol_run"] is False
        assert report["verified_role_count"] == report["required_role_count"] == 1
        assert report["requirements"][0]["assertions_verified"] == 2
        assert manifest["report_json_sha256"] == digest(directory / "report.json")
        assert manifest["report_markdown_sha256"] == digest(directory / "experimental-validation-report.md")
        assert manifest["locked_launch_authorized"] is False


def test_report_rejects_tampered_evidence_without_writing(tmp_path):
    setup(tmp_path)
    (tmp_path / "stdout.txt").write_text("changed evidence")
    result = subprocess.run(cli(tmp_path), capture_output=True, text=True)
    assert result.returncode != 0
    assert "EVIDENCE_REPORT_REJECTED" in result.stderr
    assert not (tmp_path / "results").exists()


def test_report_rejects_legacy_status_only_cohort(tmp_path):
    legacy = tmp_path / "cohort.json"
    legacy.write_text(json.dumps({"status": "PASS", "work_package_status": {"A1": "PASS"}}))
    result = subprocess.run([sys.executable, str(SCRIPT), "--cohort", str(legacy)], capture_output=True, text=True)
    assert result.returncode != 0


def test_report_rejects_overwrite_of_existing_output(tmp_path):
    setup(tmp_path)
    output = tmp_path / "prior"
    output.mkdir()
    (output / "historical.txt").write_text("preserve")
    result = subprocess.run(cli(tmp_path, "--output-dir", str(output)), capture_output=True, text=True)
    assert result.returncode != 0
    assert (output / "historical.txt").read_text() == "preserve"


def test_report_cannot_write_outside_root(tmp_path):
    setup(tmp_path)
    result = subprocess.run(cli(tmp_path, "--output-dir", "/tmp/vga-report-escape"), capture_output=True, text=True)
    assert result.returncode != 0


def test_report_refuses_unpinned_plan(tmp_path):
    setup(tmp_path)
    args = cli(tmp_path)
    args[args.index("--approved-plan-sha256") + 1] = "0" * 64
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode != 0
