import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.table import Table

from sec_parser import Edgar10QParser
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

AVAILABLE_ACTIONS = ["generate", "verify"]


@dataclass
class VerificationResult:
    document_type: str
    company_name: str
    report_name: str
    missing_items: list[dict]
    unexpected_items: list[dict]


def _generate(json_file: Path, elements: list[AbstractSemanticElement]) -> None:
    with json_file.open("w") as f:
        items = [{"id": i, **e.to_dict()} for i, e in enumerate(elements)]
        json.dump(items, f, indent=4)


import json
from pathlib import Path
from typing import List, Tuple


def load_expected_items(json_file: Path) -> list:
    with json_file.open("r") as f:
        return json.load(f)


def compare_elements(elements: List, expected_items: List) -> Tuple[List, List]:
    unexpected_items, missing_items = [], []
    i, j = 0, 0
    while i < len(elements) and j < len(expected_items):
        el_dict = elements[i].to_dict()
        if el_dict == expected_items[j]:
            i += 1
            j += 1
        elif el_dict < expected_items[j]:
            unexpected_items.append(el_dict)
            i += 1
        else:
            missing_items.append(expected_items[j])
            j += 1
    unexpected_items.extend(el.to_dict() for el in elements[i:])
    missing_items.extend(expected_items[j:])
    return unexpected_items, missing_items


def print_report(result: VerificationResult) -> None:
    print(
        f"Comparison report for {result.document_type} - {result.company_name} - {result.report_name}:\n"
    )
    if result.unexpected_items or result.missing_items:
        if result.unexpected_items:
            print("Unexpected items:")
            for item in result.unexpected_items:
                print(f"ID: {item['id']}, Item: {item}")
        if result.missing_items:
            print("Missing items:")
            for item in result.missing_items:
                print(f"ID: {item['id']}, Item: {item}")
    else:
        print("No unexpected or missing items.")


def _verify(
    json_file: Path,
    elements: List,
    document_type: str,
    company_name: str,
    report_name: str,
) -> VerificationResult:
    expected_items = load_expected_items(json_file)
    unexpected_items, missing_items = compare_elements(elements, expected_items)
    return VerificationResult(
        document_type=document_type,
        company_name=company_name,
        report_name=report_name,
        missing_items=missing_items,
        unexpected_items=unexpected_items,
    )


def _print_verification_result_table(
    results: list[VerificationResult],
) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Document", style="dim", width=20)
    table.add_column("Company", style="dim", width=20)
    table.add_column("Report", style="dim", width=20)
    table.add_column("Missing", style="dim", width=10)
    table.add_column("Unexpected", style="dim", width=10)

    for result in results:
        table.add_row(
            result.document_type,
            result.company_name,
            result.report_name,
            str(len(result.missing_items)),
            str(len(result.unexpected_items)),
        )

    console.print(table)


def manage_snapshot(action: Literal["generate", "verify"], data_dir: str) -> None:
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

                elements = Edgar10QParser().parse(html_content)

                if action == "generate":
                    _generate(json_file, elements)
                else:
                    result = _verify(
                        json_file,
                        elements,
                        document_type_dir.name,
                        company_dir.name,
                        report_dir.name,
                    )
                    results.append(result)

    if action == "verify":
        _print_verification_result_table(results)
        failed = False
        for result in results:
            if len(result.missing_items) > 0 or len(result.unexpected_items) > 0:
                failed = True
                print_report(result)
        if failed:
            msg = "End-to-end check failed: There are missing or unexpected items."
            raise ValueError(msg)
