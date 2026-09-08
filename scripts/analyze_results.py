#!/usr/bin/env python3
"""Analyze immutable pilot outputs and generate paper-facing artifacts.

The script consumes raw JSONL predictions and run manifests only. Generated
tables, facts, and TikZ figures are reproducible from those inputs; no
empirical number is typed into the manuscript by hand.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.attacks import attack_summary
from vgta_eval.metrics import metric_summary
from vgta_eval.scenario_generator import CONFLICT_LABELS
from vgta_eval.statistical_tests import paired_bootstrap_difference, summarize_seed_values


PRIMARY_METRICS = (
    "moral_salience_recall",
    "normative_conflict_f1",
    "structural_ood_accuracy",
    "useful_conformance_rate",
)
ANALYSIS_METRICS = PRIMARY_METRICS + ("purpose_accuracy", "adversarial_success_rate", "action_accuracy", "counterfactual_consistency", "capability_accuracy", "ontology_degradation_accuracy", "mean_action_confidence", "false_confidence_rate")
VARIANTS = ("A1", "B", "C1", "C2")
CONTRASTS = (("A1", "B", "A1_vs_B"), ("B", "C1", "B_vs_C1"), ("C1", "C2", "C1_vs_C2"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_runs(raw_root: Path) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
    runs: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for manifest_path in sorted(raw_root.glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        predictions = _read_jsonl(manifest_path.parent / "predictions.jsonl")
        if manifest["model_variant"] not in VARIANTS:
            continue
        runs.append((manifest, predictions))
    if not runs:
        raise FileNotFoundError(f"no run manifests found under {raw_root}")
    return runs


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _f(value: float) -> str:
    return f"{value:.3f}"


def _pp(value: float) -> str:
    return f"{value * 100.0:+.1f} pp"


def _tex(value: Any) -> str:
    return str(value).replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def _effect_text(value: Any) -> str:
    if value is None:
        return "NA (zero paired variance)"
    numeric = float(value)
    if not math.isfinite(numeric):
        return "NA (non-finite effect)"
    return f"{numeric:+.3f}"


def _resolution(difference: float, interval: Sequence[float], standardized_effect: float | None, threshold: float = 0.05, effect_threshold: float = 0.20) -> str:
    effect_clears_threshold = standardized_effect is not None and abs(standardized_effect) >= effect_threshold
    if interval[0] >= threshold and effect_clears_threshold:
        return "criterion met"
    if interval[1] <= -threshold:
        return "criterion not met"
    return "inconclusive"


def _tikz_bar_chart(path: Path, title: str, values: Mapping[str, float], *, y_label: str = "score") -> None:
    labels = list(values)
    width = 0.55
    height = 4.0
    lines = [
        "\\documentclass[tikz,border=5pt]{standalone}",
        "\\begin{document}",
        "\\begin{tikzpicture}[font=\\sffamily\\footnotesize]",
        f"\\node[font=\\sffamily\\small\\bfseries] at (3.6,4.8) {{{title}}};",
        "\\draw[->] (0,0) -- (7.2,0);",
        "\\draw[->] (0,0) -- (0,4.35);",
        f"\\node[rotate=90] at (-0.45,2.2) {{{y_label}}};",
    ]
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = tick * height
        lines.append(f"\\draw[gray!35] (0,{y:.3f}) -- (7.0,{y:.3f});")
        lines.append(f"\\node[anchor=east] at (-0.08,{y:.3f}) {{{tick:.2f}}};")
    for index, label in enumerate(labels):
        x = 0.55 + index * 1.55
        value = max(0.0, min(1.0, float(values[label])))
        lines.append(f"\\fill[black!{25 + index * 15}] ({x:.3f},0) rectangle ({x + width:.3f},{value * height:.3f});")
        lines.append(f"\\node[anchor=north] at ({x + width / 2:.3f},-0.08) {{{label}}};")
        lines.append(f"\\node[anchor=south] at ({x + width / 2:.3f},{value * height + 0.05:.3f}) {{{value:.2f}}};")
    lines.extend(["\\end{tikzpicture}", "\\end{document}"])
    source = path.with_suffix(".tex")
    source.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _tikz_line_chart(path: Path, title: str, series: Mapping[str, Sequence[tuple[float, float]]], *, y_label: str = "accuracy") -> None:
    lines = [
        "\\documentclass[tikz,border=5pt]{standalone}",
        "\\begin{document}",
        "\\begin{tikzpicture}[font=\\sffamily\\footnotesize]",
        f"\\node[font=\\sffamily\\small\\bfseries] at (3.8,4.8) {{{title}}};",
        "\\draw[->] (0,0) -- (7.4,0);",
        "\\draw[->] (0,0) -- (0,4.35);",
        f"\\node[rotate=90] at (-0.45,2.2) {{{y_label}}};",
    ]
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = tick * 4.0
        lines.append(f"\\draw[gray!35] (0,{y:.3f}) -- (7.2,{y:.3f});")
        lines.append(f"\\node[anchor=east] at (-0.08,{y:.3f}) {{{tick:.2f}}};")
    colors = ("black", "black!55")
    for series_index, (label, points) in enumerate(series.items()):
        coords = " -- ".join(f"({0.6 + x * 1.35:.3f},{max(0.0, min(1.0, y)) * 4.0:.3f})" for x, y in points)
        lines.append(f"\\draw[{colors[series_index % len(colors)]}, thick] {coords};")
        for x, y in points:
            lines.append(f"\\fill[{colors[series_index % len(colors)]}] ({0.6 + x * 1.35:.3f},{max(0.0, min(1.0, y)) * 4.0:.3f}) circle (1.2pt);")
        lines.append(f"\\node[anchor=west] at ({5.9 + (series_index % 2) * 0.8:.2f},{4.1 - (series_index // 2) * 0.35:.2f}) {{{label}}};")
    lines.extend(["\\node[anchor=north] at (3.8,-0.18) {ontology coverage};", "\\end{tikzpicture}", "\\end{document}"])
    source = path.with_suffix(".tex")
    source.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _compile_figure(source: Path) -> None:
    target_dir = source.parent
    configured = os.environ.get("TECTONIC_BIN")
    tectonic = Path(configured) if configured else Path(shutil.which("tectonic") or "/Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6/bin/tectonic")
    if not tectonic.exists():
        raise FileNotFoundError("Tectonic is required to compile generated result figures")
    subprocess.run([str(tectonic), "-X", "compile", "--outdir", str(target_dir), "--outfmt", "pdf", "--untrusted", str(source)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def _write_generated_latex(summary_rows: Sequence[Mapping[str, Any]], contrast_rows: Sequence[Mapping[str, Any]], security_rows: Sequence[Mapping[str, Any]], conformance_rows: Sequence[Mapping[str, Any]], hypothesis_rows: Sequence[Mapping[str, Any]], group_manifest: Mapping[str, Any], metadata: Mapping[str, Any]) -> None:
    generated = ROOT / "paper/generated"
    generated.mkdir(parents=True, exist_ok=True)
    scientific_status = str(group_manifest.get("scientific_status", "unknown"))
    (generated / "experiment-metadata.tex").write_text(
        "\\noindent\\textit{Generated pilot status: " + scientific_status.replace("_", "\\_") + "; "
        + str(group_manifest.get("run_group", "unknown")).replace("_", "\\_")
        + ". Results are from a synthetic shared-MLP mechanism-validation proxy and are not Transformer evidence.}\\par\n",
        encoding="utf-8",
    )
    lines = [
        "\\begin{table}[t]",
        "\\centering\\scriptsize",
        "\\caption{Generated small-pilot metrics on the sealed logical split.}",
        "\\label{tab:generated-primary-results}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Variant & Salience recall & Conflict F1 & Structural OOD & UCR\\\\",
        "\\midrule",
    ]
    by_variant: dict[str, dict[str, Mapping[str, Any]]] = {}
    for row in summary_rows:
        by_variant.setdefault(str(row["variant"]), {})[str(row["metric"])] = row
    for variant in VARIANTS:
        row = by_variant.get(variant, {})
        values = [float(row.get(metric, {}).get("mean", 0.0)) for metric in PRIMARY_METRICS]
        lines.append(variant + " & " + " & ".join(f"{value:.2f}" for value in values) + "\\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", "\\input{generated/experiment-metadata}"])
    (generated / "primary-results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (generated / "ablation-results.tex").write_text(
        "\\begin{table}[t]\\centering\\scriptsize\\caption{Generated preregistered paired contrasts.}"
        "\\begin{tabular}{llrrr}\\toprule Contrast & Metric & Difference & CI low & CI high\\\\\\midrule\n"
        + "\n".join(f"{_tex(row['contrast'])} & {_tex(row['metric'])} & {float(row['difference']):+.2f} & {float(row['ci_low']):+.2f} & {float(row['ci_high']):+.2f}\\\\" for row in contrast_rows[:12])
        + "\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )
    (generated / "security-results.tex").write_text(
        "\\begin{table}[t]\\centering\\scriptsize\\caption{Generated synthetic attack success rates; lower is better.}"
        "\\begin{tabular}{lrrrr}\\toprule Attack & A1 & B & C1 & C2\\\\\\midrule\n"
        + "\n".join(
            _tex(attack) + " & " + " & ".join(f"{float(next((row['success_rate'] for row in security_rows if row['attack'] == attack and row['variant'] == variant), 0.0)):.2f}" for variant in VARIANTS) + "\\\\"
            for attack in sorted({str(row["attack"]) for row in security_rows})
        )
        + "\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )
    summary_lookup = {(str(row["variant"]), str(row["metric"])): row for row in summary_rows}
    secondary_metrics = ("action_accuracy", "purpose_accuracy", "capability_accuracy", "mean_action_confidence", "false_confidence_rate")
    secondary_lines = [
        "\\begin{table}[t]\\centering\\scriptsize",
        "\\caption{Generated secondary outcomes on the sealed logical split.}",
        "\\label{tab:generated-secondary-results}",
        "\\begin{tabular}{lrrrrr}\\toprule",
        "Variant & Action & Purpose & Capability & Mean conf. & False conf.\\\\\\midrule",
    ]
    for variant in VARIANTS:
        values = [float(summary_lookup[(variant, metric)]["mean"]) for metric in secondary_metrics]
        secondary_lines.append(variant + " & " + " & ".join(f"{value:.2f}" for value in values) + "\\\\")
    secondary_lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    (generated / "secondary-results.tex").write_text("\n".join(secondary_lines) + "\n", encoding="utf-8")

    raw_root = ROOT / str(metadata["raw_root"])
    run_manifests = []
    for run_id in group_manifest.get("runs", []):
        manifest_path = raw_root / str(run_id) / "manifest.json"
        if manifest_path.exists():
            run_manifests.append(json.loads(manifest_path.read_text(encoding="utf-8")))
    reference_manifest = run_manifests[0] if run_manifests else {}
    dataset_manifest = group_manifest.get("dataset_manifest", {})
    overlap = group_manifest.get("sealed_structural_topology_overlap_with_train", [])
    hardware = reference_manifest.get("hardware", group_manifest.get("hardware", {}))
    reproducibility_rows = [
        ("Repository commit", group_manifest.get("git_sha", "unknown")),
        ("Run group", group_manifest.get("run_group", "unknown")),
        ("Dataset / generator", f"{dataset_manifest.get('dataset_version', reference_manifest.get('dataset_version', 'unknown'))} / {dataset_manifest.get('generator_version', 'unknown')}"),
        ("Configuration hash", str(group_manifest.get("config_sha", reference_manifest.get("config_sha", "unknown")))[:16]),
        ("Ontology / verifier", f"{reference_manifest.get('ontology_version', 'unknown')} / {reference_manifest.get('verifier_version', 'unknown')}"),
        ("Prediction rows", group_manifest.get("prediction_rows", metadata.get("processed_seed_metrics", [{}])[0].get("sealed_test_rows", "unknown"))),
        ("Seeds", ", ".join(str(seed) for seed in group_manifest.get("seeds", []))),
        ("Structural OOD leakage", "none" if not overlap else ", ".join(str(item) for item in overlap)),
        ("Hardware", f"{hardware.get('platform', 'unknown')}; {hardware.get('machine', 'unknown')}; GPU={hardware.get('gpu', 'unknown')}"),
        ("Approx. FLOPs", f"train {metadata.get('cost_accounting', {}).get('training_flops_estimate', 'unknown')}; inference {metadata.get('cost_accounting', {}).get('inference_flops_estimate', 'unknown')}"),
    ]
    reproducibility_lines = [
        "\\begin{table}[t]\\centering\\scriptsize",
        "\\caption{Generated reproducibility record for the analyzed pilot.}",
        "\\label{tab:generated-reproducibility}",
        "\\begin{tabularx}{\\linewidth}{@{}p{0.28\\linewidth}X@{}}\\toprule Field & Recorded value\\\\\\midrule",
    ]
    reproducibility_lines.extend(f"{_tex(field)} & {_tex(value)}\\\\" for field, value in reproducibility_rows)
    reproducibility_lines.extend(["\\bottomrule", "\\end{tabularx}", "\\end{table}"])
    (generated / "reproducibility.tex").write_text("\n".join(reproducibility_lines) + "\n", encoding="utf-8")
    (generated / "conformance-results.tex").write_text(
        "\\begin{table}[t]\\centering\\scriptsize\\caption{Generated conformance and ontology-coverage summaries.}"
        "\\begin{tabular}{lrrr}\\toprule Variant & Coverage & Accuracy & Rejection\\\\\\midrule\n"
        + "\n".join(f"{row['variant']} & {row['coverage']} & {float(row['accuracy']):.2f} & {float(row['rejection_rate']):.2f}\\\\" for row in conformance_rows)
        + "\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )
    (generated / "hypothesis-resolution.tex").write_text(
        "\\begin{table}[t]\\centering\\scriptsize\\caption{Generated hypothesis-resolution status for the local pilot.}"
        "\\begin{tabular}{lll}\\toprule Hypothesis & Test & Status\\\\\\midrule\n"
        + "\n".join(f"{_tex(row['hypothesis'])} & {_tex(row['test'])} & {_tex(row['status'])}\\\\" for row in hypothesis_rows)
        + "\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )


def analyze(raw_root: Path) -> dict[str, Any]:
    runs = _load_runs(raw_root)
    by_variant_seed: dict[str, dict[int, tuple[dict[str, Any], list[dict[str, Any]]]]] = {variant: {} for variant in VARIANTS}
    for manifest, rows in runs:
        by_variant_seed[str(manifest["model_variant"])][int(manifest["seed"])] = (manifest, rows)
    summary_rows: list[dict[str, Any]] = []
    processed_rows: list[dict[str, Any]] = []
    metric_values: dict[tuple[str, str], list[float]] = {}
    metric_by_seed: dict[tuple[str, str], dict[int, float]] = {}
    for variant in VARIANTS:
        for seed, (manifest, rows) in sorted(by_variant_seed[variant].items()):
            metrics = metric_summary([row for row in rows if row["split"] == "sealed-test"], CONFLICT_LABELS)
            processed_rows.append({
                "run_id": manifest["run_id"],
                "variant": variant,
                "seed": seed,
                "scientific_status": manifest.get("scientific_status", "unknown"),
                "training_seconds": manifest.get("training_seconds", 0.0),
                "gpu_hours": manifest.get("gpu_hours", 0.0),
                "training_flops_estimate": manifest.get("training_flops_estimate", 0),
                "inference_flops_estimate": manifest.get("inference_flops_estimate", 0),
                **{metric: float(metrics[metric]) for metric in ANALYSIS_METRICS},
            })
            for metric in ANALYSIS_METRICS:
                metric_by_seed.setdefault((variant, metric), {})[seed] = float(metrics[metric])
        for metric in ANALYSIS_METRICS:
            values = [value for _, value in sorted(metric_by_seed.get((variant, metric), {}).items())]
            if not values:
                continue
            summary = summarize_seed_values(values)
            metric_values[(variant, metric)] = values
            summary_rows.append({"variant": variant, "metric": metric, **summary, "scope": "sealed-test", "scientific_status": "pilot-uncommitted"})

    contrast_rows: list[dict[str, Any]] = []
    for left, right, contrast in CONTRASTS:
        for metric in PRIMARY_METRICS + ("purpose_accuracy", "adversarial_success_rate"):
            left_values = [metric_by_seed[(left, metric)][seed] for seed in sorted(metric_by_seed[(left, metric)]) if seed in metric_by_seed[(right, metric)]]
            right_values = [metric_by_seed[(right, metric)][seed] for seed in sorted(metric_by_seed[(left, metric)]) if seed in metric_by_seed[(right, metric)]]
            difference, interval, effect = paired_bootstrap_difference(left_values, right_values)
            contrast_rows.append({"contrast": contrast, "metric": metric, "difference": difference, "ci_low": interval[0], "ci_high": interval[1], "standardized_effect": effect, "n_seeds": len(left_values)})

    security_rows: list[dict[str, Any]] = []
    for variant in VARIANTS:
        for seed, (_, rows) in sorted(by_variant_seed[variant].items()):
            for attack, values in attack_summary(row for row in rows if row["split"] == "sealed-test").items():
                security_rows.append({"variant": variant, "seed": seed, "attack": attack, **values})
    security_aggregate: list[dict[str, Any]] = []
    for variant in VARIANTS:
        for attack in sorted({str(row["attack"]) for row in security_rows}):
            values = [float(row["success_rate"]) for row in security_rows if row["variant"] == variant and row["attack"] == attack]
            security_aggregate.append({"variant": variant, "attack": attack, "success_rate": mean(values) if values else 0.0, "n_seeds": len(values)})

    conformance_rows: list[dict[str, Any]] = []
    for variant in VARIANTS:
        for coverage in (100, 75, 50, 25, 0):
            values = []
            rejections = []
            for _, rows in by_variant_seed[variant].values():
                subset = [row for row in rows if row["split"] == "sealed-test" and row["family"] == "ontology_degradation" and int((row["coverage"] or 0.0) * 100) == coverage]
                values.extend(bool(row["action_correct"]) for row in subset)
                rejections.extend(not bool(row["verifier_permitted"]) for row in subset)
            conformance_rows.append({"variant": variant, "coverage": coverage, "accuracy": sum(values) / len(values) if values else 0.0, "rejection_rate": sum(rejections) / len(rejections) if rejections else 0.0, "n": len(values)})

    hypothesis_results: list[dict[str, Any]] = []
    contrast_lookup = {(row["contrast"], row["metric"]): row for row in contrast_rows}
    # The stored contrast is left minus right. These hypotheses predict that
    # the right-hand variant improves the metric, so the factual result is
    # reported as right minus left for a uniform interpretation.
    mappings = (
        ("H1", "moral salience", "B_vs_C1", "moral_salience_recall"),
        ("H2", "structural OOD", "B_vs_C1", "structural_ood_accuracy"),
        ("H3", "adversarial prompting", "A1_vs_B", "adversarial_success_rate"),
        ("H4", "useful conformance", "A1_vs_B", "useful_conformance_rate"),
        ("H5", "purpose relevance", "A1_vs_B", "purpose_accuracy"),
        ("H9", "normative conflict", "C1_vs_C2", "normative_conflict_f1"),
    )
    for hypothesis, test, contrast, metric in mappings:
        row = contrast_lookup.get((contrast, metric))
        if row is None:
            # H3 is a lower-is-better metric, so reverse the interpretation.
            row = contrast_lookup.get((contrast, metric))
        if row is None:
            hypothesis_results.append({"hypothesis": hypothesis, "test": test, "status": "untested"})
        else:
            difference = -float(row["difference"])
            interval = (-float(row["ci_high"]), -float(row["ci_low"]))
            hypothesis_results.append({"hypothesis": hypothesis, "test": test, "metric": metric, "difference": difference, "ci_low": interval[0], "ci_high": interval[1], "standardized_effect": row["standardized_effect"], "status": _resolution(difference, interval, row["standardized_effect"])})
    hypothesis_results.extend([
        {"hypothesis": "H6", "test": "MoE routing", "status": "untested"},
        {"hypothesis": "H7", "test": "continual-learning protection", "status": "exploratory"},
        {"hypothesis": "H8", "test": "axiological conformance stability", "status": "exploratory"},
    ])

    output = ROOT / "results"
    _write_csv(output / "tables/primary-results.csv", summary_rows, ("variant", "metric", "n_seeds", "mean", "seed_stddev", "bootstrap_95_ci", "scope", "scientific_status"))
    contrast_csv_rows = [dict(row, standardized_effect=_effect_text(row["standardized_effect"])) for row in contrast_rows]
    _write_csv(output / "tables/ablation-results.csv", contrast_csv_rows, ("contrast", "metric", "difference", "ci_low", "ci_high", "standardized_effect", "n_seeds"))
    _write_csv(output / "tables/security-results.csv", security_aggregate, ("variant", "attack", "success_rate", "n_seeds"))
    _write_csv(output / "tables/conformance-results.csv", conformance_rows, ("variant", "coverage", "accuracy", "rejection_rate", "n"))
    _write_csv(
        output / "processed/seed-metrics.csv",
        processed_rows,
        ("run_id", "variant", "seed", "scientific_status", "training_seconds", "gpu_hours", "training_flops_estimate", "inference_flops_estimate", *ANALYSIS_METRICS),
    )
    cost_accounting = {
        "runs": len(processed_rows),
        "training_seconds": sum(float(row["training_seconds"]) for row in processed_rows),
        "gpu_hours": sum(float(row["gpu_hours"]) for row in processed_rows),
        "training_flops_estimate": sum(int(row["training_flops_estimate"]) for row in processed_rows),
        "inference_flops_estimate": sum(int(row["inference_flops_estimate"]) for row in processed_rows),
        "method": "Per-run manifests use 2 * allocated parameters * examples * epochs for training and 2 * allocated parameters * predictions for inference; CPU-only approximate accounting.",
    }
    statistics = {
        "raw_root": str(raw_root.relative_to(ROOT)),
        "scientific_status": "pilot-uncommitted",
        "primary_results": summary_rows,
        "contrasts": contrast_rows,
        "security": security_aggregate,
        "conformance": conformance_rows,
        "processed_seed_metrics": processed_rows,
        "cost_accounting": cost_accounting,
        "hypotheses": hypothesis_results,
        "negative_results": [row for row in contrast_rows if float(row["difference"]) <= 0.0],
        "caveat": "Synthetic benchmark and shared-MLP proxy; not Transformer, population, or human-morality evidence.",
    }
    (output / "statistics/summary.json").write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    facts = [
        "# Generated result facts",
        "",
        "Status: `pilot-uncommitted`.",
        "These facts are generated from raw JSONL outputs and describe a synthetic shared-MLP mechanism-validation proxy. They are not claims about a trained Transformer or real-world security.",
        "",
        f"- Cost accounting across {cost_accounting['runs']} runs: {cost_accounting['training_seconds']:.2f} CPU-seconds; {cost_accounting['training_flops_estimate']} estimated training FLOPs; {cost_accounting['inference_flops_estimate']} estimated inference FLOPs; GPU hours {cost_accounting['gpu_hours']:.1f}.",
    ]
    for row in contrast_rows:
        facts.append(f"- `{row['contrast']}` / `{row['metric']}`: difference {float(row['difference']):+.3f}; 95% bootstrap CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}]; standardized paired effect {_effect_text(row['standardized_effect'])}.")
    (output / "statistics/result-facts.md").write_text("\n".join(facts) + "\n", encoding="utf-8")
    _write_generated_latex(summary_rows, contrast_rows, security_aggregate, conformance_rows, hypothesis_results, json.loads((raw_root / "group-manifest.json").read_text(encoding="utf-8")), statistics)

    primary_values = {variant: float(next(row["mean"] for row in summary_rows if row["variant"] == variant and row["metric"] == "structural_ood_accuracy")) for variant in VARIANTS}
    _tikz_bar_chart(output / "figures/primary-results", "Structural-OOD accuracy", primary_values, y_label="accuracy")
    _compile_figure(output / "figures/primary-results.tex")
    _tikz_bar_chart(output / "figures/ood-results", "Action accuracy on structural OOD", primary_values, y_label="accuracy")
    _compile_figure(output / "figures/ood-results.tex")
    degradation = {variant: [(index, next(row["accuracy"] for row in conformance_rows if row["variant"] == variant and row["coverage"] == coverage)) for index, coverage in enumerate((100, 75, 50, 25, 0))] for variant in VARIANTS}
    _tikz_line_chart(output / "figures/ontology-degradation", "Ontology degradation", degradation)
    _compile_figure(output / "figures/ontology-degradation.tex")
    drift_series: dict[str, Sequence[tuple[float, float]]] = {}
    for variant in ("C1", "C2"):
        points = []
        for index, (_, rows) in enumerate(sorted(by_variant_seed[variant].items())):
            del rows
            manifest = by_variant_seed[variant][sorted(by_variant_seed[variant])[index]][0]
            drift = manifest["drift_summary"]
            points.append((index, max(0.0, min(1.0, float(drift.get("acd_unrestricted", 0.0)) + 0.5))))
        drift_series[variant] = points
    _tikz_line_chart(output / "figures/conformance-drift", "Conformance drift (offset display)", drift_series, y_label="offset ACD")
    _compile_figure(output / "figures/conformance-drift.tex")
    attack_values = {variant: mean(float(row["success_rate"]) for row in security_aggregate if row["variant"] == variant) if any(row["variant"] == variant for row in security_aggregate) else 0.0 for variant in VARIANTS}
    _tikz_bar_chart(output / "figures/security-results", "Synthetic attack success", attack_values, y_label="success rate")
    _compile_figure(output / "figures/security-results.tex")
    (ROOT / "paper/generated/result-facts.md").write_text((output / "statistics/result-facts.md").read_text(encoding="utf-8"), encoding="utf-8")
    return statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.raw_root.resolve())
    print(f"Analyzed raw results from {args.raw_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
