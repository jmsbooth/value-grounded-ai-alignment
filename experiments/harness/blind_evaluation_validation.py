from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import blind_evaluation_validation

if __name__ == "__main__":
    run_experiment(experiment_id="blind-evaluation-validation", research_question="Can variant identity remain hidden through metric generation?", compute=blind_evaluation_validation)
