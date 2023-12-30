from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from sec_parser.processing_engine.core import AbstractSemanticElementParser
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


@pytest.fixture(scope="session")
def check() -> (
    Callable[[AbstractSemanticElementParser, Path, pytest.FixtureRequest], None]
):
    def _check(
        parser: AbstractSemanticElementParser,
        html_path: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        # Arrange
        assert html_path.exists(), f"{html_path} does not exist"
        with html_path.open("r") as file:
            html_content = file.read()

        # Act
        elements = parser.parse(html_content)
        actual_elements_dicts = _elements_to_dicts(elements)

        # Pre-Assert: Load expected results or save actual results as expected
        json_file = html_path.with_suffix(".json")
        if (
            not json_file.exists() and request.config.getoption("--create-missing")
        ) or request.config.getoption("--update"):
            with json_file.open("w") as f:
                json.dump(
                    actual_elements_dicts,
                    f,
                    indent=4,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            pytest.skip(f"{json_file} was missing and has been created.")
        elif not json_file.exists():
            pytest.fail(f"{json_file} is missing. Use --create-missing to create it.")

        # Assert
        with json_file.open("r") as f:
            expected_elements_dicts = json.load(f)
        missing, unexpected = _compare_elements(
            expected_elements_dicts,
            actual_elements_dicts,
        )
        error_messages = []
        if unexpected:
            e = json.dumps(
                missing,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            error_messages.append(
                f"Unexpected elements in {html_path}:\n{e}",
            )
        if missing:
            e = json.dumps(
                missing,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )
            error_messages.append(
                f"Missing elements in {html_path}:\n{e}",
            )
        if error_messages:
            pytest.fail("\n\n".join(error_messages))

    return _check


def _elements_to_dicts(elements: list[AbstractSemanticElement]) -> list[dict]:
    return [
        e.to_dict(
            include_previews=False,
            include_contents=True,
        )
        for e in elements
    ]


def _compare_elements(
    expected_elements_dicts: list[dict],
    actual_elements_dicts: list[dict],
) -> tuple[list[dict], list[dict]]:
    # STEP: Compare the actual elements to the expected elements
    index_of_last_matched_element = 0
    elements_not_found_in_actual = []
    for expected_element in expected_elements_dicts:
        for index_in_actual in range(
            index_of_last_matched_element,
            len(actual_elements_dicts),
        ):
            if actual_elements_dicts[index_in_actual] == expected_element:
                index_of_last_matched_element = index_in_actual + 1
                break
        else:
            elements_not_found_in_actual.append(expected_element)
    elements_not_expected_but_present = [
        actual_element
        for actual_element in actual_elements_dicts
        if actual_element not in expected_elements_dicts
    ]

    # STEP: Sanity check
    if not elements_not_found_in_actual and not elements_not_expected_but_present:
        assert actual_elements_dicts == expected_elements_dicts

    return elements_not_found_in_actual, elements_not_expected_but_present
