from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import sham_feature_control

if __name__ == "__main__":
    run_experiment(experiment_id="sham-feature-control", research_question="Are intended semantic improvements distinguishable from matched sham features?", compute=sham_feature_control)
