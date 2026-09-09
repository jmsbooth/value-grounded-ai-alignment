from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import scenario_transformation_validation

if __name__ == "__main__":
    run_experiment(experiment_id="scenario-transformation-validation", research_question="Do invariant transformations preserve outcomes while causal transformations change outcomes where defined?", compute=scenario_transformation_validation)
