from __future__ import annotations

import json
import pprint
from pathlib import Path

import rich.traceback
import yaml
from rich import print
from rich.panel import Panel

from tests.utils import DEFAULT_VALIDATION_DATA_DIR, traverse_repository_for_filings

rich.traceback.install()


DEFAULT_YAML = Path(__file__).parent / "selected-filings.yaml"
LAST_ACCURACY_TEST_RESULT_PATH = (
    DEFAULT_VALIDATION_DATA_DIR / "last_accuracy_test_result.json"
)


def main() -> None:
    # STEP: Load the YAML file
    with DEFAULT_YAML.open("r") as file:
        selected_filings = yaml.safe_load(file)
    accession_numbers = list(selected_filings["accession_numbers"])
    assert accession_numbers, "No accession numbers found in YAML file."

    # STEP: Load the metrics for each report
    filings = [
        report
        for report in traverse_repository_for_filings()
        if report.accession_number in accession_numbers
    ]
    all_metrics = []
    for report in filings:
        assert (
            report.actual_structure_and_text_summary.exists()
        ), f"missing '{report.actual_structure_and_text_summary.name}' for '{report.identifier}'"
        with report.actual_structure_and_text_summary.open("r") as file:
            summary_data = json.load(file)
        metrics = summary_data["metrics"].copy()
        metrics["identifier"] = report.identifier
        all_metrics.append(metrics)

    # STEP: Aggregate the metrics
    num_filings = len(all_metrics)
    assert num_filings > 0, "No filings found."
    average_expected = sum(m["total_expected"] for m in all_metrics) / num_filings
    average_actual = sum(m["total_actual"] for m in all_metrics) / num_filings
    average_missing = sum(m["total_missing"] for m in all_metrics) / num_filings
    average_unexpected = sum(m["total_unexpected"] for m in all_metrics) / num_filings
    average_precision = (
        sum(float(m["precision"].rstrip("%")) for m in all_metrics) / num_filings
    )
    average_recall = (
        sum(float(m["recall"].rstrip("%")) for m in all_metrics) / num_filings
    )
    average_f1_score = (
        sum(float(m["f1_score"].rstrip("%")) for m in all_metrics) / num_filings
    )
    num_perfect_f1_score = sum(
        1 for m in all_metrics if float(m["f1_score"].rstrip("%")) == 100.00
    )
    num_perfect_recall = sum(
        1 for m in all_metrics if float(m["recall"].rstrip("%")) == 100.00
    )
    summary = {
        "num_filings": {
            "total": num_filings,
            "perfect_f1_score": num_perfect_f1_score,
            "perfect_recall": num_perfect_recall,
            "ratio_perfect_f1_score": f"{num_perfect_f1_score / num_filings:.2%}",
            "ratio_perfect_recall": f"{num_perfect_recall / num_filings:.2%}",
        },
        "average_metrics": {
            "f1_score": f"{average_f1_score:.2f}%",
            "precision": f"{average_precision:.2f}%",
            "recall": f"{average_recall:.2f}%",
        },
        "average_elements": {
            "expected": f"{average_expected:g}",
            "actual": f"{average_actual:g}",
            "missing": f"{average_missing:g}",
            "unexpected": f"{average_unexpected:g}",
        },
        "total_missing": {},
        "total_unexpected": {},
    }
    for metrics in all_metrics:
        for element_type, count in metrics["missing_elements_by_type"].items():
            summary["total_missing"].setdefault(element_type, 0)
            summary["total_missing"][element_type] += count
        for element_type, count in metrics["unexpected_elements_by_type"].items():
            summary["total_unexpected"].setdefault(element_type, 0)
            summary["total_unexpected"][element_type] += count

    # STEP: Show and save the summary
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Selected filings", style="dim", width=33)
    table.add_column("F1-score", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("Precision", justify="right")
    table.add_column("Missing", justify="right")
    table.add_column("Unexpected", justify="right")
    table.add_column("Total", justify="right")

    for m in all_metrics:
        table.add_row(
            m["identifier"],
            str(m["f1_score"]),
            str(m["recall"]),
            str(m["precision"]),
            str(m["total_missing"]),
            str(m["total_unexpected"]),
            str(m["total_actual"]),
        )
    console.print(table)
    print(
        json.dumps(summary, indent=4, sort_keys=False, ensure_ascii=False),
    )
    with LAST_ACCURACY_TEST_RESULT_PATH.open("w") as file:
        saved_summary = summary.copy()
        saved_summary["selected_filings"] = {
            m["identifier"]: {k: v for k, v in m.items() if k != "identifier"}
            for m in all_metrics
        }
        json.dump(saved_summary, file, indent=4, sort_keys=False, ensure_ascii=False)


if __name__ == "__main__":
    main()
