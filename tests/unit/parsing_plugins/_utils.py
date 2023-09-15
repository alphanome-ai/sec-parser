import pytest

from sec_parser.parsing_engine.root_tag_parser import RootTagParser
from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import UndeterminedElement


def get_elements_from_html(html: str) -> list[AbstractSemanticElement]:
    html_parser = RootTagParser()
    root_tags = html_parser.parse(html)
    elements: list[AbstractSemanticElement] = [
        UndeterminedElement(tag) for tag in root_tags
    ]
    return elements
