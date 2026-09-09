from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import attack_discrimination

if __name__ == "__main__":
    run_experiment(experiment_id="attack-discrimination", research_question="Does attack difficulty produce useful variation rather than all-zero or all-one outcomes?", compute=attack_discrimination)
