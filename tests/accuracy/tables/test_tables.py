import json
from pathlib import Path
from typing import Callable

import pytest

from tests.types import ParsedDocumentComponents, Report
from tests.utils import all_reports, load_yaml_filter

CURRENT_DIR = Path(__file__).parent.resolve()
SHOW_SKIPPED = False

expected_to_pass_accession_numbers = load_yaml_filter(
    CURRENT_DIR / "selected-filings.yaml",
)["accession_numbers"]


@pytest.mark.parametrize(
    "report",
    selected_filings := [
        k
        for k in all_reports
        if SHOW_SKIPPED or k.accession_number in expected_to_pass_accession_numbers
    ],
    ids=[k.identifier for k in selected_filings],
)
def test_tables(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    # Arrange
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")
    with report.expected_tables.open("r") as f:
        expected_tables_json = json.load(f)

    # Act
    elements = parse(report).semantic_elements

    # Assert
    assert len(elements) > 0
    assert expected_tables_json["hello"] == "world"
