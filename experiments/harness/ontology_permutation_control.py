from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import ontology_permutation_control

if __name__ == "__main__":
    run_experiment(experiment_id="ontology-permutation-control", research_question="Does semantic structure provide information beyond arbitrary graph/features?", compute=ontology_permutation_control)
