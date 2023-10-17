from __future__ import annotations

import contextlib
import difflib
import fnmatch
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
DEFAULT_YAML_FILTER_PATH = Path(__file__).parent / "e2e_test_data.yaml"


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


@dataclass
class GenerationResult:
    created_files: int
    modified_files: int
    removed_lines: int
    added_lines: int

    def __str__(self) -> str:
        return f"Success! Created {self.created_files} files, Modified {self.modified_files} files, with {self.removed_lines} removed lines and {self.added_lines} added lines"


def _generate(
    json_file: Path, elements: list[AbstractSemanticElement]
) -> GenerationResult:
    dict_items = [e.to_dict() for e in elements]
    created_files = 0
    modified_files = 0
    removed_lines = 0
    added_lines = 0

    if json_file.exists():
        with json_file.open("r") as f:
            old_content = f.read()
        new_content = json.dumps(dict_items, indent=4)
        diff = list(
            difflib.unified_diff(old_content.splitlines(), new_content.splitlines())
        )
        for line in diff:
            if line.startswith("-"):
                removed_lines += 1
            elif line.startswith("+"):
                added_lines += 1
        modified_files += 1
    else:
        created_files += 1
        added_lines += len(dict_items)

    with json_file.open("w") as f:
        json.dump(dict_items, f, indent=4)

    return GenerationResult(created_files, modified_files, removed_lines, added_lines)


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


def manage_snapshots(
    action: Literal["generate", "verify"],
    data_dir: str,
    document_types: list[str] | None,
    company_names: list[str] | None,
    report_ids: list[str] | None,
    yaml_path_str: str | None,
) -> None:
    if action not in AVAILABLE_ACTIONS:
        msg = f"Invalid action. Available actions are: {AVAILABLE_ACTIONS}"
        raise ValueError(msg)

    yaml_path = Path(yaml_path_str) if yaml_path_str else None
    if (
        not document_types
        and not company_names
        and not report_ids
        and not yaml_path_str
    ):
        if not DEFAULT_YAML_FILTER_PATH.exists():
            msg = f"No filter arguments provided and {yaml_path} does not exist."
            raise FileNotFoundError(msg)
        yaml_path = DEFAULT_YAML_FILTER_PATH

    document_types = list(document_types) if document_types else []
    company_names = list(company_names) if company_names else []
    report_ids = list(report_ids) if report_ids else []
    if yaml_path:
        filters = load_yaml_filter(yaml_path)
        document_types.extend(filters.get("document_types", []))
        company_names.extend(filters.get("company_names", []))
        report_ids.extend(filters.get("report_ids", []))

    if not document_types and not company_names and not report_ids:
        msg = "No filters provided in document_types, company_names, or report_ids."
        raise ValueError(msg)

    dir_path = Path(data_dir)
    results: list[VerificationResult] = []
    generation_results: list[GenerationResult] = []
    for document_type_dir in dir_path.iterdir():
        if document_type_dir.name.startswith("."):
            continue
        if not document_type_dir.is_dir():
            continue
        for company_dir in document_type_dir.iterdir():
            if not company_dir.is_dir():
                continue
            for report_dir in company_dir.iterdir():
                if (
                    (document_type_dir.name not in document_types)
                    and (company_dir.name not in company_names)
                    and (report_dir.name not in report_ids)
                ):
                    print(
                        f"Skipping {document_type_dir.name}/{company_dir.name}/{report_dir.name}"
                    )
                    continue
                print(
                    f"Processing {document_type_dir.name}/{company_dir.name}/{report_dir.name}"
                )
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
                    generation_result = _generate(json_file, elements)
                    generation_results.append(generation_result)
                else:
                    with json_file.open("r") as f:
                        expected_contents = f.read()
                    dict_items = [e.to_dict() for e in elements]
                    actual_contents = json.dumps(
                        dict_items,
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

    if action == "generate":
        for result in generation_results:
            print(result)
    elif action == "verify":
        print_verification_result_table(results)
        if any(result.errors_found() for result in results):
            msg = "[ERROR] Verification failed."
            raise VerificationFailedError(msg)
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


def load_yaml_filter(file_path: Path) -> dict:
    with file_path.open("r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return {}
