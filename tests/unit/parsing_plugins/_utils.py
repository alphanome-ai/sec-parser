import pytest

from sec_parser.parsing_engine.html_parser import HtmlParser
from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import UnclaimedElement


def get_elements_from_html(html: str) -> list[AbstractSemanticElement]:
    html_parser = HtmlParser()
    root_tags = html_parser.get_root_tags(html)
    elements: list[AbstractSemanticElement] = [
        UnclaimedElement(tag) for tag in root_tags
    ]
    return elements
