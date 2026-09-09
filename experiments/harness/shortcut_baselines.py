from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.harness.common import run_experiment
from experiments.harness.experiments import shortcut_baselines

if __name__ == "__main__":
    run_experiment(experiment_id="shortcut-baselines", research_question="Are structured tasks not trivially solved by surface shortcuts?", compute=shortcut_baselines)
