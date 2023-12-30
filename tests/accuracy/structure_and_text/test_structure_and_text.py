import importlib.util
import json
import shutil
import warnings
from collections import Counter
from pathlib import Path
from pprint import pprint
from typing import Callable

import pytest

from sec_parser.semantic_elements.semantic_elements import IrrelevantElement
from tests.accuracy.structure_and_text.utils import elements_to_dicts
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
def test_structure_and_text(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
    request: pytest.FixtureRequest,
):
    # STEP: Skip the test if the report is not in the list of filings to test
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")

    # STEP: Parse the report and convert the elements to dicts
    elements = parse(report).semantic_elements
    actual_json = elements_to_dicts(elements)

    # STEP: Load (or save) the expected elements
    expected_elements_json = None
    if request.config.getoption("--update"):
        config_json_path = report.expected_structure_and_text_config_json
        was_manually_edited = False
        if config_json_path.exists():
            with config_json_path.open("r") as config_file:
                config_json = json.load(config_file)
                was_manually_edited = config_json["was_manually_edited"]

        if not was_manually_edited:
            existed_before = report.expected_structure_and_text.exists()
            with report.expected_structure_and_text.open("w") as f:
                json.dump(actual_json, f, sort_keys=True, indent=4, ensure_ascii=False)
            py_path = report.expected_structure_and_text_postprocessor
            if report.expected_structure_and_text_postprocessor.exists():
                # Set up input file for the postprocessor
                shutil.copy(
                    report.expected_structure_and_text,
                    report.expected_structure_and_text_postprocessor_input,
                )

                # Run python code
                spec = importlib.util.spec_from_file_location("postprocessor", py_path)
                assert spec is not None, f"Could not load {py_path} (spec is None))"
                assert (
                    spec.loader is not None
                ), f"Could not load {py_path} (spec.loader is None))"
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "main"):
                    module.main()
                else:
                    msg = f"The module {module.__name__} does not have a main function."
                    raise AttributeError(msg)
            if not existed_before:
                warnings.warn(
                    f"Created {report.expected_structure_and_text.name}. Please manually review it and commit the file.",
                    stacklevel=0,
                )
        elif not report.expected_structure_and_text.exists():
            with report.expected_structure_and_text.open("w") as f:
                json.dump(actual_json, f, sort_keys=True, indent=4, ensure_ascii=False)
            expected_elements_json = actual_json
    if expected_elements_json is None:
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

    # STEP: Sanity check
    if not elements_not_found_in_actual and not elements_not_expected_but_present:
        assert actual_json == expected_elements_json

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
            json.dump(
                summary_output_contents,
                f,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
            )
