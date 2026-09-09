from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import verifier_mutation_validation

if __name__ == "__main__":
    run_experiment(experiment_id="verifier-mutation-validation", research_question="Do verifier tests detect every explicitly enumerated critical mutation?", compute=verifier_mutation_validation)
