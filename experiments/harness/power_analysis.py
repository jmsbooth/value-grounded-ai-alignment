from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import power_analysis

if __name__ == "__main__":
    run_experiment(experiment_id="power-analysis", research_question="What scenario and seed counts should be planned for future Transformer effects?", compute=power_analysis)
