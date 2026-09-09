from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import random_label_control

if __name__ == "__main__":
    run_experiment(experiment_id="random-label-control", research_question="Does randomizing target labels reduce performance toward chance?", compute=random_label_control)
