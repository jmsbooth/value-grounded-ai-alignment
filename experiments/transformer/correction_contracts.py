#!/usr/bin/env python3
"""Execute the v0.6.2 implementation contract suite and write a receipt."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-contracts")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/contract-tests" / run_id
    command = [sys.executable, "-m", "pytest", "-q", "tests/transformer"]
    completed = subprocess.run(command, cwd=ROOT, env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=False)
    compile_result = subprocess.run([sys.executable, "-m", "compileall", "-q", "src", "experiments/transformer", "tests/transformer"], cwd=ROOT, capture_output=True, text=True, check=False)
    result = {"protocol": "te-v0.6.2-pythia-correction", "experiment_id": "correction-contract-tests", "run_id": run_id, "status": "CORRECTION_IMPLEMENTATION_VALIDATED" if completed.returncode == 0 and compile_result.returncode == 0 else "CORRECTION_IMPLEMENTATION_REJECTED", "pytest": {"command": command, "return_code": completed.returncode, "output": completed.stdout + completed.stderr}, "compileall": {"return_code": compile_result.returncode, "output": compile_result.stdout + compile_result.stderr}, "tests": {"response_eos": completed.returncode == 0, "independent_scoring": completed.returncode == 0, "variant_fidelity": completed.returncode == 0, "accumulation": completed.returncode == 0, "auxiliary_and_accounting": completed.returncode == 0, "mutation_coverage": completed.returncode == 0}, "locked_data_read_or_scored": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="training_diagnostic", protocol=result["protocol"], status=result["status"], experiment_id=result["experiment_id"], run_id=run_id, result_sha256=sha256_file(output), pytest_return_code=completed.returncode, compile_return_code=compile_result.returncode, locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "run_id": run_id, "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return completed.returncode or compile_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
