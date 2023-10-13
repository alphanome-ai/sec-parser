from __future__ import annotations

import contextlib
import difflib
import io
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal, Tuple

import yaml
from millify import millify
from rich import console, print
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from sec_parser import Edgar10QParser
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

AVAILABLE_ACTIONS = ["generate", "verify"]
ALLOWED_MICROSECONDS_PER_CHAR = 1


class VerificationFailedError(ValueError):
    pass


@dataclass
class VerificationResult:
    document_type: str
    company_name: str
    report_name: str
    execution_time_in_seconds: float
    character_count: int
    unexpected_count: int
    missing_count: int
    allowed_execution_time_in_seconds: float

    def get_report_identifier(self) -> str:
        return f"{self.document_type}_{self.company_name}_{self.report_name}"

    def errors_found(self) -> bool:
        return (
            self.missing_count > 0
            or self.unexpected_count > 0
            or self.execution_time_in_seconds > self.allowed_execution_time_in_seconds
        )


def _generate(json_file: Path, elements: list[AbstractSemanticElement]) -> None:
    with json_file.open("w") as f:
        items = [e.to_dict() for e in elements]
        json.dump(items, f, indent=4)


def compare_elements(
    elements: list[AbstractSemanticElement],
    expected_items: list[dict],
) -> tuple[list, list]:
    unexpected_items, missing_items = [], []
    i, j = 0, 0
    while i < len(elements) and j < len(expected_items):
        el_dict = elements[i].to_dict()
        if {k: v for k, v in el_dict.items() if k != "id"} == {
            k: v for k, v in expected_items[j].items() if k != "id"
        }:
            i += 1
            j += 1
        elif i < j:
            unexpected_items.append(el_dict)
            i += 1
        else:
            missing_items.append(expected_items[j])
            j += 1
    unexpected_items.extend(el.to_dict() for el in elements[i:])
    missing_items.extend(expected_items[j:])
    return unexpected_items, missing_items


def print_verification_result_table(
    results: list[VerificationResult],
) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Report", style="dim")
    table.add_column(
        "Accuracy",
        justify="center",
    )
    table.add_column("Execution Time\n(Limit, %Limit, Size)", justify="center")

    for result in results:
        if result.missing_count and result.unexpected_count:
            accuracy_str = f"[bold red]{result.missing_count} Missing, {result.unexpected_count} Unexpected[/bold red]"
        elif result.missing_count:
            accuracy_str = f"[bold red]{result.missing_count} Missing[/bold red]"
        elif result.unexpected_count:
            accuracy_str = f"[bold red]{result.unexpected_count} Unexpected[/bold red]"
        else:
            accuracy_str = "[bold green]✓[/bold green]"

        speed_percentage = (
            100
            * result.execution_time_in_seconds
            / result.allowed_execution_time_in_seconds
        )
        speed_str = (
            f"[bold cyan]{result.execution_time_in_seconds * 1000:.0f}ms[/bold cyan] "
            f"([dim]{result.allowed_execution_time_in_seconds * 1000:.0f}ms, "
            f"{speed_percentage:.0f}%, "
            f"{millify(result.character_count)}[/dim])"
        )

        table.add_row(
            f"[bold]{result.get_report_identifier()}[/bold]"
            if result.errors_found()
            else f"{result.get_report_identifier()}",
            accuracy_str,
            speed_str,
        )

    console.print(table)
    print(
        f"[dim]Note: Execution Time Limit is based on a set rate of [bold]{ALLOWED_MICROSECONDS_PER_CHAR}[/bold] microseconds per HTML character (Size).[/dim]\n",
    )


def manage_snapshots(action: Literal["generate", "verify"], data_dir: str) -> None:
    assert action in AVAILABLE_ACTIONS
    dir_path = Path(data_dir)
    results: list[VerificationResult] = []
    for document_type_dir in dir_path.iterdir():
        if document_type_dir.name.startswith("."):
            continue
        if not document_type_dir.is_dir():
            continue
        for company_dir in document_type_dir.iterdir():
            if not company_dir.is_dir():
                continue
            for report_dir in company_dir.iterdir():
                html_file = report_dir / "primary-document.html"
                json_file = report_dir / "semantic-elements-list.json"
                if not html_file.exists():
                    msg = f"HTML file not found: {html_file}"
                    raise FileNotFoundError(msg)

                with html_file.open("r") as f:
                    html_content = f.read()

                execution_time_start = time.perf_counter()
                elements = Edgar10QParser().parse(html_content)
                execution_time_in_seconds = time.perf_counter() - execution_time_start

                if action == "generate":
                    _generate(json_file, elements)
                else:
                    with json_file.open("r") as f:
                        expected_contents = f.read()
                    actual_contents = json.dumps(
                        [e.to_dict() for e in elements],
                        indent=4,
                    )
                    with json_file.with_suffix(".actual.json").open("w") as f:
                        f.write(actual_contents)

                    missing_count, unexpected_count = show_diff_with_line_numbers(
                        expected_contents,
                        actual_contents,
                        f"[dim]{document_type_dir.name}_{company_dir.name}_{report_dir.name}[/dim]",
                    )

                    character_count = len(html_content)
                    allowed_execution_time_in_seconds = (
                        character_count * ALLOWED_MICROSECONDS_PER_CHAR / 1_000_000
                    )
                    result = VerificationResult(
                        document_type=document_type_dir.name,
                        company_name=company_dir.name,
                        report_name=report_dir.name,
                        execution_time_in_seconds=execution_time_in_seconds,
                        character_count=character_count,
                        allowed_execution_time_in_seconds=allowed_execution_time_in_seconds,
                        missing_count=missing_count,
                        unexpected_count=unexpected_count,
                    )
                    results.append(result)

    if action == "verify":
        print_verification_result_table(results)
        if any(result.errors_found() for result in results):
            raise VerificationFailedError("[ERROR] Verification failed.")
        print("Verification of the end-to-end snapshots completed successfully.")


def show_diff_with_line_numbers(expected, actual, identifier):
    identifier = identifier.ljust(25)
    word1, word2 = "\[expected]:", "\[actual]:"
    d = difflib.Differ()
    diff = list(d.compare(expected.splitlines(), actual.splitlines()))

    line_number_expected = 0
    line_number_actual = 0
    missing_count = 0
    unexpected_count = 0
    for line in diff:
        if line.startswith("  "):
            line_number_expected += 1
            line_number_actual += 1
        elif line.startswith("- "):
            print(
                f'"{identifier}" Line {line_number_expected + 1} {word1.ljust(len(word2))} {line[2:].strip()}',
            )
            missing_count += 1
            line_number_expected += 1
        elif line.startswith("+ "):
            print(
                f'"{identifier}" Line {line_number_actual + 1} {word2.ljust(len(word1))} {line[2:].strip()}',
            )
            unexpected_count += 1
            line_number_actual += 1
    return missing_count, unexpected_count
