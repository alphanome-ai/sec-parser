from collections.abc import Iterable

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement


def create_unclassified_elements(
    root_tags: Iterable[HtmlTag],
) -> list[AbstractSemanticElement]:
    return [NotYetClassifiedElement(tag) for tag in root_tags]
