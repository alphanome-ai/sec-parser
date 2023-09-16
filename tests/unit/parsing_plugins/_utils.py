from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag
from sec_parser.parsing_engine.html_parsers.root_tag_parser import RootTagParser
from sec_parser.semantic_elements.base_semantic_element import (
    BaseSemanticElement,
)
from typing import List, Union


class DummyElement(BaseSemanticElement):
    pass


class SpecialElement(BaseSemanticElement):
    pass


def create_element(tag) -> BaseSemanticElement:
    if tag.name == "special":
        return SpecialElement(tag)
    return DummyElement(tag)


def parse_elements(root_tags: List[HtmlTag]) -> List[BaseSemanticElement]:
    elements: List[BaseSemanticElement] = [create_element(tag) for tag in root_tags]
    for element in elements:
        if element.html_tag.name == "div":
            inner_tags = element.html_tag.get_children()
            element.inner_elements = parse_elements(inner_tags)

    return elements


def get_elements_from_html(html: str) -> List[BaseSemanticElement]:
    html_parser = RootTagParser()
    root_tags = html_parser.parse(html)
    elements = parse_elements(root_tags)
    return elements


def assert_elements(
    elements: List[BaseSemanticElement],
    expected_elements,
    path: Union[str, List[str]] = "root",
):
    assert len(elements) == len(
        expected_elements
    ), f"Expected {len(expected_elements)} elements, but got {len(elements)}. Path: {path}"

    for i, (ele, expected) in enumerate(zip(elements, expected_elements)):
        current_path = f"{path} -> Element {i} (type: {expected['type'].__name__}, tag: {expected['tag']})"

        assert isinstance(
            ele, expected["type"]
        ), f"Element at index {i} has type {type(ele).__name__}, but expected type {expected['type'].__name__}. Path: {current_path}"

        assert (
            ele.html_tag.name == expected["tag"]
        ), f"Element at index {i} has tag '{ele.html_tag.name}', but expected tag '{expected['tag']}'. Path: {current_path}"

        # Recursively check all descendants
        if "children" in expected:
            assert_elements(
                ele.inner_elements,
                expected["children"],
                path=current_path,
            )
