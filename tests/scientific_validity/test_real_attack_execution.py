from vgta_eval.model_attacks import execute_model_attacks
from vgta_eval.semantic_worlds import generate_semantic_dataset


def test_attack_results_are_raw_outputs_from_supplied_predictor():
    example = generate_semantic_dataset(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1}).examples[0]
    calls = []
    def predict(text):
        calls.append(text)
        return "raw-output:" + str(len(text))
    results = execute_model_attacks((example,), predict)
    assert len(results) == 4
    assert len(calls) == 4
    assert all(result.executed and result.raw_model_output.startswith("raw-output:") for result in results)

