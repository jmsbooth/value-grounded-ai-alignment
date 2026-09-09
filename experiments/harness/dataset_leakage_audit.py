from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import dataset_leakage_audit

if __name__ == "__main__":
    run_experiment(experiment_id="dataset-leakage-audit", research_question="Are train and held-out records free of unexplained leakage?", compute=dataset_leakage_audit)
