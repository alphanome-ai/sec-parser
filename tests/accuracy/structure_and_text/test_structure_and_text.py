import json
import warnings
from collections import Counter
from pathlib import Path
from pprint import pprint
from typing import Callable

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
    request: pytest.FixtureRequest,
):
    # STEP: Skip the test if the report is not in the list of filings to test
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")

    # STEP: Parse the report
    elements = parse(report).semantic_elements

    # STEP: Compare the actual elements to the expected elements
    actual_json = [
        e.to_dict(
            include_previews=False,
            include_contents=True,
        )
        for e in elements
        if not isinstance(e, IGNORED_SEMANTIC_ELEMENT_TYPES)
    ]

    # STEP: Load (or save) the expected elements
    if not report.expected_structure_and_text.exists():
        if request.config.getoption("--create-missing-files"):
            with report.expected_structure_and_text.open("w") as f:
                json.dump(actual_json, f, sort_keys=True, indent=4, ensure_ascii=False)
            warnings.warn(
                f"Created {report.expected_structure_and_text.name}. Please manually review it and commit the file.",
                stacklevel=0,
            )
        else:
            pytest.fail(
                f"File {report.expected_structure_and_text.name} does not exist. Use --create-missing-files to create it.",
            )
    with report.expected_structure_and_text.open("r") as f:
        expected_elements_json = json.load(f)

    # STEP: Compare the actual elements to the expected elements
    index_of_last_matched_element = 0
    elements_not_found_in_actual = []
    for expected_element in expected_elements_json:
        for index_in_actual in range(
            index_of_last_matched_element,
            len(actual_json),
        ):
            if actual_json[index_in_actual] == expected_element:
                index_of_last_matched_element = index_in_actual + 1
                break
        else:
            elements_not_found_in_actual.append(expected_element)
    elements_not_expected_but_present = [
        actual_element
        for actual_element in actual_json
        if actual_element not in expected_elements_json
    ]

    # STEP: Report and save the results
    total_expected = len(expected_elements_json)
    total_missing = len(elements_not_found_in_actual)
    total_unexpected = len(elements_not_expected_but_present)
    total_actual = len(actual_json)

    true_positives = total_expected - total_missing
    false_positives = total_unexpected
    false_negatives = total_missing

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives)
        else None
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives)
        else None
    )
    if precision is not None and recall is not None:
        f1_score = (
            (2 * precision * recall) / (precision + recall)
            if (precision + recall)
            else None
        )
    else:
        f1_score = None

    missing_elements_by_type = Counter(
        element.get("cls_name") for element in elements_not_found_in_actual
    )
    unexpected_elements_by_type = Counter(
        element.get("cls_name") for element in elements_not_expected_but_present
    )

    summary_output_contents = {
        "metrics": {
            "total_expected": total_expected,
            "total_actual": total_actual,
            "total_missing": total_missing,
            "total_unexpected": total_unexpected,
            "precision": f"{precision:.2%}" if precision is not None else None,
            "recall": f"{recall:.2%}" if recall is not None else None,
            "f1_score": f"{f1_score:.2%}" if f1_score is not None else None,
            "missing_elements_by_type": dict(missing_elements_by_type),
            "unexpected_elements_by_type": dict(unexpected_elements_by_type),
        },
        "missing_elements": elements_not_found_in_actual,
        "unexpected_elements": elements_not_expected_but_present,
    }
    if request.config.getoption("--with-verbose-output"):
        if summary_output_contents["missing_elements"]:
            print(f"[{report.identifier}] Missing elements:")
            pprint(summary_output_contents["missing_elements"], width=200)
        if summary_output_contents["unexpected_elements"]:
            print(f"[{report.identifier}] Unexpected elements:")
            pprint(summary_output_contents["unexpected_elements"], width=200)
    if request.config.getoption("--with-saved-output"):
        with report.actual_structure_and_text.open("w") as f:
            json.dump(actual_json, f, sort_keys=True, indent=4, ensure_ascii=False)
        with report.actual_structure_and_text_summary.open("w") as f:
            json.dump(summary_output_contents, f, indent=4, ensure_ascii=False)
