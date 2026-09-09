from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import verifier_property_validation

if __name__ == "__main__":
    run_experiment(experiment_id="verifier-property-validation", research_question="Does the verifier obey enumerated safety properties?", compute=verifier_property_validation)
