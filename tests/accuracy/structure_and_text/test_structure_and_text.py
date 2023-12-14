import json
from pathlib import Path
from typing import Callable

import deepdiff
import pytest

from sec_parser.semantic_elements.semantic_elements import IrrelevantElement
from tests.types import ParsedDocumentComponents, Report
from tests.utils import all_reports, load_yaml_filter

CURRENT_DIR = Path(__file__).parent.resolve()
SHOW_SKIPPED = False
IGNORED_SEMANTIC_ELEMENT_TYPES = (IrrelevantElement,)

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
def test_structure_and_text(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    # Arrange
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")

    # Act
    elements = parse(report).semantic_elements

    # (Prepare) Assert
    actual_json = [
        e.to_dict(
            include_previews=False,
            include_contents=True,
        )
        for e in elements
        if not isinstance(e, IGNORED_SEMANTIC_ELEMENT_TYPES)
    ]

    if not report.expected_structure_and_text.exists():
        with report.expected_structure_and_text.open("w") as f:
            json.dump(actual_json, f, sort_keys=True, indent=4)
            pytest.fail(
                f"Expected structure and text file did not exist. "
                f"Created {report.expected_structure_and_text}. Please review and commit the file.",
            )

    # Assert
    with report.expected_structure_and_text.open("r") as f:
        expected_json = json.load(f)
    differences = deepdiff.DeepDiff(actual_json, expected_json)
    if differences:
        for k, v in differences.items():
            print(f"[{report.identifier}] {k}: {v}")
        pytest.fail(
            f"Actual structure and text did not match expected structure and text. "
            f"Please review {report.expected_structure_and_text}. ",
        )
