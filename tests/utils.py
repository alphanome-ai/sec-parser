from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from tests.types import Report

if TYPE_CHECKING:
    from collections.abc import Generator

DEFAULT_VALIDATION_DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent / "sec-parser-test-data"
)


def filter_valid_directories(starting_directory: Path) -> Generator[Path, None, None]:
    for current_directory in starting_directory.iterdir():
        if current_directory.name.startswith("."):
            continue
        if not current_directory.is_dir():
            continue
        yield current_directory


def traverse_repository_for_filings(
    root_directory: Path | None = None,
) -> Generator[Report, None, None]:
    root_directory = Path(root_directory or DEFAULT_VALIDATION_DATA_DIR)
    for document_type_directory in filter_valid_directories(root_directory):
        for company_directory in filter_valid_directories(document_type_directory):
            for individual_report_directory in filter_valid_directories(
                company_directory,
            ):
                yield Report(
                    document_type=document_type_directory.name,
                    company_name=company_directory.name,
                    accession_number=individual_report_directory.name,
                    path=individual_report_directory,
                )


def load_yaml_filter(file_path: Path) -> dict:
    with file_path.open("r") as stream:
        return yaml.safe_load(stream)


all_reports = None
if "pytest" in sys.modules:
    all_reports = list(traverse_repository_for_filings())
