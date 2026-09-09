from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import ground_truth_independence

if __name__ == "__main__":
    run_experiment(experiment_id="ground-truth-independence", research_question="Can ground-truth outcomes be computed independently of the candidate VGA ontology?", compute=ground_truth_independence)
