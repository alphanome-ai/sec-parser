from typing import Union

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import ErrorWhileProcessingElement


def assert_elements(
    elements: list[AbstractSemanticElement],
    expected_elements,
    path: Union[str, list[str]] = "root",
):
    assert len(elements) == len(
        expected_elements,
    ), f"Expected {len(expected_elements)} elements, but got {len(elements)}. Path: {path}"

    for i, (ele, expected) in enumerate(zip(elements, expected_elements)):
        current_path = f"{path} -> Element {i} (type: {expected['type'].__name__}, tag: {expected['tag']})"

        if isinstance(ele, ErrorWhileProcessingElement):
            raise ele.error

        assert isinstance(
            ele,
            expected["type"],
        ), f"Element at index {i} has type {type(ele).__name__}, but expected type {expected['type'].__name__}. Path: {current_path}"

        assert (
            ele.html_tag.name == expected["tag"]
        ), f"Element at index {i} has tag '{ele.html_tag.name}', but expected tag '{expected['tag']}'. Path: {current_path}"

        if "fields" in expected:
            for field, expected_value in expected["fields"].items():
                assert (
                    getattr(ele, field) == expected_value
                ), f"Element at index {i} has field '{field}' with value '{getattr(ele, field)}', but expected value '{expected_value}'. Path: {current_path}"

        # Recursively check all descendants
        if "inner_elements" in expected:
            assert isinstance(ele, CompositeSemanticElement)
            assert_elements(
                list(ele.inner_elements),
                expected["inner_elements"],
                path=current_path,
            )
